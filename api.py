import fitz
from PIL import Image, ImageStat
from io import BytesIO
import json


def handler(event, context):
    body = json.loads(event["body"])
    file_content = body.get("file_content")

    if not file_content:
        return {"statusCode": 400, "body": "Arquivo PDF não enviado."}

    try:
        pdf_data = BytesIO(bytes(file_content, encoding="utf-8"))
        output_file = process_pdf(pdf_data)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/pdf"},
            "body": output_file.getvalue().decode("latin1"),
            "isBase64Encoded": True,
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}


def process_pdf(pdf_data):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
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
        else:
            raise ValueError("Todas as páginas foram consideradas em branco.")


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
