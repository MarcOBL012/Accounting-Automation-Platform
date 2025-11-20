from django import forms
from .models import AsientoContable, Saldo_Inicial
from .constants import cuentas_dict, tipo_cuenta, valores_tipo_monto

class AsientoContableForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AsientoContableForm, self).__init__(*args, **kwargs)
        self.fields['cuenta'].choices = cuentas_dict
        self.fields['tipo_cuenta'].choices = tipo_cuenta
        self.fields['tipo_monto'].choices = valores_tipo_monto

    class Meta:
        model = AsientoContable
        fields = ['fecha', 'cuenta', 'tipo_cuenta', 'tipo_monto', 'monto', 'glose']
        
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'monto': forms.NumberInput(attrs={'step': '0.01'}),
            'glose': forms.Textarea(attrs={'rows': 3, 'maxlength': '100'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class SaldoInicialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SaldoInicialForm, self).__init__(*args, **kwargs)
        self.fields['cuenta'].choices = cuentas_dict

    class Meta:
        model = Saldo_Inicial
        fields = ['cuenta', 'saldo_inicial']
        widgets = {
            'saldo_inicial': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Saldo Inicial'}),
        }
