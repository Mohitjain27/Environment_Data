import os

FILES = {
    "run.py": """\
import argparse
import sys
from document.docx_redactor import redact_document
from evaluation.evaluator import evaluate
from config import DATA_DIR, OUTPUT_DIR
import os
import unittest

def main():
    parser = argparse.ArgumentParser(description="PII Redactor")
    parser.add_argument('--input', type=str, help='Input DOCX file')
    parser.add_argument('--output', type=str, help='Output DOCX file')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation against ground truth')
    parser.add_argument('--test', action='store_true', help='Run test suite')

    args = parser.parse_args()

    if args.test:
        print("Running tests...")
        suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
        unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0)

    if args.evaluate:
        print("Running evaluation...")
        evaluate()
        sys.exit(0)

    if args.input and args.output:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        print(f"Redacting {args.input} to {args.output}...")
        redact_document(args.input, args.output)
        print("Redaction complete.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
""",
    "config.py": """\
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

PII_TYPES = [
    'PERSON', 'EMAIL', 'PHONE', 'ORG', 'ADDRESS', 
    'SSN', 'CREDIT_CARD', 'DOB', 'IP_ADDRESS', 'PIN_CODE', 'CIN'
]

NON_PII_TERMS = [
    'Red Herring Prospectus', 'Book Running Lead Managers',
    'Companies Act', 'Equity Shares', 'Risk Factors', 'Offer Price',
    'Offer Amount', 'Page', 'Section', 'SEBI', 'SEBI ICDR Regulations'
]
""",
    "detectors/regex_detector.py": """\
import re

REGEX_PATTERNS = {
    'EMAIL': r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b',
    'PHONE': r'(?:\\+91[-.\\s]?)?(?:0?\\d{2,4}[-.\\s]?)?\\d{6,8}\\b|\\b\\d{10}\\b',
    'SSN': r'\\b\\d{3}-\\d{2}-\\d{4}\\b',
    'CREDIT_CARD': r'\\b(?:\\d[ -]*?){13,16}\\b',
    'IP_ADDRESS': r'\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b',
    'PIN_CODE': r'\\b\\d{6}\\b',
    'CIN': r'\\b[L|U]\\d{5}[A-Z]{2}\\d{4}[A-Z]{3}\\d{6}\\b'
}

class RegexDetector:
    def detect(self, text):
        entities = []
        for pii_type, pattern in REGEX_PATTERNS.items():
            for match in re.finditer(pattern, text):
                val = match.group()
                # Exclude simple numbers matching CC/Phone erroneously
                if pii_type == 'PHONE' and len(val) < 8:
                    continue
                entities.append({
                    'type': pii_type,
                    'start': match.start(),
                    'end': match.end(),
                    'value': val,
                    'confidence': 1.0
                })
        return entities
""",
    "detectors/ner_detector.py": """\
import spacy
from config import NON_PII_TERMS

class NERDetector:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
    
    def detect(self, text):
        entities = []
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE']:
                val = ent.text.strip()
                if any(term.lower() in val.lower() for term in NON_PII_TERMS):
                    continue
                # Specific check for dates as DOB
                t_type = ent.label_
                if ent.label_ == 'GPE':
                    t_type = 'ADDRESS'
                entities.append({
                    'type': t_type,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'value': val,
                    'confidence': 0.8
                })
        return entities
""",
    "detectors/address_detector.py": """\
import re

class AddressDetector:
    def detect(self, text):
        entities = []
        # Keywords for addresses
        addr_pattern = r'\\b(?:Registered Office|Corporate Office|Village|Taluka|District|Pune|Maharashtra|India)\\b.*?(?:\\d{6}|India)'
        for match in re.finditer(addr_pattern, text, re.IGNORECASE):
            entities.append({
                'type': 'ADDRESS',
                'start': match.start(),
                'end': match.end(),
                'value': match.group(),
                'confidence': 0.9
            })
        return entities
""",
    "detectors/company_detector.py": """\
import re
from config import NON_PII_TERMS

class CompanyDetector:
    def detect(self, text):
        entities = []
        pattern = r'\\b[A-Z][a-zA-Z0-9]*\\s+(?:[A-Z][a-zA-Z0-9]*\\s+)*(?:Limited|Ltd\\.?|Private Limited|Pvt\\.? Ltd\\.?|LLP)\\b'
        for match in re.finditer(pattern, text):
            val = match.group()
            if any(term.lower() in val.lower() for term in NON_PII_TERMS):
                continue
            entities.append({
                'type': 'ORG',
                'start': match.start(),
                'end': match.end(),
                'value': val,
                'confidence': 0.95
            })
        return entities
""",
    "detectors/pii_detector.py": """\
from .regex_detector import RegexDetector
from .ner_detector import NERDetector
from .address_detector import AddressDetector
from .company_detector import CompanyDetector
import re

class PIIDetector:
    def __init__(self):
        self.detectors = [
            RegexDetector(),
            NERDetector(),
            AddressDetector(),
            CompanyDetector()
        ]
        
    def detect(self, text):
        all_entities = []
        for detector in self.detectors:
            all_entities.extend(detector.detect(text))
            
        # DOB specific rule
        dob_pattern = r'Date of Birth:\\s*([A-Za-z]+\\s+\\d{1,2},\\s+\\d{4})'
        for match in re.finditer(dob_pattern, text, re.IGNORECASE):
            all_entities.append({
                'type': 'DOB',
                'start': match.start(1),
                'end': match.end(1),
                'value': match.group(1),
                'confidence': 1.0
            })
            
        return self._resolve_overlaps(all_entities)
        
    def _resolve_overlaps(self, entities):
        # Sort by start descending, then end descending to prioritize longer matches
        entities.sort(key=lambda x: (x['start'], -x['end']))
        resolved = []
        for ent in entities:
            overlap = False
            for r in resolved:
                # Check overlap
                if not (ent['end'] <= r['start'] or ent['start'] >= r['end']):
                    overlap = True
                    break
            if not overlap:
                resolved.append(ent)
        return resolved
""",
    "replacers/faker_replacer.py": """\
from faker import Faker
import random

class FakerReplacer:
    def __init__(self):
        self.faker = Faker('en_IN')
        Faker.seed(42)
        random.seed(42)
        
    def get_fake(self, pii_type):
        if pii_type == 'PERSON':
            return self.faker.name()
        elif pii_type == 'EMAIL':
            return self.faker.email()
        elif pii_type == 'PHONE':
            return self.faker.phone_number()
        elif pii_type == 'ORG':
            return self.faker.company()
        elif pii_type == 'ADDRESS':
            return self.faker.address().replace('\\n', ', ')
        elif pii_type == 'SSN':
            return self.faker.ssn()
        elif pii_type == 'CREDIT_CARD':
            return self.faker.credit_card_number()
        elif pii_type == 'DOB':
            return self.faker.date_of_birth().strftime('%B %d, %Y')
        elif pii_type == 'IP_ADDRESS':
            return self.faker.ipv4()
        elif pii_type == 'PIN_CODE':
            return self.faker.postcode()
        elif pii_type == 'CIN':
            return 'L12345MH2000PLC123456'
        else:
            return '[REDACTED]'
""",
    "replacers/replacement_manager.py": """\
import json
import os
from .faker_replacer import FakerReplacer
from config import OUTPUT_DIR

class ReplacementManager:
    def __init__(self):
        self.mapping = {}
        self.replacer = FakerReplacer()
        self.map_file = os.path.join(OUTPUT_DIR, 'replacement_map.json')
        
    def get_replacement(self, original_value, pii_type):
        key = f"{pii_type}:{original_value}"
        if key not in self.mapping:
            self.mapping[key] = self.replacer.get_fake(pii_type)
        return self.mapping[key]
        
    def save_mapping(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        with open(self.map_file, 'w') as f:
            json.dump(self.mapping, f, indent=2)
""",
    "document/docx_redactor.py": """\
from docx import Document
from detectors.pii_detector import PIIDetector
from replacers.replacement_manager import ReplacementManager

def process_text_elements(elements, detector, rep_manager):
    for element in elements:
        text = element.text
        if not text.strip():
            continue
            
        entities = detector.detect(text)
        if not entities:
            continue
            
        # Replace right-to-left
        entities.sort(key=lambda x: x['start'], reverse=True)
        new_text = text
        for ent in entities:
            fake_val = rep_manager.get_replacement(ent['value'], ent['type'])
            new_text = new_text[:ent['start']] + fake_val + new_text[ent['end']:]
            
        element.text = new_text

def redact_document(input_path, output_path):
    doc = Document(input_path)
    detector = PIIDetector()
    rep_manager = ReplacementManager()
    
    # Process paragraphs
    for p in doc.paragraphs:
        process_text_elements([p], detector, rep_manager)
        
    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    process_text_elements([p], detector, rep_manager)
                    
    # Save
    doc.save(output_path)
    rep_manager.save_mapping()
""",
    "evaluation/evaluator.py": """\
import json
import os
from detectors.pii_detector import PIIDetector
from config import DATA_DIR, OUTPUT_DIR
from .metrics import calculate_metrics

def evaluate():
    detector = PIIDetector()
    gt_file = os.path.join(DATA_DIR, 'pii_ground_truth.json')
    
    if not os.path.exists(gt_file):
        print(f"Ground truth file {gt_file} not found. Cannot evaluate.")
        return
        
    with open(gt_file, 'r') as f:
        ground_truth = json.load(f)
        
    tp, fp, fn = 0, 0, 0
    type_stats = {}
    
    for item in ground_truth:
        text = item['text']
        true_entities = item['entities']
        pred_entities = detector.detect(text)
        
        # Simple match logic
        true_set = {(e['start'], e['end'], e['type']) for e in true_entities}
        pred_set = {(e['start'], e['end'], e['type']) for e in pred_entities}
        
        tp += len(true_set & pred_set)
        fp += len(pred_set - true_set)
        fn += len(true_set - pred_set)
        
        # Record stats per type
        for e in true_set:
            t = e[2]
            if t not in type_stats:
                type_stats[t] = {'tp': 0, 'fp': 0, 'fn': 0}
            if e in pred_set:
                type_stats[t]['tp'] += 1
            else:
                type_stats[t]['fn'] += 1
                
        for e in pred_set - true_set:
            t = e[2]
            if t not in type_stats:
                type_stats[t] = {'tp': 0, 'fp': 0, 'fn': 0}
            type_stats[t]['fp'] += 1
            
    # Calculate overall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    report = {
        'overall': {
            'tp': tp, 'fp': fp, 'fn': fn,
            'precision': precision, 'recall': recall, 'f1': f1
        },
        'per_type': type_stats
    }
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(os.path.join(OUTPUT_DIR, 'evaluation_report.json'), 'w') as f:
        json.dump(report, f, indent=2)
        
    # Markdown
    with open(os.path.join(OUTPUT_DIR, 'evaluation_report.md'), 'w') as f:
        f.write("# Evaluation Report\\n\\n")
        f.write("## Overall Metrics\\n")
        f.write(f"- **Precision:** {precision:.2f}\\n")
        f.write(f"- **Recall:** {recall:.2f}\\n")
        f.write(f"- **F1 Score:** {f1:.2f}\\n\\n")
        f.write("## Per-Type Metrics\\n")
        f.write("| Type | TP | FP | FN | Precision | Recall | F1 |\\n")
        f.write("|---|---|---|---|---|---|---|\\n")
        for t, stats in type_stats.items():
            p = stats['tp'] / (stats['tp'] + stats['fp']) if (stats['tp'] + stats['fp']) > 0 else 0
            r = stats['tp'] / (stats['tp'] + stats['fn']) if (stats['tp'] + stats['fn']) > 0 else 0
            f1_t = 2 * p * r / (p + r) if (p + r) > 0 else 0
            f.write(f"| {t} | {stats['tp']} | {stats['fp']} | {stats['fn']} | {p:.2f} | {r:.2f} | {f1_t:.2f} |\\n")
            
    print("Evaluation completed. Reports generated in output/.")
""",
    "evaluation/metrics.py": """\
def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1
""",
    "data/pii_ground_truth.json": """\
[
  {
    "text": "11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune – 410 501 Maharashtra, India",
    "entities": [
      {
        "type": "ADDRESS",
        "start": 0,
        "end": 92,
        "value": "11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune – 410 501 Maharashtra, India"
      }
    ]
  },
  {
    "text": "Sarthak Malvadkar Company Secretary and Compliance Officer",
    "entities": [
      {
        "type": "PERSON",
        "start": 0,
        "end": 17,
        "value": "Sarthak Malvadkar"
      }
    ]
  },
  {
    "text": "Email: cs.connect@kshinternational.com Telephone: +91 20 4505 3237",
    "entities": [
      {
        "type": "EMAIL",
        "start": 7,
        "end": 38,
        "value": "cs.connect@kshinternational.com"
      },
      {
        "type": "PHONE",
        "start": 50,
        "end": 66,
        "value": "+91 20 4505 3237"
      }
    ]
  },
  {
    "text": "Rashi Patil: John Doe, rashhi.patil@gmail.com, john.doe@example.com",
    "entities": [
      {
        "type": "PERSON",
        "start": 0,
        "end": 11,
        "value": "Rashi Patil"
      },
      {
        "type": "PERSON",
        "start": 13,
        "end": 21,
        "value": "John Doe"
      },
      {
        "type": "EMAIL",
        "start": 23,
        "end": 45,
        "value": "rashhi.patil@gmail.com"
      },
      {
        "type": "EMAIL",
        "start": 47,
        "end": 67,
        "value": "john.doe@example.com"
      }
    ]
  },
  {
    "text": "Rohan Dey: rohan.dey@gmail.com, peter.parker@example.com, +91 9876543210, +91 1234567645",
    "entities": [
      {
        "type": "PERSON",
        "start": 0,
        "end": 9,
        "value": "Rohan Dey"
      },
      {
        "type": "EMAIL",
        "start": 11,
        "end": 30,
        "value": "rohan.dey@gmail.com"
      },
      {
        "type": "EMAIL",
        "start": 32,
        "end": 56,
        "value": "peter.parker@example.com"
      },
      {
        "type": "PHONE",
        "start": 58,
        "end": 72,
        "value": "+91 9876543210"
      },
      {
        "type": "PHONE",
        "start": 74,
        "end": 88,
        "value": "+91 1234567645"
      }
    ]
  },
  {
    "text": "Date of Birth: December 10, 1998.",
    "entities": [
      {
        "type": "DOB",
        "start": 15,
        "end": 32,
        "value": "December 10, 1998"
      }
    ]
  },
  {
    "text": "CORPORATE IDENTITY NUMBER: U28129PN1979PLC141032",
    "entities": [
      {
        "type": "CIN",
        "start": 27,
        "end": 48,
        "value": "U28129PN1979PLC141032"
      }
    ]
  }
]
""",
    "tests/test_redaction.py": """\
import unittest
from detectors.pii_detector import PIIDetector

class TestRedaction(unittest.TestCase):
    def setUp(self):
        self.detector = PIIDetector()
        
    def test_email(self):
        text = "Contact me at test@example.com"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]['type'], 'EMAIL')
        
    def test_phone(self):
        text = "Call me at +91 9876543210"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]['type'], 'PHONE')
        
    def test_financial_not_flagged(self):
        text = "Offer Price: ₹7,100 million"
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 0)

if __name__ == '__main__':
    unittest.main()
""",
    "README.md": """\
# PII Redaction Tool

A robust tool to redact Personally Identifiable Information (PII) from DOCX files using a hybrid approach of Regular Expressions, Named Entity Recognition (NER), and contextual rules.

## Requirements
- Python 3
- `python-docx`, `regex`, `spacy`, `Faker`, `pandas`
- SpaCy model: `en_core_web_sm`

## Approach
The tool uses a hybrid detection pipeline:
1. **Regex**: High confidence for structured PII like Emails, Phones, CINs.
2. **NER (spaCy)**: Detects unstructured PII like Person names and Organizations.
3. **Rules/Context**: Resolves ambiguities (e.g., Dates as DOB only if preceded by 'Date of Birth').

Replacements are generated deterministically using `Faker`, ensuring formatting survives using `python-docx` in-place paragraph updates.

## Evaluation
Run `python run.py --evaluate` to compare detection against ground truth.

## Usage
Redact a document:
`python run.py --input Red_Herring_Prospectus.docx --output output/redacted_prospectus.docx`

Run tests:
`python run.py --test`
"""
}

for filepath, content in FILES.items():
    dirname = os.path.dirname(filepath)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {filepath}")
