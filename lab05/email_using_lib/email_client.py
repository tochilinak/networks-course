import smtplib
from email.message import EmailMessage
from getpass import getpass
import sys


if __name__ == "__main__":

    receiver = sys.argv[1]
    filename = sys.argv[2]
    login = "tochilina.2002@yandex.ru"
    password = getpass()

    with open(filename, 'r') as file:
        content = file.read()

    msg = EmailMessage()
    subtype = "html" if filename[-5:] == ".html" else "plain"
    print(subtype)
    msg.set_content(content, subtype=subtype)
    msg['Subject'] = "Message from Lab05"
    msg['From'] = login
    msg['To'] = receiver

    s = smtplib.SMTP_SSL(host='smtp.yandex.ru', port=465)
    s.login(login, password)
    s.send_message(msg)
    s.quit()
