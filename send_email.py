import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        msg.attach(part)

    text = msg.as_string()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, text)

if __name__ == "__main__":
    subject = "LocalClarity - Stavros - Review Download Link"
    body = "Please find attached the latest JSON file from LocalClarity."
    to_email = os.environ['TO_EMAIL']
    from_email = os.environ['FROM_EMAIL']
    smtp_server = os.environ['SMTP_SERVER']
    smtp_port = int(os.environ['SMTP_PORT'])
    smtp_username = os.environ['SMTP_USERNAME']
    smtp_password = os.environ['SMTP_PASSWORD']
    attachment_path = "/github/workspace/downloads/localclarity_data.json"

    send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path)
