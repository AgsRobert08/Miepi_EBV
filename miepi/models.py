from django.db import models
import uuid


def qr_upload_path(instance, filename):
    return f"qr/inscritos/{instance.codigo}.png"

class Inscrito(models.Model):
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=150, null=True)

    GENEROS = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    genero = models.CharField(max_length=2, choices=GENEROS)

    ZONAS = [
        ('CEN', 'CENTRAL'),
        ('CDMX', 'CD. DE MEX.'),
        ('PUE', 'PUEBLA, PUE.'),
        ('XAL', 'XALAPA, VER.'),
        ('MIS', 'MISANTLA, VER.'),
        ('ALT', 'ALTOTONGA, VER.'),
        ('JUC', 'JUCHIQUE DE FERRER, VER.'),
        ('POZ', 'POZA RICA, VER.'),
        ('CUE', 'CUERNAVACA, MOR.'),
        ('URU', 'URUAPAN, MICH.'),
        ('CAR', 'CARDENAS, TAB.'),
        ('GDL', 'GUADALAJARA, JAL.'),
        ('SIL', 'SILAO, GTO.'),
        ('PAC', 'PACHUCA, HGO.'),
        ('CAN', 'CANCÚN, Q. R.'),
        ('JUA', 'CIUDAD JUÁREZ, CHIH.'),
        ('MAT', 'MATÍAS ROMERO, OAX.'),
        ('CHP', 'CHILPANCINGO, GRO.'),
        ('TIJ', 'TIJUANA, B.C.'),
        ('REY', 'REYNOSA, TAMPS.'),
        ('TOL', 'TOLUCA, EDO. DE MEX.'),
        ('OAX', 'OAXACA, OAX.'),
        ('ELG', 'ELGIN ILLINOIS, EUA'),
        ('TAP', 'TAPACHULA, CHIS.'),
        ('CAB', 'CABO SAN LUCAS, B.C.S.'),
        ('TEZ', 'TEZIUTLÁN, PUE.'),
        ('TAM', 'TAMPICO, TAMPS.'),
        ('VER', 'VERACRUZ, VER.'),
        ('TOP', 'TOPILEJO, CD. MEX.'),
        ('NEZ', 'CIUDAD NEZAHUALCÓYOTL, EDOMEX'),
        ('MIR', 'MIRAFLORES, EDOMEX'),
        ('CAL', 'CALPULALPAN, TLAX.'),
        ('COY', 'COYOTEPEC, EDOMEX'),
        ('CSU', 'CENTRO Y SUDAMÉRICA'),
    ]

    zona = models.CharField(max_length=100, choices=ZONAS, blank=True, null=True)
    subzona = models.CharField(max_length=100, blank=True, null=True)

    otra_denominacion = models.BooleanField(default=False)
    denominacion = models.CharField(max_length=150, blank=True, null=True)

    iglesia = models.CharField(max_length=150, null=True, blank=True)
    pastor = models.CharField(max_length=150, null=True, blank=True)

    telefono = models.CharField(max_length=20, unique=True)
    correo_electronico = models.EmailField(null=True, blank=True)

    GRADOS = [
        ('MIN', 'MINISTRO / DIACONISA'),
        ('EG_ESC', 'EGRESADO DEL I.T.E. (Sistema Escolarizado)'),
        ('EG_AB', 'EGRESADO DEL I.T.E. (Sistema Abierto)'),
        ('EST_1E', 'ESTUDIANTE (PRIMER AÑO) S.E.'),
        ('EST_2E', 'ESTUDIANTE (SEGUNDO AÑO) S.E.'),
        ('EST_3E', 'ESTUDIANTE (TERCER AÑO) S.E.'),
        ('EST_1A', 'ESTUDIANTE (PRIMER AÑO) S. ABIERTO'),
        ('EST_2A', 'ESTUDIANTE (SEGUNDO AÑO) S. ABIERTO'),
        ('EST_3A', 'ESTUDIANTE (TERCER AÑO) S. ABIERTO'),
        ('EST_4A', 'ESTUDIANTE (CUARTO AÑO) S. ABIERTO'),
        ('OBR', 'OBRERO LAICO'),
        ('ANC', 'ANCIANO DE IGLESIA'),
        ('OTR', 'OTRO (ESPECIFICAR)'),
        ('REP_Z', 'REPRESENTANTE DE ZONA'),
        ('REP_S', 'REPRESENTANTE DE SUB ZONA'),
        ('EG_XE', 'EGRESADO ITE CAMPUS XALAPA S. ESCOLARIZADO'),
        ('EG_XA', 'EGRESADO ITE CAMPUS XALAPA S. ABIERTO'),
        ('EG_SE', 'EGRESADO ITE CAMPUS SURESTE S. ESCOLARIZADO'),
        ('EG_EL', 'EGRESADO ITE CAMPUS ELGIN, IL'),
        ('SIN_R', 'SIN RANGO'),
    ]
    grado = models.CharField(max_length=100, choices=GRADOS)

    periodo = models.CharField(max_length=50, null=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)

    qr_image = models.ImageField(upload_to=qr_upload_path, blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Asistencia(models.Model):
    inscrito = models.ForeignKey(
        Inscrito,
        on_delete=models.CASCADE,
        related_name="asistencias"
    )
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    asistio = models.BooleanField(default=True)

    class Meta:
        unique_together = ('inscrito', 'fecha')
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['inscrito']),
        ]

    def __str__(self):
        return f"{self.inscrito.nombre} - {self.fecha}"