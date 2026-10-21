
from fastapi import FastAPI, File, HTTPException, UploadFile
from app.services.field_extractor import extract_invoice_fields, check_review
import pymupdf

app = FastAPI(
    title="Document Intelligence API",
    description="A document processing and review system.",
    version="0.2.0",
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/documents/extract")
async def extract_pdf(file: UploadFile = File(...)):
    # 1. Check the file extension.
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    # 2. Read enough data to enforce the size limit.
    content = await file.read(MAX_FILE_SIZE + 1)
    await file.close()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB limit.",
        )

    # 3. Check the PDF signature.
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF.",
        )

    # 4. Extract text from each page.
    try:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            if document.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported yet.",
                )

            pages = [
                {
                    "page_number": page_number,
                    "text": page.get_text(),
                }
                for page_number, page in enumerate(document, start=1)
            ]

        full_text = "\n".join(page["text"] for page in pages)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please check the file.",
        )

    # 5. Extract invoice fields.
    fields = extract_invoice_fields(full_text)

    # 6. Check whether the extracted fields need human review.
    review = check_review(fields)

    # 7. Flag PDFs that contain no extractable text.
    if not full_text.strip():
        review["notes"] = "No text found. This may be a scanned PDF."

    # 8. Return the extraction results.
    return {
        "filename": file.filename,
        "page_count": len(pages),
        "pages": pages,
        "extracted_fields": fields,
        "review": review,
    }
