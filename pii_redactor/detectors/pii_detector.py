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
        dob_pattern = r'Date of Birth:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})'
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
