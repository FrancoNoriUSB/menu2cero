from django.core.mail.message import EmailMessage
from django.db.models import Count
from django.db.models import Q

#Set de funciones varias a utilizar en el frontend

#Funcion para los correos que se envian en Contact Us
def contact_email(request, form):

    emailF = form
    emails = []

    #Informacion del usuario
    name = emailF.cleaned_data['nombre']
    emails.append("info@menu2cero.com")
    telephone = emailF.cleaned_data['telefono']

    #Verificacion de si posee telefono
    if telephone == '':
        telephone = 'No posee telefono de contacto.'

    #Mensaje a enviar
    message = 'Correo de contacto del usuario: '+ str(name) +'. Con correo: ' + str(emailF.cleaned_data['correo']) +'<br>'
    message += 'Mensaje: '+ str(emailF.cleaned_data['mensaje']) + '<br>'
    message += 'Telefono de contacto: '+ str(telephone)

    email = EmailMessage()
    email.subject = '[Menu2Cero] Correo contacto'
    email.body = message
    email.from_email = 'Usuario Menu2Cero <'+str(emailF.cleaned_data['correo'])+'>'
    email.to = emails
    email.content_subtype = "html"
    enviado=email.send()
    return True
