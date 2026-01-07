from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.formats import date_format

from django.db.models import Q
from django.views.generic import UpdateView

from django.core.mail import EmailMessage
from django.conf import settings
from django.core.files import File

from io import BytesIO
import qrcode

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.contrib.messages.views import SuccessMessageMixin

from .models import Inscrito, Asistencia
from .forms import *
from miepi.services.email import enviar_correo_registro


# vista del login
def login_view(request):
    # Si el usuario ya está autenticado, redirigir al dashboard
    #if request.user.is_authenticated:
     #   return redirect('miepi:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('miepi:dashboard') 
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'miepi/login.html')


@login_required(login_url='miepi:login')
def dashboard(request):  
    return render(request, 'miepi/dashboard.html')

# Inscribir a los usuarios
class InscritoCreateView(LoginRequiredMixin, View):
    template_name = 'miepi/dashboard.html'

    def get(self, request):
        form = InscritoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = InscritoForm(request.POST)

        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return render(request, self.template_name, {'form': form})

        inscrito = form.save()

        # QR
        qr = qrcode.make(str(inscrito.codigo))
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)

        inscrito.qr_image.save(
            f"{inscrito.codigo}.png",
            File(buffer),
            save=True
        )

        # EMAIL (aislado)
        try:
            enviar_correo_registro(inscrito)
        except Exception as e:
            print("Error enviando correo:", e)
            messages.warning(
                request,
                "Registro creado, pero el correo no pudo enviarse."
           )

        messages.success(
            request,
            "Usuario registrado correctamente. Registro finalizado."
        )

        return redirect('miepi:inscritos_list')

def get_inscritos_filtrados(request):
    genero = request.GET.get('genero', '').strip()

    qs = Inscrito.objects.all().order_by('nombre')

    if genero:
        qs = qs.filter(genero__iexact=genero)

    return qs.order_by('nombre')

class InscritosListView(LoginRequiredMixin, View):
    template_name = "miepi/inscripciones/inscritos.html"

    def get(self, request):
        inscritos = get_inscritos_filtrados(request)

        return render(request, self.template_name, {
            'inscritos': inscritos
        })

# Eliminar los registros de inscritos en el evento
def eliminar_registros(request, id):
    registro = get_object_or_404(Inscrito, id=id)
    registro.delete()
    messages.success(request, "Registro eliminado correctamente")
    return redirect('miepi:inscritos_list')

#class InscritoUpdateView(SuccessMessageMixin, UpdateView):
 #   model = Inscrito
  #  form_class = InscritoFormEdit
   # template_name = 'miepi/inscripciones/editar_inscrito.html'
    #success_url = reverse_lazy('miepi:inscritos_list')
    #success_message = "Registro actualizado correctamente"


class InscritoUpdateView(LoginRequiredMixin, View):
    template_name = 'miepi/inscripciones/editar_inscrito.html'

    def get(self, request, pk):
        inscrito = get_object_or_404(Inscrito, pk=pk)
        form = InscritoForm(instance=inscrito)

        return render(request, self.template_name, {
            'form': form,
            'inscrito': inscrito
        })

    def post(self, request, pk):
        inscrito = get_object_or_404(Inscrito, pk=pk)
        form = InscritoForm(request.POST, instance=inscrito)

        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
            return render(request, self.template_name, {
                'form': form,
                'inscrito': inscrito
            })

        form.save()
        messages.success(request, "Registro actualizado correctamente.")
        return redirect('miepi:inscritos_list')

