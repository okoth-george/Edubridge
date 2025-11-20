from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list, html_message=None):
    """
    Send an email to one or more recipients.

    Args:
        subject (str): Email subject
        message (str): Plain text message
        recipient_list (list): List of email addresses
        html_message (str, optional): HTML version of the message
    """
    if not isinstance(recipient_list, list):
        recipient_list = [recipient_list]

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False
    )
