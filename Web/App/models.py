from django.db import models
from .constants import tipo_cuenta, valores_tipo_monto

# Create your models here.
class AsientoContable(models.Model):
    fecha = models.DateField()
    cuenta = models.CharField(max_length=255)
    tipo_cuenta = models.CharField(max_length=50, choices=tipo_cuenta)
    tipo_monto = models.CharField(max_length=5, choices=valores_tipo_monto)
    monto = models.FloatField()
    glose = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.cuenta} ({self.fecha})"


class Saldo_Inicial(models.Model):
    cuenta = models.CharField(max_length=100)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cuenta} - Saldo: {self.saldo_inicial}"
