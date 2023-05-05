import requests
from bs4 import BeautifulSoup
import html2text


def generate():
    email_addres = requests.get(
        "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1").json()[0]
    return email_addres


def refresh(username, domain):
    response = requests.get(
        f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}").json()

    # if email have message
    if response:

        files = []
        # last message id
        email_id = response[0]["id"]
        # get message info
        response_msg = requests.get(
            f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={email_id}").json()
        email_from = response_msg["from"]
        email_subject = response_msg["subject"]
        email_date = response_msg["date"]
        email_html = response_msg["htmlBody"]
        email_text = html2text.html2text(email_html)
        attachments = response_msg["attachments"]

        # if message have attachments
        if attachments:
            files = [attachment["filename"] for attachment in attachments]
        return [email_id, email_from, email_subject, email_date, email_text, files]

    return "No Messages Were Received.."


def download(username, domain, email_id, file):
    attachment_url = f"https://www.1secmail.com/api/v1/?action=download&login={username}&domain={domain}&id={email_id}&file={file}"
    return attachment_url
