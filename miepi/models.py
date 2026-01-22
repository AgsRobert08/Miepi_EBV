from django.db import models
import uuid


def qr_upload_path(instance, filename):
    return f"qr/inscritos/{instance.codigo}.png"

class Inscrito(models.Model):
    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nombre = models.CharField(max_length=150, null=True)

    GENEROS = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]
    genero = models.CharField(max_length=150, choices=GENEROS)

    ZONAS = [
        ('CENTRAL', 'CENTRAL'),
        ('CDMX', 'CD. DE MEX.'),
        ('PUEBLA', 'PUEBLA, PUE.'),
        ('XALAPA', 'XALAPA, VER.'),
        ('MISANTLA', 'MISANTLA, VER.'),
        ('ALTOTONGA', 'ALTOTONGA, VER.'),
        ('JUCHIQUE', 'JUCHIQUE DE FERRER, VER.'),
        ('POZA_RICA', 'POZA RICA, VER.'),
        ('CUERNAVACA', 'CUERNAVACA, MOR.'),
        ('URUAPAN', 'URUAPAN, MICH.'),
        ('CARDENAS', 'CARDENAS, TAB.'),
        ('GUADALAJARA', 'GUADALAJARA, JAL.'),
        ('SILAO', 'SILAO, GTO.'),
        ('PACHUCA', 'PACHUCA, HGO.'),
        ('CANCUN', 'CANCÚN, Q. R.'),
        ('JUAREZ', 'CIUDAD JUÁREZ, CHIH.'),
        ('MATIAS_ROMERO', 'MATÍAS ROMERO, OAX.'),
        ('CHILPANCINGO', 'CHILPANCINGO, GRO.'),
        ('TIJUANA', 'TIJUANA, B.C.'),
        ('REYNOSA', 'REYNOSA, TAMPS.'),
        ('TOLUCA', 'TOLUCA, EDO. DE MEX.'),
        ('OAXACA', 'OAXACA, OAX.'),
        ('ELGIN', 'ELGIN ILLINOIS, EUA'),
        ('TAPACHULA', 'TAPACHULA, CHIS.'),
        ('CABO', 'CABO SAN LUCAS, B.C.S.'),
        ('TEZIUTLAN', 'TEZIUTLÁN, PUE.'),
        ('TAMPICO', 'TAMPICO, TAMPS.'),
        ('VERACRUZ', 'VERACRUZ, VER.'),
        ('TOPILEJO', 'TOPILEJO, CD. MEX.'),
        ('NEZA', 'CIUDAD NEZAHUALCÓYOTL, EDOMEX'),
        ('MIRAFLORES', 'MIRAFLORES, EDOMEX'),
        ('CALPULALPAN', 'CALPULALPAN, TLAX.'),
        ('COYOTEPEC', 'COYOTEPEC, EDOMEX'),
        ('CENTRO_SUR', 'CENTRO Y SUDAMÉRICA'),
    ]

    zona = models.CharField(max_length=200, choices=ZONAS, blank=True, null=True)
    subzona = models.CharField(max_length=200, blank=True, null=True)

    otra_denominacion = models.BooleanField(default=False)
    denominacion = models.CharField(max_length=200, blank=True, null=True)

    iglesia = models.CharField(max_length=200, null=True, blank=True)
    pastor = models.CharField(max_length=200, null=True, blank=True)

    telefono = models.CharField(max_length=200, unique=True)
    correo_electronico = models.EmailField(null=True, blank=True)

    GRADOS = [
        ('MINISTRO', 'MINISTRO / DIACONISA'),
        ('EG_ITE_ESC', 'EGRESADO DEL I.T.E. (Sistema Escolarizado)'),
        ('EG_ITE_AB', 'EGRESADO DEL I.T.E. (Sistema Abierto)'),
        ('EST_1_ESC', 'ESTUDIANTE (PRIMER AÑO) S.E.'),
        ('EST_2_ESC', 'ESTUDIANTE (SEGUNDO AÑO) S.E.'),
        ('EST_3_ESC', 'ESTUDIANTE (TERCER AÑO) S.E.'),
        ('EST_1_AB', 'ESTUDIANTE (PRIMER AÑO) S. ABIERTO'),
        ('EST_2_AB', 'ESTUDIANTE (SEGUNDO AÑO) S. ABIERTO'),
        ('EST_3_AB', 'ESTUDIANTE (TERCER AÑO) S. ABIERTO'),
        ('EST_4_AB', 'ESTUDIANTE (CUARTO AÑO) S. ABIERTO'),
        ('OBRERO', 'OBRERO LAICO'),
        ('ANCIANO', 'ANCIANO DE IGLESIA'),
        ('OTRO', 'OTRO (ESPECIFICAR)'),
        ('REP_ZONA', 'REPRESENTANTE DE ZONA'),
        ('REP_SUBZONA', 'REPRESENTANTE DE SUB ZONA'),
        ('EG_XAL_ESC', 'EGRESADO ITE CAMPUS XALAPA S. ESCOLARIZADO'),
        ('EG_XAL_AB', 'EGRESADO ITE CAMPUS XALAPA S. ABIERTO'),
        ('EG_SUR_ESC', 'EGRESADO ITE CAMPUS SURESTE S. ESCOLARIZADO'),
        ('EG_ELGIN', 'EGRESADO ITE CAMPUS ELGIN, IL'),
        ('SIN_RANGO', 'SIN RANGO'),
    ]
    grado = models.CharField(max_length=200, choices=GRADOS)

    periodo = models.CharField(max_length=200, null=True)
    monto = models.DecimalField(max_digits=100, decimal_places=2)

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
