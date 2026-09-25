import re

class AddressDetector:
    def detect(self, text):
        entities = []
        # Keywords for addresses
        addr_pattern = r'\b(?:Registered Office|Corporate Office|Village|Taluka|District|Pune|Maharashtra|India)\b.*?(?:\d{6}|India)'
        for match in re.finditer(addr_pattern, text, re.IGNORECASE):
            entities.append({
                'type': 'ADDRESS',
                'start': match.start(),
                'end': match.end(),
                'value': match.group(),
                'confidence': 0.9
            })
        return entities
