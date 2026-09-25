import re

REGEX_PATTERNS = {
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'PHONE': r'(?:\+91[-.\s]?)?(?:0?\d{2,4}[-.\s]?)?\d{6,8}\b|\b\d{10}\b',
    'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
    'CREDIT_CARD': r'\b(?:\d[ -]*?){13,16}\b',
    'IP_ADDRESS': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'PIN_CODE': r'\b\d{6}\b',
    'CIN': r'\b[L|U]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b'
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
