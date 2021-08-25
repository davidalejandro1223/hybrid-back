# Django
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Models
from users.models import User

# Utilities
import jwt
from datetime import timedelta

def notify_positive_covid(user):
    subject = 'Reporte positivo de caso de covid en la oficina'
    from_email = 'Hybrid <noreply@hybrid.com>'
    
    content = render_to_string(
        'emails/users/covid_workers_notification.html',
        {'user': user}
    )
    
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.content_subtype = 'html'
    msg.attach_alternative(content, "text/html")
    msg.send()