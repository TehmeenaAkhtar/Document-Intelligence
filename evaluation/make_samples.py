import json
from pathlib import Path

import pymupdf

SAMPLES_DIR = Path("evaluation/samples")

# Each sample = the text on the PDF + the CORRECT answers (the answer key).
SAMPLES = [
    {
        "file": "01_standard.pdf",
        "text": "Invoice Number: INV-001\nCustomer: Ahmed\nInvoice Date: 19 October 2026\nTotal Amount: PKR 5,000",
        "expected": {"invoice_number": "INV-001", "customer": "Ahmed",
                     "invoice_date": "19 October 2026", "total_amount": "PKR 5,000"},
    },
    {
        "file": "02_other_labels.pdf",
        "text": "Invoice No: INV-002\nBill To: Fatima Traders\nDate: 2 September 2026\nGrand Total: PKR 18,400",
        "expected": {"invoice_number": "INV-002", "customer": "Fatima Traders",
                     "invoice_date": "2 September 2026", "total_amount": "PKR 18,400"},
    },
    {
        "file": "03_hash_label.pdf",
        "text": "Invoice #: 2026-0099\nCustomer Name: Hassan & Sons\nDate: 01/10/2026\nTotal: $1,250.00",
        "expected": {"invoice_number": "2026-0099", "customer": "Hassan & Sons",
                     "invoice_date": "01/10/2026", "total_amount": "$1,250.00"},
    },
    {
        "file": "04_capital_letters.pdf",
        "text": "INVOICE NO: INV-004\nBILL TO: Zara Enterprises\nDATE: 7 Oct 2026\nGRAND TOTAL: Rs. 12,500.00",
        "expected": {"invoice_number": "INV-004", "customer": "Zara Enterprises",
                     "invoice_date": "7 Oct 2026", "total_amount": "Rs. 12,500.00"},
    },
    {
        "file": "05_missing_customer.pdf",
        "text": "Invoice Number: INV-005\nInvoice Date: 5 August 2026\nTotal Amount: PKR 3,200",
        "expected": {"invoice_number": "INV-005", "customer": None,
                     "invoice_date": "5 August 2026", "total_amount": "PKR 3,200"},
    },
    {
        "file": "06_with_tax_lines.pdf",
        "text": "Invoice Number: INV-006\nCustomer: Usman Electronics\nInvoice Date: 12 July 2026\nSubtotal: PKR 4,000\nTax: PKR 500\nTotal: PKR 4,500",
        "expected": {"invoice_number": "INV-006", "customer": "Usman Electronics",
                     "invoice_date": "12 July 2026", "total_amount": "PKR 4,500"},
    },
    # ---- The next three are HARD on purpose. We expect misses here. ----
    {
        "file": "07_value_on_next_line.pdf",
        "text": "Invoice Number\nINV-007\nCustomer\nSara Khan\nInvoice Date\n3 September 2026\nTotal Amount\nPKR 12,500",
        "expected": {"invoice_number": "INV-007", "customer": "Sara Khan",
                     "invoice_date": "3 September 2026", "total_amount": "PKR 12,500"},
    },
    {
        "file": "08_no_colon.pdf",
        "text": "Invoice Number   INV-008\nCustomer   Bilal Traders\nInvoice Date   14 June 2026\nTotal Amount   PKR 9,900",
        "expected": {"invoice_number": "INV-008", "customer": "Bilal Traders",
                     "invoice_date": "14 June 2026", "total_amount": "PKR 9,900"},
    },
    {
        "file": "09_extra_text_after_value.pdf",
        "text": "Invoice Number: INV-009\nCustomer: Noor Pharmacy\nInvoice Date: 20 May 2026\nTotal Amount: PKR 8,000 (due in 30 days)",
        "expected": {"invoice_number": "INV-009", "customer": "Noor Pharmacy",
                     "invoice_date": "20 May 2026", "total_amount": "PKR 8,000"},
    },
    {
        "file": "10_unknown_labels.pdf",
        "text": "INVOICE\nInv. Ref: BX-2210\nBilled To: Imran Hardware Store\nIssued: 8 Oct 2026\nAmount Due: PKR 21,750",
        "expected": {"invoice_number": "BX-2210", "customer": "Imran Hardware Store",
                     "invoice_date": "8 Oct 2026", "total_amount": "PKR 21,750"},
    },
    {
        "file": "11_written_as_sentence.pdf",
        "text": "Dear Ahmed, thank you for your order.\nInvoice INV-011 dated 4 June 2026 comes to PKR 6,300 in total.",
        "expected": {"invoice_number": "INV-011", "customer": "Ahmed",
                     "invoice_date": "4 June 2026", "total_amount": "PKR 6,300"},
    },
    {
        "file": "12_table_then_details.pdf",
        "text": "Description  Qty  Amount\nPaper  5  PKR 2,000\nInk  2  PKR 1,000\n\nInvoice: INV-012\nTo: Mehreen Salon\nDate: 15 Sept 2026\nPayable: PKR 3,000",
        "expected": {"invoice_number": "INV-012", "customer": "Mehreen Salon",
                     "invoice_date": "15 Sept 2026", "total_amount": "PKR 3,000"},
    },
    {
        "file": "13_client_label.pdf",
        "text": "Invoice Number: INV-013\nClient: Kareem Motors\nInvoice Date: 11 Aug 2026\nNet Payable: PKR 11,700",
        "expected": {"invoice_number": "INV-013", "customer": "Kareem Motors",
                     "invoice_date": "11 Aug 2026", "total_amount": "PKR 11,700"},
    },
    {
        "file": "14_all_on_one_line.pdf",
        "text": "Invoice INV-014 | Customer: Rana Foods | Date: 2 Jan 2026 | Total: PKR 4,200",
        "expected": {"invoice_number": "INV-014", "customer": "Rana Foods",
                     "invoice_date": "2 Jan 2026", "total_amount": "PKR 4,200"},
    },
]


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    answer_key = {}

    for sample in SAMPLES:
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((72, 100), sample["text"], fontsize=12)
        doc.save(SAMPLES_DIR / sample["file"])
        doc.close()
        answer_key[sample["file"]] = sample["expected"]

    (SAMPLES_DIR / "expected.json").write_text(
        json.dumps(answer_key, indent=2), encoding="utf-8"
    )
    print(f"Made {len(SAMPLES)} sample PDFs in {SAMPLES_DIR}")


if __name__ == "__main__":
    main()