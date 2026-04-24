"""Lógica de divisão do PDF em quadrantes (uma etiqueta por página)."""

from io import BytesIO

import fitz
from PIL import Image, ImageStat


def process_pdf(pdf_data):
    pdf_data.seek(0)
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    try:
        output = BytesIO()
        with fitz.open() as pdf_output:
            for page in pdf_document:
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                for part in divide_into_quadrants(img):
                    if not is_image_blank(part):
                        pdf_output.insert_pdf(fitz.open("pdf", image_to_pdf_bytes(part)))
            if pdf_output.page_count > 0:
                pdf_output.save(output)
                output.seek(0)
                return output
            raise ValueError("Todas as páginas foram consideradas em branco.")
    finally:
        pdf_document.close()


def divide_into_quadrants(image):
    w, h = image.size
    return [
        image.crop((0, 0, w // 2, h // 2)),
        image.crop((0, h // 2, w // 2, h)),
        image.crop((w // 2, 0, w, h // 2)),
        image.crop((w // 2, h // 2, w, h)),
    ]


def is_image_blank(image):
    stat = ImageStat.Stat(image)
    return sum(stat.mean) / len(stat.mean) > 250


def image_to_pdf_bytes(image):
    pdf_bytes = BytesIO()
    image.save(pdf_bytes, format="PDF")
    return pdf_bytes.getvalue()
