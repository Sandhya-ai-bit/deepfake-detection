"""
report_generator.py
-------------------
PDF report module for the Deepfake Image Detection System.

Main function:
    generate_report(prediction, confidence, image_path=None, model_name=None)

It builds a one-page PDF report and saves it in the `reports/` folder
(next to this file). It returns the path of the saved PDF.

Requires: reportlab, Pillow   (pip install -r requirements.txt)
"""

import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape  # makes text safe for ReportLab Paragraphs

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ----------------------------------------------------------------------
# Settings (change these if you want)
# ----------------------------------------------------------------------
# Always save next to this file, no matter where the program is started from.
REPORTS_DIR = Path(__file__).resolve().parent / "reports"

MAX_IMAGE_WIDTH = 8 * cm    # the image is shrunk to fit inside this box
MAX_IMAGE_HEIGHT = 8 * cm

DISCLAIMER_TEXT = (
    "This report was produced by an automated machine-learning model. "
    "Predictions can be incorrect and should not be treated as proof that "
    "an image is real or manipulated. Please use this result only as a "
    "guide and verify important cases by other means."
)

DARK_BLUE = colors.HexColor("#1F3A5F")
GREEN = colors.HexColor("#1E8449")
RED = colors.HexColor("#C0392B")
LIGHT_GREY = colors.HexColor("#F2F4F7")
MID_GREY = colors.HexColor("#C8CDD3")


# ----------------------------------------------------------------------
# Small helper functions
# ----------------------------------------------------------------------
def _clean_prediction(prediction):
    """Return 'Real' or 'Fake'. Raise ValueError for anything else."""
    if not isinstance(prediction, str):
        raise ValueError("prediction must be the text 'Real' or 'Fake'.")

    label = prediction.strip().capitalize()
    if label not in ("Real", "Fake"):
        raise ValueError(f"prediction must be 'Real' or 'Fake', got '{prediction}'.")
    return label


def _clean_confidence(confidence):
    """Return confidence as a float between 0 and 1. Raise ValueError if not."""
    if isinstance(confidence, bool):  # True/False would silently become 1/0
        raise ValueError("confidence must be a number between 0 and 1.")

    try:
        # float() also accepts numpy numbers such as numpy.float32
        value = float(confidence)
    except (TypeError, ValueError):
        raise ValueError(f"confidence must be a number between 0 and 1, got '{confidence}'.")

    # This check also rejects NaN (nan is never between 0 and 1).
    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"confidence must be between 0 and 1 (e.g. 0.93 for 93%), got {value}."
        )
    return value


def _load_image(image_path):
    """
    Try to load the uploaded image for the PDF.

    Returns (image_flowable, message).
    If the image cannot be used, image_flowable is None and message explains why.
    This function never crashes the report.
    """
    if image_path is None or str(image_path).strip() == "":
        return None, "No image was provided."

    try:
        path = Path(image_path)
    except TypeError:
        return None, "Image path is invalid."

    if not path.is_file():
        return None, "Image file was not found."

    try:
        # Open with Pillow, convert to RGB and keep a JPEG copy in memory.
        # This lets us support PNG, JPG, WEBP, BMP, etc. (even images with transparency).
        with PILImage.open(path) as img:
            img = img.convert("RGB")
            width, height = img.size
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
    except Exception:
        # Corrupted file, not an image, too big, etc.
        return None, "The file could not be read as an image."

    # Shrink the image to fit the box, keeping the original proportions.
    scale = min(MAX_IMAGE_WIDTH / width, MAX_IMAGE_HEIGHT / height, 1.0)
    pdf_image = Image(buffer, width=width * scale, height=height * scale)
    return pdf_image, ""


def _footer(report_id):
    """Return a function that draws the footer on each page."""

    def draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.2 * cm, f"Deepfake Image Detection System  |  {report_id}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        canvas.restoreState()

    return draw_footer


