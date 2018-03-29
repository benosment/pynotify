import sys
import logging
import logging.config
import os
import smtplib
import subprocess
from email.generator import Generator
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO

import settings


def send_email(subject, body):
    gmail_user = os.environ.get('MAIL_USERNAME')
    gmail_password = os.environ.get('MAIL_PASSWORD')

    if not gmail_user or not gmail_password:
        raise EnvironmentError('invalid user or password for sending mail')

    logging.debug(gmail_user)
    logging.debug(gmail_password)

    from_address = ['pynotify', gmail_user]
    recipient = [gmail_user, gmail_user]

    # 'alternative' MIME type - HTML and plaintext bundled in one email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '%s' % Header(subject, 'utf-8')
    msg['From'] = '"%s" <%s>' % (Header(from_address[0], 'utf-8'),
                                 from_address[1])
    msg['To'] = '"%s" <%s>' % (Header(recipient[0], 'utf-8'), recipient[1])

    html_body = MIMEText(body, 'html', 'UTF-8')
    msg.attach(html_body)
    str_io = StringIO()
    gen = Generator(str_io, False)
    gen.flatten(msg)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, gmail_user, str_io.getvalue())
        server.close()
    except smtplib.SMTPException as e:
        logging.error('Failed to send mail')
        logging.exception(e)


def run_command(command):
    try:
        logging.debug('command: %s' % ' '.join(command))
        output = subprocess.check_output(command)
    except Exception as e:
        logging.error("%s call failed" % ' '.join(command))
        logging.exception(e)
        output = str(e)
    return output


if __name__ == '__main__':
    # init logger
    logging.config.dictConfig(settings.LOGGING)
    command = sys.argv[1:]
    # TODO - start timer
    output = run_command(command)
    # TODO - end timer
    # TODO - add timer output to command output
    send_email('pynotify - "%s" finished' % ' '.join(command), output)