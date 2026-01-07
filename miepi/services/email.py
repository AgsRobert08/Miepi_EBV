from django.core.mail import EmailMessage
from django.conf import settings
import requests

def enviar_correo_registro(inscrito):
    if not inscrito.correo_electronico:
        return

    subject = "Confirmación de registro – MIEPI"

    body = f"""
Hola {inscrito.nombre},

Tu registro ha sido realizado correctamente.
Debe presentar el QR recibido en este correo para validar 
su asistencia.
Dios te bendiga.
"""

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[inscrito.correo_electronico],
        reply_to=[settings.EMAIL_HOST_USER],
    )

    # Adjuntar QR desde Cloudinary
    if hasattr(inscrito, "qr_image") and inscrito.qr_image:
        try:
            # Obtener la URL de Cloudinary
            qr_url = inscrito.qr_image.url
            
            # Descargar el QR desde Cloudinary
            response = requests.get(qr_url)
            
            if response.status_code == 200:
                # Adjuntar el contenido del archivo
                filename = f"qr_{inscrito.id}.png"
                email.attach(filename, response.content, 'image/png')
            else:
                print(f"No se pudo descargar el QR: HTTP {response.status_code}")
                
        except Exception as e:
            print("No se pudo adjuntar el QR:", e)

    email.send(fail_silently=False)