# ----------------------------------------------------------------------
# Main function
# ----------------------------------------------------------------------
def generate_report(prediction, confidence, image_path=None, model_name=None):
    """
    Create a PDF report and save it in the `reports/` folder.

    Parameters
    ----------
    prediction : str
        "Real" or "Fake" (not case-sensitive).
    confidence : float
        Model confidence as a number from 0 to 1 (0.93 means 93%).
    image_path : str or Path, optional
        Path to the uploaded image. If it is missing or invalid, the report
        is still created with a short note instead of the image.
    model_name : str, optional
        Name of the model that made the prediction.

    Returns
    -------
    str
        Path of the saved PDF file.

    Raises
    ------
    ValueError
        If `prediction` or `confidence` is invalid.
    """
    # 1. Check the inputs (bad prediction/confidence -> ValueError)
    label = _clean_prediction(prediction)
    score = _clean_confidence(confidence)

    # 2. Report ID, date/time and file name
    now = datetime.now()
    report_id = f"DF-{now:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:4].upper()}"
    date_text = now.strftime("%d %B %Y, %H:%M:%S")

    model_text = str(model_name).strip() if model_name else ""
    if not model_text:
        model_text = "Not specified"

    REPORTS_DIR.mkdir(exist_ok=True)
    output_path = REPORTS_DIR / f"report_{report_id}.pdf"

    # 3. Text styles
    base = getSampleStyleSheet()["Normal"]
    title_style = ParagraphStyle("Title", parent=base, fontName="Helvetica-Bold",
                                 fontSize=22, leading=28, textColor=DARK_BLUE, alignment=1, spaceAfter=4)
    subtitle_style = ParagraphStyle("Subtitle", parent=base, fontSize=11,
                                    leading=14, textColor=colors.grey, alignment=1)
    heading_style = ParagraphStyle("Heading", parent=base, fontName="Helvetica-Bold",
                                   fontSize=13, leading=16, textColor=DARK_BLUE, spaceBefore=14, spaceAfter=6)
    label_style = ParagraphStyle("Label", parent=base, fontName="Helvetica-Bold", fontSize=10)
    value_style = ParagraphStyle("Value", parent=base, fontSize=10)
    note_style = ParagraphStyle("Note", parent=base, fontSize=10,
                                textColor=colors.grey, alignment=1)
    disclaimer_style = ParagraphStyle("Disclaimer", parent=base, fontSize=9,
                                      textColor=colors.HexColor("#555555"), leading=13)

    result_color = GREEN if label == "Real" else RED
    result_style = ParagraphStyle("Result", parent=base, fontName="Helvetica-Bold",
                                  fontSize=18, leading=22, textColor=result_color)

    story = []

    # 4. Title
    story.append(Paragraph("Deepfake Image Detection Report", title_style))
    story.append(Paragraph("Automated analysis result", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=DARK_BLUE))

    # 5. Report details table
    story.append(Paragraph("Report Details", heading_style))
    details = Table(
        [
            [Paragraph("Report ID", label_style), Paragraph(report_id, value_style)],
            [Paragraph("Date and Time", label_style), Paragraph(date_text, value_style)],
            [Paragraph("Model", label_style), Paragraph(escape(model_text), value_style)],
        ],
        colWidths=[4 * cm, 13 * cm],
    )
    details.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREY),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(details)

    # 6. Uploaded image (or a note if it is not available)
    story.append(Paragraph("Uploaded Image", heading_style))
    pdf_image, image_message = _load_image(image_path)
    if pdf_image is not None:
        image_box = Table([[pdf_image]], hAlign="CENTER")
        image_box.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, MID_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(image_box)
    else:
        story.append(Paragraph(f"Image not available: {escape(image_message)}", note_style))

    # 7. Prediction and confidence
    story.append(Paragraph("Detection Result", heading_style))
    result = Table(
        [
            [Paragraph("Prediction", label_style), Paragraph(label.upper(), result_style)],
            [Paragraph("Confidence Score", label_style), Paragraph(f"{score * 100:.2f}%", result_style)],
        ],
        colWidths=[4 * cm, 13 * cm],
    )
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREY),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(result)

    # 8. Disclaimer
    story.append(Spacer(1, 16))
    disclaimer = Table(
        [[Paragraph(f"<b>Disclaimer:</b> {DISCLAIMER_TEXT}", disclaimer_style)]],
        colWidths=[17 * cm],
    )
    disclaimer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 0.5, MID_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(disclaimer)

    # 9. Build the PDF file
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Deepfake Image Detection Report",
        author="Deepfake Image Detection System",
    )
    footer = _footer(report_id)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    return str(output_path)


# Quick manual test:  python report_generator.py
if __name__ == "__main__":
    path = generate_report("Fake", 0.9345, image_path=None, model_name="Demo Model")
    print("Report saved to:", path)
