# PII Redaction Tool

## Approach
Our redaction tool uses a hybrid approach to maximize both precision and recall. 
1. **Regex Patterns**: Used for highly structured PII such as Emails, Indian/International Phone Numbers, SSNs, Credit Cards, and CINs.
2. **NER Model (spaCy `en_core_web_sm`)**: Extracts unstructured entities like `PERSON` and `ORG`.
3. **Contextual Rules**: We apply contextual keywords to detect Indian Addresses and specific logic to differentiate normal dates from Dates of Birth (DOB). We also employ an exclusion list to prevent redacting generic financial and legal terms (e.g., "Red Herring Prospectus", "Companies Act").

We process the `.docx` document natively using the `python-docx` library, modifying text directly within the paragraph runs. This ensures that the original formatting, bolding, italics, and table structures are perfectly preserved. Once detected, PII is mapped to realistic fake data using the `Faker` library, and a deterministic dictionary ensures that repeated PII gets the exact same replacement throughout the document.

## Tradeoffs and False Positives/Negatives
- **Tradeoffs:** We chose a hybrid approach over a pure Deep Learning approach to ensure the tool is fast, interpretable, and doesn't require GPUs to run. However, rule-based systems require manual tuning.
- **False Positives:** The NER model occasionally flags generic capitalized jargon as `ORG` or `PERSON`. While we added a strict exclusion list, novel financial jargon may still be erroneously redacted.
- **False Negatives:** Addresses in India are highly unstructured. Our `AddressDetector` requires specific anchor keywords ("Village", "Taluka", etc.). If an address omits these, it may be missed. Also, PII split across multiple formatting runs in a `.docx` file (e.g. half of an email is bolded) can occasionally evade regex detection.

## Extending to a New PII Type
The code is designed to be highly modular. To add a new PII type (e.g., "PASSPORT_NUMBER"):
1. Open `config.py` and add `'PASSPORT_NUMBER'` to the `PII_TYPES` list.
2. Open `detectors/regex_detector.py` and add the passport regex pattern to the `REGEX_PATTERNS` dictionary.
3. Open `replacers/faker_replacer.py` and add an `elif pii_type == 'PASSPORT_NUMBER': return self.faker.passport_number()` block to generate the fake data.
