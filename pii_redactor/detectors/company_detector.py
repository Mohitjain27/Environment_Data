import re
from config import NON_PII_TERMS

class CompanyDetector:
    def detect(self, text):
        entities = []
        pattern = r'\b[A-Z][a-zA-Z0-9]*\s+(?:[A-Z][a-zA-Z0-9]*\s+)*(?:Limited|Ltd\.?|Private Limited|Pvt\.? Ltd\.?|LLP)\b'
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
