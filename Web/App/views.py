from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import AsientoContable, Saldo_Inicial
from .forms import AsientoContableForm, SaldoInicialForm
from .constants import valores_cuentas, tipo_cuenta_valor, valores_tipo_monto, cuentas_dict, tipo_cuenta
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_protect
import json

# Create your views here.
@csrf_protect
def home(request):
    if request.method == 'POST':
        form = AsientoContableForm(request.POST)
        if form.is_valid():
            cuenta = form.cleaned_data['cuenta']
            tipo_cuenta_codigo = form.cleaned_data['tipo_cuenta']
            
            if tipo_cuenta_codigo is None:
                form.add_error('tipo_cuenta', "Tipo de cuenta no válido")
                return render(request, 'home.html', {'form': form})
                
            tipo_monto = form.cleaned_data['tipo_monto']
            monto = form.cleaned_data['monto']
            fecha = form.cleaned_data['fecha']
            glosa = form.cleaned_data.get('glose', '')

            asiento = AsientoContable(
                fecha=fecha,
                cuenta=cuenta,
                tipo_cuenta=tipo_cuenta_codigo,
                tipo_monto=tipo_monto,
                monto=monto,
                glose=glosa if glosa else None
            )
            asiento.save()

            return redirect('home')
        else:
            return render(request, 'home.html', {'form': form})
    else:
        form = AsientoContableForm()
        form.fields['cuenta'].choices = cuentas_dict
        form.fields['tipo_cuenta'].choices = tipo_cuenta
        form.fields['tipo_monto'].choices = valores_tipo_monto

    context = {
        'form': form,
        'valores_cuentas': valores_cuentas,
        'valores_tipo_monto': valores_tipo_monto,
        'tipo_cuenta': tipo_cuenta,
        'cuentas_dict': cuentas_dict,
        'errors': form.errors if form.errors else None
    }
    return render(request, 'home.html', context)

def registro(request):
    fecha_inicio, fecha_final = obtener_fechas(request)

    if fecha_inicio and fecha_final:
        asientos = AsientoContable.objects.filter(fecha__range=(fecha_inicio, fecha_final))
    else:
        asientos = AsientoContable.objects.all()

    saldos = Saldo_Inicial.objects.all()

    resultados_mayores = calcular_mayores(asientos)
    resultados_mayores_ce = calcular_mayores_ce(asientos, saldos)
    estado_resultados, utilidad_bruta, utilidad_operacion, utilidad_antes_impuestos, utilidad_neta = calcular_estado_resultados(asientos)
    estado_situacion_financiera = calcular_situacion_financiera(asientos)

    resultados_mayores_json = json.dumps(resultados_mayores, cls=DjangoJSONEncoder, ensure_ascii=False)
    resultados_mayores_ce_json = json.dumps(resultados_mayores_ce, cls=DjangoJSONEncoder, ensure_ascii=False)
    
    context = {
        'libro_diario': calcular_libro_diario(asientos),
        'resultados_mayores': resultados_mayores,
        'resultados_mayores_ce': resultados_mayores_ce,
        'resultados_mayores_json': resultados_mayores_json,
        'resultados_mayores_ce_json': resultados_mayores_ce_json,
        'estado_resultados': {
            'ventas': estado_resultados['ventas'], 'costo_ventas': estado_resultados['costo_ventas'],
            'utilidad_bruta': utilidad_bruta, 'gastos_administrativos': estado_resultados['gastos_administrativos'],
            'gastos_ventas': estado_resultados['gastos_ventas'], 'utilidad_operacion': utilidad_operacion,
            'otros_ingresos': estado_resultados['otros_ingresos'], 'ingresos_financieros': estado_resultados['ingresos_financieros'],
            'otros_gastos': estado_resultados['otros_gastos'], 'gastos_financieros': estado_resultados['gastos_financieros'],
            'utilidad_antes_impuestos': utilidad_antes_impuestos, 'impuesto_renta': estado_resultados['impuesto_renta'],
            'utilidad_neta': utilidad_neta,
        },
        'estado_situacion_financiera': estado_situacion_financiera,
        'cuentas_dict': cuentas_dict,
        'tipo_cuenta': tipo_cuenta,
    }
    return render(request, 'registros.html', context)

