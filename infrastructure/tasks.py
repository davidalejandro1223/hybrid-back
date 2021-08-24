from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from users.models import User


def send_email(data):
    context = {'email': data["admin"].email, 'sender': data["sender"], "reported_date": data["reported_date"]}
    from_email = settings.EMAIL_HOST_USER

    content = render_to_string(
        str(settings.BASE_DIR) + '/templates/emails/users/'+data["template_file"],
        context
    )
    
    email = EmailMultiAlternatives(
        data["subject"],
        context,
        from_email,
        [data["admin"].email])
    email.attach_alternative(content, 'text/html')
    email.send()
