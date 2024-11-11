#Importing libraries
from django.conf import settings
from django.core.mail import send_mail

#This function sends the activation email
def send_account_activation_email(email, email_token):
    subject = "Verify your account"
    email_from = settings.DEFAULT_FROM_EMAIL
    message = f'Verify your email using this url: http://127.0.0.1:8000/accounts/activate/{email_token}'    
    send_mail(subject, message, email_from, [email])