def calcular_libro_diario(asientos):
    cuentas_dict_dic = dict(cuentas_dict)
    return [
        (asiento.fecha, asiento.cuenta, cuentas_dict_dic.get(asiento.tipo_cuenta, asiento.tipo_cuenta), asiento.glose, asiento.tipo_monto, asiento.monto)
        for asiento in asientos
    ]

# Helper function to calculate the state of results
def calcular_estado_resultados(asientos):
    estado_resultados = {
        'ventas': 0, 'costo_ventas': 0, 'gastos_administrativos': 0, 'gastos_ventas': 0,
        'otros_ingresos': 0, 'ingresos_financieros': 0, 'otros_gastos': 0, 'gastos_financieros': 0, 'impuesto_renta': 0
    }

    for asiento in asientos:
        cuenta = str(asiento.cuenta)
        if cuenta == '70':
            estado_resultados['ventas'] += float(asiento.monto)
        elif cuenta == '75':
            estado_resultados['otros_ingresos'] += float(asiento.monto)
        elif cuenta == '77':
            estado_resultados['ingresos_financieros'] += float(asiento.monto)
        elif cuenta == '69':
            estado_resultados['costo_ventas'] += float(asiento.monto)
        elif cuenta == '94':
            estado_resultados['gastos_administrativos'] += float(asiento.monto)
        elif cuenta == '95':
            estado_resultados['gastos_ventas'] += float(asiento.monto)
        elif cuenta == '65':
            estado_resultados['otros_gastos'] += float(asiento.monto)
        elif cuenta == '67':
            estado_resultados['gastos_financieros'] += float(asiento.monto)
        elif cuenta == '88':
            estado_resultados['impuesto_renta'] += float(asiento.monto)

    utilidad_bruta = estado_resultados['ventas'] - estado_resultados['costo_ventas']
    utilidad_operacion = utilidad_bruta - estado_resultados['gastos_administrativos'] - estado_resultados['gastos_ventas']
    utilidad_antes_impuestos = utilidad_operacion + estado_resultados['otros_ingresos'] + estado_resultados['ingresos_financieros'] - estado_resultados['otros_gastos'] - estado_resultados['gastos_financieros']
    utilidad_neta = utilidad_antes_impuestos - estado_resultados['impuesto_renta']

    return estado_resultados, utilidad_bruta, utilidad_operacion, utilidad_antes_impuestos, utilidad_neta


