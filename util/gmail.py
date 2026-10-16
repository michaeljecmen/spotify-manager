import os
import smtplib, ssl
import traceback
from datetime import date

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from util.debug import debug_print
from util.config import read_config, get_absolute_spotify_repo_path

def send_gmail(sender, sender_pw, receiver, subject, content):
    """
    Sends a simple text-based email over GMail.
    :param sender: The gmail address of the sending account
    :param sender_pw: The password associated with the sender gmail account
    :param receiver: The gmail address you'd like to send the email to
    :param content: The actual text content of the email
    """
    port = 465  # for ssl

    # necessary for secure ssl context
    context = ssl.create_default_context()

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject

    # specify utf-8, definitely could have some weird characters
    message.attach(MIMEText(content, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, sender_pw)
        server.sendmail(sender, receiver, message.as_string())

def debug_print_and_email_message(config, subject, content):
    if content != "":
        send_gmail(config["SENDER_EMAIL"], config["SENDER_PASSWORD"], config["ROLLING_SONGS"]["RECEIVER_EMAIL"], subject, content)
        debug_print(content)


def email_error(job_name):
    """
    Call from inside an except block. Prints the traceback for the cron log
    and emails it, at most once a day per job so an hourly job can't flood the inbox.
    """
    error = traceback.format_exc()
    print(error)

    stamp_path = get_absolute_spotify_repo_path() + ".last-error-email-" + job_name
    today = str(date.today())
    if os.path.exists(stamp_path):
        with open(stamp_path, "r") as stamp:
            if stamp.read().strip() == today:
                return

    try:
        config = read_config()
        send_gmail(config["SENDER_EMAIL"], config["SENDER_PASSWORD"], config["ROLLING_SONGS"]["RECEIVER_EMAIL"], "error in " + job_name, error)
        with open(stamp_path, "w") as stamp:
            stamp.write(today)
    except Exception:
        print("could not email the error:")
        traceback.print_exc()
