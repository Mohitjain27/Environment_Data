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