# Helper function to calculate the financial situation
def calcular_situacion_financiera(asientos):
    activos_corrientes = {}
    pasivos_corrientes = {}
    activos_no_corrientes = {}
    pasivos_no_corrientes = {}
    patrimonio = {}
    valores_cuentas = {
        '10': 0,
        '11': 0,
        '12': 0,
        '13': 0,
        '14': 0,
        '16': 0,
        '17': 0,
        '18': 0,
        '20': 0,
        '21': 0,
        '22': 0,
        '23': 0,
        '24': 0,
        '25': 0,
        '26': 0,
        '27': 0,
        '28': 0,
        '29': 0,
        '30': 0,
        '31': 0,
        '32': 0,
        '33': 0,
        '34': 0,
        '35': 0,
        '36': 0,
        '37': 0,
        '38': 0,
        '39': 0,
        '40': 0,
        '41': 0,
        '42': 0,
        '43': 0,
        '44': 0,
        '45': 0,
        '46': 0,
        '47': 0,
        '48': 0,
        '49': 0,
        '50': 0,
        '51': 0,
        '52': 0,
        '56': 0,
        '57': 0,
        '58': 0,
    }

    for asiento in asientos:
        tipo_cuenta = str(asiento.cuenta)
        cuenta = str(asiento.tipo_cuenta)

        if tipo_cuenta == 'Desconocido':
            continue

        tipo_cuenta_num = int(tipo_cuenta)
        if 40 <= tipo_cuenta_num <= 59:
            monto = float(-asiento.monto) if asiento.tipo_monto == 'D' else float(asiento.monto)
        else:
            monto = float(asiento.monto) if asiento.tipo_monto == 'D' else float(-asiento.monto)

        if cuenta == 'AC':
            if tipo_cuenta not in activos_corrientes:
                activos_corrientes[tipo_cuenta] = 0
            activos_corrientes[tipo_cuenta] += monto
            valores_cuentas[tipo_cuenta] += monto
        elif cuenta == 'ANC':
            if tipo_cuenta not in activos_no_corrientes:
                activos_no_corrientes[tipo_cuenta] = 0
            activos_no_corrientes[tipo_cuenta] += monto
            valores_cuentas[tipo_cuenta] += monto
        elif cuenta == 'P' and (tipo_cuenta in ["40", "41", "42", "43", "44", "46", "47", "48"]):
            if tipo_cuenta not in pasivos_corrientes:
                pasivos_corrientes[tipo_cuenta] = 0
            pasivos_corrientes[tipo_cuenta] += monto
            valores_cuentas[tipo_cuenta] += monto
        elif cuenta == 'P' and (tipo_cuenta in ["45","49"]):
            if tipo_cuenta not in pasivos_no_corrientes:
                pasivos_no_corrientes[tipo_cuenta] = 0
            pasivos_no_corrientes[tipo_cuenta] += monto
            valores_cuentas[tipo_cuenta] += monto
        elif cuenta == 'PT':
            if tipo_cuenta not in patrimonio:
                patrimonio[tipo_cuenta] = 0
            patrimonio[tipo_cuenta] += monto
            valores_cuentas[tipo_cuenta] += monto

    total_activo_corriente = sum(activos_corrientes.values())
    total_pasivo_corriente = sum(pasivos_corrientes.values())
    total_activo_no_corriente = sum(activos_no_corrientes.values())
    total_pasivo_no_corriente = sum(pasivos_no_corrientes.values())
    total_patrimonio = sum(patrimonio.values())

    total_activo = total_activo_corriente + total_activo_no_corriente
    total_pasivo = total_pasivo_corriente + total_pasivo_no_corriente
    total_pasivo_patrimonio = total_pasivo + total_patrimonio

    return {
        'activos_corrientes': activos_corrientes,
        'pasivos_corrientes': pasivos_corrientes,
        'activos_no_corrientes': activos_no_corrientes,
        'pasivos_no_corrientes': pasivos_no_corrientes,
        'patrimonio': patrimonio,
        'total_activo_corriente': total_activo_corriente,
        'total_pasivo_corriente': total_pasivo_corriente,
        'total_activo_no_corriente': total_activo_no_corriente,
        'total_pasivo_no_corriente': total_pasivo_no_corriente,
        'total_activo': total_activo,
        'total_pasivo': total_pasivo,
        'total_patrimonio': total_patrimonio,
        'total_pasivo_patrimonio': total_pasivo_patrimonio,
        'valores_cuentas': valores_cuentas
    }

# Helper function to extract date range from request
def obtener_fechas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_final = request.GET.get('fecha_final')

    if fecha_inicio and fecha_final:
        fecha_inicio = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_final = timezone.datetime.strptime(fecha_final, '%Y-%m-%d')
        return fecha_inicio, fecha_final
    return None, None

# Helper function to get monto from asiento
def obtener_monto(asiento, tipo):
    if asiento.tipo_monto == tipo:
        return asiento.monto
    return 0

