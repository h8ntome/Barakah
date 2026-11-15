"""Explicit SMTP reset delivery; no tokens or recipient addresses in logs."""
import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode
from .config import get_settings

logger = logging.getLogger(__name__)


def send_reset_email(email, token):
    config = get_settings()
    message = EmailMessage()
    message['From'] = config.smtp_sender
    message['To'] = email
    message['Subject'] = 'Reset your Barakah password'
    separator = '&' if '?' in config.reset_url else '?'
    message.set_content('Use this one-time link within 30 minutes: ' + config.reset_url + separator + urlencode({'token': token}) + '\nIf you did not request a reset, ignore this email.')
    try:
        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            if config.smtp_username:
                smtp.login(config.smtp_username, config.smtp_password or '')
            smtp.send_message(message)
        return True
    except (smtplib.SMTPException, OSError):
        # Same public response for registered/unregistered recipients, even on delivery failure.
        logger.error('Password reset SMTP delivery failed; check provider configuration')
        return False
