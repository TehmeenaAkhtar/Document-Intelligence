import json
from pathlib import Path

import pymupdf

from app.services.field_extractor import extract_invoice_fields

SAMPLES_DIR = Path("evaluation/samples")
FIELDS = ["invoice_number", "customer", "invoice_date", "total_amount"]


def same(found, expected):
    """True if the answer matches. Ignores capital letters and extra spaces."""
    if found is None or expected is None:
        return found == expected
    return found.strip().lower() == expected.strip().lower()


def main():
    answer_key = json.loads((SAMPLES_DIR / "expected.json").read_text(encoding="utf-8"))
    correct = {field: 0 for field in FIELDS}

    for filename, expected in answer_key.items():
        with pymupdf.open(SAMPLES_DIR / filename) as doc:
            text = "\n".join(page.get_text() for page in doc)

        found = extract_invoice_fields(text)

        for field in FIELDS:
            if same(found[field], expected[field]):
                correct[field] += 1
            else:
                print(f"MISS  {filename} | {field}: expected {expected[field]!r}, got {found[field]!r}")

    total_docs = len(answer_key)
    print("\n--- ACCURACY ---")
    for field in FIELDS:
        print(f"{field:15} {correct[field]}/{total_docs}  ({correct[field] / total_docs:.0%})")

    all_correct = sum(correct.values())
    all_checks = total_docs * len(FIELDS)
    print(f"{'OVERALL':15} {all_correct}/{all_checks}  ({all_correct / all_checks:.0%})")


if __name__ == "__main__":
    main()