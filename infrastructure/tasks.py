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

def send_cancel_email_by_fase(user):
    subject = 'Cancelacion de reservas por cambio de fase'
    from_email = 'Hybrid <noreply@hybrid.com>'
    
    content = render_to_string(
        'emails/users/cancel_booking.html',
        {'user': user}
    )
    
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.content_subtype = 'html'
    msg.attach_alternative(content, "text/html")
    msg.send()