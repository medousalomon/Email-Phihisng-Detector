import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import letter


def generate_pdf_report(

    email_text,
    prediction,
    confidence,
    explanation,
    output_path="exports/report.pdf"

):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    doc = SimpleDocTemplate(

        output_path,

        pagesize=letter

    )

    styles = getSampleStyleSheet()

    elements = []

    # -------------------------
    # TITLE
    # -------------------------

    title = Paragraph(

        "Phishing Email Investigation Report",

        styles["Title"]

    )

    elements.append(title)

    elements.append(Spacer(1, 20))

    # -------------------------
    # PREDICTION
    # -------------------------

    prediction_text = Paragraph(

        f"<b>Prediction:</b> {prediction}",

        styles["BodyText"]

    )

    confidence_text = Paragraph(

        f"<b>Confidence:</b> {confidence:.4f}",

        styles["BodyText"]

    )

    elements.append(prediction_text)

    elements.append(confidence_text)

    elements.append(Spacer(1, 20))

    # -------------------------
    # EMAIL CONTENT
    # -------------------------

    email_paragraph = Paragraph(

        f"<b>Email Content:</b><br/>{email_text}",

        styles["BodyText"]

    )

    elements.append(email_paragraph)

    elements.append(Spacer(1, 20))

    # -------------------------
    # EXPLANATION
    # -------------------------

    explanation_title = Paragraph(

        "<b>LIME Explanation:</b>",

        styles["Heading2"]

    )

    elements.append(explanation_title)

    for word, weight in explanation:

        line = Paragraph(

            f"{word}: {weight:.4f}",

            styles["BodyText"]

        )

        elements.append(line)

    # -------------------------
    # BUILD PDF
    # -------------------------

    doc.build(elements)

    return output_path