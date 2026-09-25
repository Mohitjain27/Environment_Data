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
