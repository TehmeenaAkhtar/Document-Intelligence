import re

MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
ID_PATTERN = re.compile(r"\b[A-Z]{2,5}-\d{2,}(?:-\d+)?\b")
DATE_PATTERN = re.compile(rf"\b\d{{1,2}}\s+(?:{MONTHS})[a-z]*\.?\s+\d{{4}}\b", re.I)
AMOUNT_PATTERN = re.compile(r"(?:PKR|Rs\.?|USD|\$)\s?\d[\d,]*(?:\.\d+)?", re.I)


def find_field(text: str, labels: list[str]) -> str | None:
    """Find a value written after one of the supplied labels."""

    # Pass 1: the label starts the line.
    for label in labels:
        pattern = rf"(?im)^[ \t]*{re.escape(label)}[ \t]*(?::|[ \t]{{2,}}|\n)[ \t]*(.+?)[ \t]*$"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    # Pass 2: the label is inside a line, e.g. "A | Customer: Rana | B".
    for label in labels:
        pattern = rf"(?i)\b{re.escape(label)}[ \t]*:[ \t]*([^|\n]+)"
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None


def clean_amount(value: str | None) -> str | None:
    """Remove a trailing note like '(due in 30 days)' from an amount."""

    if value is None:
        return None
    return re.sub(r"\s*\(.*\)\s*$", "", value).strip()


def amount_value(amount: str) -> float:
    number = re.search(r"\d[\d,]*(?:\.\d+)?", amount).group()
    return float(number.replace(",", ""))


def extract_invoice_fields(text: str) -> dict:
    """Extract common invoice fields from text."""

    invoice_number = find_field(
        text, ["Invoice Number", "Invoice No", "Invoice #", "Inv. Ref", "Inv No"]
    )
    if invoice_number is None:
        match = ID_PATTERN.search(text)
        invoice_number = match.group() if match else None

    customer = find_field(
        text, ["Customer", "Customer Name", "Bill To", "Billed To", "Client", "To"]
    )
    if customer is None:
        match = re.search(r"\bDear\s+([A-Z][\w&.\- ]*?)\s*,", text)
        customer = match.group(1) if match else None

    invoice_date = find_field(text, ["Invoice Date", "Issued", "Issue Date", "Date"])
    if invoice_date is None:
        match = DATE_PATTERN.search(text)
        invoice_date = match.group() if match else None

    total_amount = clean_amount(
        find_field(
            text,
            ["Total Amount", "Grand Total", "Net Payable", "Amount Due", "Payable", "Total"],
        )
    )
    if total_amount is None:
        amounts = AMOUNT_PATTERN.findall(text)
        total_amount = max(amounts, key=amount_value) if amounts else None

    return {
        "invoice_number": invoice_number,
        "customer": customer,
        "invoice_date": invoice_date,
        "total_amount": total_amount,
    }

REQUIRED_FIELDS = ["invoice_number", "customer", "invoice_date", "total_amount"]


def check_review(fields: dict) -> dict:
    """Say whether a human should double-check this document."""

    missing = [name for name in REQUIRED_FIELDS if not fields.get(name)]

    return {
        "needs_review": len(missing) > 0,
        "missing_fields": missing,
    }
