# Document Intelligence API

A Python API that extracts text and key invoice fields from PDF documents. It is built with FastAPI and supports testing through an interactive API interface.

## Run with Docker

### 1. Build the Docker image

```bash
docker build -t document-intelligence .
```

### 2. Start the API

```bash
docker run --name document-intelligence-api -p 8000:8000 document-intelligence
```

### 3. Open the API documentation

Visit:

http://127.0.0.1:8000/docs

Use the interactive documentation to test the available endpoints and upload a PDF to the document extraction endpoint.

## Example

For a sample invoice containing an invoice number, customer, date, and total amount, the API returns extracted text and structured fields.

```json
{
  "invoice_number": "INV-103",
  "customer": "Hira Malik",
  "invoice_date": "17 October 2026",
  "total_amount": "PKR 6,750"
}
```

The API also reports whether any required fields are missing and whether the document needs review.


## Current Status

- PDF text extraction tested successfully.
- Invoice field extraction tested successfully on a sample invoice.
- Docker image built and API run successfully.
- Evaluation scripts and sample documents included.


---

**Note:** This project is a work in progress. Extraction results may vary depending on the PDF layout and document quality.
