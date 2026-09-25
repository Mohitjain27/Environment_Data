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
