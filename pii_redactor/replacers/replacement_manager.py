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