class RegistrosPDFView(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Lista_Inscritos.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=30,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()

        cell_style = styles['Normal']
        cell_style.fontSize = 8
        cell_style.leading = 10

        # === ENCABEZADOS ===
        data = [[
            "Nombre",
            "Zona",
            "Subzona",
            "¿Otra denominación?",
            "Denominación",
            "Teléfono",
            "Correo Electrónico",
            "Grado Eclesiástico",
            "Monto",
        ]]

        registros = get_inscritos_filtrados(request)

        for a in registros:
            data.append([
                Paragraph(a.nombre or "", cell_style),
                Paragraph(a.zona or "", cell_style),
                Paragraph(a.subzona or "", cell_style),
                Paragraph("Sí" if a.otra_denominacion else "No", cell_style),
                Paragraph(a.denominacion or "", cell_style),
                Paragraph(a.telefono or "", cell_style),
                Paragraph(a.correo_electronico or "", cell_style),
                Paragraph(a.grado or "", cell_style),
                Paragraph(f"${a.monto}" if a.monto else "", cell_style),
            ])

        tabla = Table(
            data,
            colWidths=[95, 55, 65, 80, 95, 75, 160, 100, 50],
            repeatRows=1
        )

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#52658c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))

        doc.build([tabla])
        return response


#Pase de lista
def escanear_asistencia(request):
    inscritos = Inscrito.objects.order_by('nombre')
    return render(request, 'miepi/pase_lista/escanear.html', {
        'inscritos': inscritos
    })

class AsistenciasListView(View):
    template_name = 'miepi/pase_lista/lista_asistencias.html'

    def get(self, request):
        asistencias = Asistencia.objects.select_related('inscrito').order_by('-fecha', '-hora')
        
        # FILTRAR POR GÉNERO SI EXISTE EN GET
        genero = request.GET.get('genero')
        if genero:
            asistencias = asistencias.filter(inscrito__genero=genero)

        return render(request, self.template_name, {
            'asistencias': asistencias
        })

@login_required
def eliminar_asistencia(request, id):
    asistencia = get_object_or_404(Asistencia, id=id)

    asistencia.delete()
    messages.success(request, "✅ Asistencia eliminada correctamente")

    return redirect('miepi:lista_asistencias')



@csrf_exempt
def registrar_asistencia(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        if not codigo:
            return JsonResponse({
                "ok": False,
                "msg": "❌ Código vacío"
            })

        try:
            inscrito = Inscrito.objects.get(codigo=codigo)

            asistencia, creada = Asistencia.objects.get_or_create(
                inscrito=inscrito,
                fecha=timezone.now().date(),
                defaults={
                    "asistio": True,
                    "hora": timezone.now().time()
                }
            )

            if creada:
                return JsonResponse({
                    "ok": True,
                    "msg": f" Asistencia registrada: {inscrito.nombre}",
                    "fecha": asistencia.fecha.strftime("%Y-%m-%d"),
                    "hora": asistencia.hora.strftime("%H:%M")
                })
            else:
                return JsonResponse({
                    "ok": False,
                    "msg": f"⚠️ {inscrito.nombre} ya pasó lista hoy"
                })

        except Inscrito.DoesNotExist:
            return JsonResponse({
                "ok": False,
                "msg": "❌ QR no válido"
            })

    return JsonResponse({
        "ok": False,
        "msg": "Método no permitido"
    })

class AsistenciaPDFView(LoginRequiredMixin, View):

    def get(self, request):

        # =========================
        # FILTRO (MISMO QUE HTML)
        # =========================
        genero = request.GET.get('genero')

        asistencias = (
            Asistencia.objects
            .select_related('inscrito')
            .order_by('-fecha', '-hora')
        )

        if genero:
            asistencias = asistencias.filter(inscrito__genero=genero)

        # =========================
        # RESPUESTA PDF
        # =========================
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="lista_asistencias.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            rightMargin=20,
            leftMargin=20,
            topMargin=30,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()

        # 🔹 Estilo para salto de línea automático
        cell_style = ParagraphStyle(
            'cell',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=1  # CENTER
        )

        elementos = []

        # =========================
        # TÍTULO
        # =========================
        elementos.append(
            Paragraph("LISTA DE ASISTENCIAS", styles['Title'])
        )
        elementos.append(Paragraph("<br/>", styles['Normal']))

        # =========================
        # ENCABEZADOS
        # =========================
        data = [[
            "Día",
            "Fecha",
            "Nombre",
            "Correo",
            "Teléfono",
            "Zona",
            "Subzona",
            "Asistió"
        ]]

        # =========================
        # REGISTROS
        # =========================
        for a in asistencias:
            data.append([
                Paragraph(date_format(a.fecha, "l"), cell_style),
                Paragraph(a.fecha.strftime('%d/%m/%Y'), cell_style),
                Paragraph(a.inscrito.nombre, cell_style),
                Paragraph(a.inscrito.correo_electronico or "-", cell_style),
                Paragraph(a.inscrito.telefono or "-", cell_style),
                Paragraph(a.inscrito.zona or "-", cell_style),
                Paragraph(a.inscrito.subzona or "-", cell_style),
                Paragraph("Sí" if a.asistio else "No", cell_style),
            ])

        # =========================
        # TABLA
        # =========================
        tabla = Table(
            data,
            repeatRows=1,
            colWidths=[
                60,   # Día
                70,   # Fecha
                140,  # Nombre
                180,  # Correo
                90,   # Teléfono
                90,   # Zona
                90,   # Subzona
                60    # Asistió
            ]
        )

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#52658c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),

            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        elementos.append(tabla)
        doc.build(elementos)

        return response


def buscar_inscrito(request):
    q = request.GET.get('q', '').strip()

    if not q:
        return JsonResponse([], safe=False)

    inscritos = Inscrito.objects.filter(
        Q(nombre__icontains=q) |
        Q(telefono__icontains=q)
    )[:10]

    data = []
    for i in inscritos:
        data.append({
            "id": i.id,
            "nombre": i.nombre,
            "telefono": i.telefono,
            "codigo": i.codigo
        })

    return JsonResponse(data, safe=False)