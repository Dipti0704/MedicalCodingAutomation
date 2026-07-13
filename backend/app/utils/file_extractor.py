import io
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}


class TesseractNotAvailable(Exception):
    pass


def _ocr_image(image: Image.Image) -> str:
    try:
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError as exc:
        raise TesseractNotAvailable(
            "OCR engine (Tesseract) is not installed on this machine. "
            "Install Tesseract-OCR to extract text from scanned documents or images."
        ) from exc


def _extract_pdf(file_bytes: bytes) -> dict:
    text_parts = []
    ocr_used = False

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text().strip()

            if page_text:
                text_parts.append(page_text)
                continue

            # No embedded text layer - page is likely a scanned image, fall back to OCR.
            pixmap = page.get_pixmap(dpi=300)
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            text_parts.append(_ocr_image(image))
            ocr_used = True

    return {"text": "\n\n".join(part for part in text_parts if part), "ocr_used": ocr_used}


def _extract_image(file_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(file_bytes))
    return {"text": _ocr_image(image), "ocr_used": True}


def extract_text(filename: str, file_bytes: bytes) -> dict:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return _extract_pdf(file_bytes)

    if extension in IMAGE_EXTENSIONS:
        return _extract_image(file_bytes)

    if extension == ".txt":
        return {"text": file_bytes.decode("utf-8", errors="ignore"), "ocr_used": False}

    raise ValueError(f"Unsupported file type: {extension}")
