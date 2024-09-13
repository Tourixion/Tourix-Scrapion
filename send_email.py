import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        if os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attachment_path)}",
            )
            msg.attach(part)
            logger.info(f"Attached file: {attachment_path}")
        else:
            logger.error(f"Attachment file not found: {attachment_path}")
            body += f"\n\nNote: The attachment file ({attachment_path}) was not found."
            msg.attach(MIMEText(body, 'plain'))

    text = msg.as_string()

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_email, text)
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    subject = "LocalClarity - Stavros - Review Download Link"
    body = "Please find attached the latest JSON file from LocalClarity."
    to_email = os.environ['TO_EMAIL']
    from_email = os.environ['FROM_EMAIL']
    smtp_server = os.environ['SMTP_SERVER']
    smtp_port = int(os.environ['SMTP_PORT'])
    smtp_username = os.environ['SMTP_USERNAME']
    smtp_password = os.environ['SMTP_PASSWORD']
    
    download_dir = os.path.join(os.getcwd(), "downloads")
    attachment_path = os.path.join(download_dir, "localclarity_data.json")

    # List contents of the download directory
    logger.info(f"Contents of {download_dir}:")
    if os.path.exists(download_dir):
        for filename in os.listdir(download_dir):
            logger.info(f"- {filename}")
    else:
        logger.error(f"Download directory does not exist: {download_dir}")

    send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path)

    send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path)
