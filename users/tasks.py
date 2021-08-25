# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse_lazy

# Models
from users.models import User

# Utilities
import jwt
from datetime import timedelta

def gen_verification_token(user):
    """Crea JWT usado por el usuario para verificar su cuenta"""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user': user.email,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def send_confirmation_email(user):
    """Envia correo de verificacion al usuario en cuestion"""
    print('enviando..')
    
    verification_token = gen_verification_token(user)
    subject = 'Bienvenido {}! Verifica tu cuenta'.format(user.first_name)
    from_email = 'Hybrid by talana <noreply@hybrid.com>'
    verification_url = f"?code={verification_token}" #reverse_lazy('users:verify_account', kwargs={'token':verification_token})
    
    content = render_to_string(
        'emails/users/account_verification.html',
        {'verification_url': verification_url, 'user': user, 'token':verification_token}
    )
    
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.content_subtype = 'html'
    msg.attach_alternative(content, "text/html")
    msg.send()