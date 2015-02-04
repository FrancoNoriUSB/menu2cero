from django.core.mail.message import EmailMessage
from django.db.models import Count
from django.db.models import Q
from django.core.mail import send_mail

#Set de funciones varias a utilizar en el frontend

#Funcion para los correos que se envian en Contact Us
def contact_email(request, form):

    emailF = form
    emails = []

    #Informacion del usuario
    name = emailF.cleaned_data['nombre']
    telephone = emailF.cleaned_data['telefono']
    emails.append("info@menu2cero.com")

    #Mensaje a enviar
    message = 'Correo de contacto del usuario: '+ str(name) +'. Con correo: ' + str(emailF.cleaned_data['correo']) +'<br>'
    message += 'Mensaje: '+ str(emailF.cleaned_data['mensaje']) + '<br>'
    message += 'Telefono de contacto: '+ str(telephone)
    send_mail('[Menu2Cero] Correo contacto', message, 'Usuario Menu2Cero <'+str(emailF.cleaned_data['correo'])+'>', emails, fail_silently=False)
    return True