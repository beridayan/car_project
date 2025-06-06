import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_list_email(sender_email: str, receiver_email: str, app_password: str, subject: str, item_list: list):
    """
    Sends a list of items as an email.

    Args:
        sender_email (str): Your Gmail address.
        receiver_email (str): Recipient's email address (can be the same as sender).
        app_password (str): Gmail App Password (not your Gmail password).
        subject (str): Subject line of the email.
        item_list (list): The list of items to send.
    """
    # Email body (as plain text)
    body = "Here is the list:\n\n" + "\n".join(str(item) for item in item_list)

    # Set up the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)



send_list_email(
    sender_email="beridayan2008@gmail.com",
    receiver_email="beridayan2008@gmail.com",
    app_password="qapuzlpqfeiueerl",  # No spaces!
    subject="Filtered Cars from Yad2",
    item_list=[2,3,4,])
