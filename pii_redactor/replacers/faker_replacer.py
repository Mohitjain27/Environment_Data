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
            return self.faker.address().replace('\n', ', ')
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