def calcular_mayores(asientos):
    mayores = {}
    
    for asiento in asientos:
        if asiento.cuenta not in mayores:
            mayores[asiento.cuenta] = {
                'fechas_debe_haber': [],
                'total_debe': 0,
                'total_haber': 0
            }

        debe = obtener_monto(asiento, 'D')
        haber = obtener_monto(asiento, 'H')

        if debe > 0 or haber > 0:
            mayores[asiento.cuenta]['fechas_debe_haber'].append({
                'fecha': asiento.fecha.strftime('%d/%m/%Y'),
                'debe': float(debe),
                'haber': float(haber)
            })
            mayores[asiento.cuenta]['total_debe'] += float(debe)
            mayores[asiento.cuenta]['total_haber'] += float(haber)

    return [
        {
            'cuenta': dict(cuentas_dict).get(cuenta, cuenta),
            'fechas_debe_haber': data['fechas_debe_haber'],
            'total_debe': float(data['total_debe']),
            'total_haber': float(data['total_haber'])
        }
        for cuenta, data in mayores.items()
        if data['fechas_debe_haber']
    ]

# Helper function to calculate mayores by specific account
def calcular_mayores_ce(asientos, saldos):
    mayores_ce = {}
    
    for asiento in asientos:
        if asiento.tipo_cuenta not in mayores_ce:
            mayores_ce[asiento.tipo_cuenta] = {
                'fechas_debe_haber': [],
                'total_debe': 0,
                'total_haber': 0,
                'saldo_final': 0
            }
            
            saldo_cuenta = saldos.filter(cuenta=asiento.tipo_cuenta).last()
            if saldo_cuenta:
                mayores_ce[asiento.tipo_cuenta]['saldo_final'] = float(saldo_cuenta.saldo_inicial)

        debe = obtener_monto(asiento, 'D')
        haber = obtener_monto(asiento, 'H')

        if debe > 0 or haber > 0:
            mayores_ce[asiento.tipo_cuenta]['fechas_debe_haber'].append({
                'fecha': asiento.fecha.strftime('%d/%m/%Y'),
                'debe': float(debe),
                'haber': float(haber)
            })
            mayores_ce[asiento.tipo_cuenta]['total_debe'] += float(debe)
            mayores_ce[asiento.tipo_cuenta]['total_haber'] += float(haber)

            try:
                tipo_cuenta_num = int(asiento.tipo_cuenta)
                if 40 <= tipo_cuenta_num <= 59:  # Cuentas de pasivo
                    mayores_ce[asiento.tipo_cuenta]['saldo_final'] -= float(debe)
                    mayores_ce[asiento.tipo_cuenta]['saldo_final'] += float(haber)
                else:  # Cuentas de activo
                    mayores_ce[asiento.tipo_cuenta]['saldo_final'] += float(debe)
                    mayores_ce[asiento.tipo_cuenta]['saldo_final'] -= float(haber)
            except ValueError:
                mayores_ce[asiento.tipo_cuenta]['saldo_final'] += float(debe)
                mayores_ce[asiento.tipo_cuenta]['saldo_final'] -= float(haber)

    return [
        {
            'tipo_cuenta': dict(cuentas_dict).get(tipo_cuenta, tipo_cuenta),
            'fechas_debe_haber': data['fechas_debe_haber'],
            'total_debe': float(data['total_debe']),
            'total_haber': float(data['total_haber']),
            'saldo_final': float(data['saldo_final'])
        }
        for tipo_cuenta, data in mayores_ce.items()
        if data['fechas_debe_haber'] 
    ]

@csrf_protect
def saldo(request):
    if request.method == 'POST':
        form = SaldoInicialForm(request.POST)
        if form.is_valid():
            cuenta = form.cleaned_data['cuenta']
            saldo_inicial = form.cleaned_data['saldo_inicial']
            
            saldo = Saldo_Inicial(
                cuenta=cuenta,
                saldo_inicial=saldo_inicial
            )
            saldo.save()
            
            return redirect('saldo')
    else:
        form = SaldoInicialForm()
        form.fields['cuenta'].choices = cuentas_dict

    saldos = Saldo_Inicial.objects.all().order_by('-fecha_registro')
    
    context = {
        'form': form,
        'saldos': saldos,
        'cuentas_dict': cuentas_dict
    }
    return render(request, 'saldo.html', context)