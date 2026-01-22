from django.core.mail import EmailMessage
from django.conf import settings


def enviar_correo_registro(inscrito):
    if not inscrito.correo_electronico:
        return

    subject = "Confirmación de registro – MIEPI"

    body = f"""
Hola {inscrito.nombre},

Tu registro ha sido realizado correctamente.
Debe presentar el qr recibido en este correo para validar 
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

    # Adjuntar QR si existe
    if hasattr(inscrito, "qr_image") and inscrito.qr_image:
        try:
            email.attach_file(inscrito.qr_image.path)
        except Exception as e:
            print("No se pudo adjuntar el QR:", e)

    email.send(fail_silently=False)
