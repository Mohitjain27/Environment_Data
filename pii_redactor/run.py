import argparse
import sys
from document.docx_redactor import redact_document
from evaluation.evaluator import evaluate
from config import DATA_DIR, OUTPUT_DIR
import os
import unittest

def main():
    parser = argparse.ArgumentParser(description="PII Redactor")
    parser.add_argument('--input', type=str, help='Input DOCX file')
    parser.add_argument('--output', type=str, help='Output DOCX file')
    parser.add_argument('--evaluate', action='store_true', help='Run evaluation against ground truth')
    parser.add_argument('--test', action='store_true', help='Run test suite')

    args = parser.parse_args()

    if args.test:
        print("Running tests...")
        suite = unittest.TestLoader().discover('tests', pattern='test_*.py')
        unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0)

    if args.evaluate:
        print("Running evaluation...")
        evaluate()
        sys.exit(0)

    if args.input and args.output:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        print(f"Redacting {args.input} to {args.output}...")
        redact_document(args.input, args.output)
        print("Redaction complete.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
