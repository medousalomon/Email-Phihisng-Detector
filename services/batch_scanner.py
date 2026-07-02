from services.predictor import predict_email


def batch_scan_emails(email_list):

    results = []

    for email in email_list:

        label, confidence = predict_email(
            email
        )

        results.append({

            "email": email,

            "prediction": label,

            "confidence": confidence

        })

    return results