#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para calcular proyecciones UVA
Usa tasa de inflación mensual configurable por plan
"""

from datetime import datetime

# Valor UVA base aproximado (actualizar según necesidad)
UVA_BASE = 1500.0

def get_valor_uva_actual():
    """
    Obtener el valor actual de UVA
    
    Returns:
        dict: {fecha, valor, cer, fuente}
    """
    # Valor UVA aproximado actual
    return {
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'valor': UVA_BASE,
        'cer': 100000.0,  # CER aproximado
        'fuente': 'manual'
    }

def proyectar_uva(meses, tasa_inflacion_mensual=0.04):
    """
    Proyectar valores futuros de UVA basado en tasa de inflación
    
    Args:
        meses: Cantidad de meses a proyectar
        tasa_inflacion_mensual: Tasa de inflación mensual en decimal (ej: 0.04 para 4%)
    
    Returns:
        list: Lista de valores UVA proyectados por mes
    """
    uva_actual = UVA_BASE
    proyeccion = []
    
    for mes in range(meses + 1):
        uva_proyectado = uva_actual * ((1 + tasa_inflacion_mensual) ** mes)
        proyeccion.append({
            'mes': mes,
            'valor_uva': round(uva_proyectado, 2)
        })
    
    return proyeccion

def calcular_cuota_uva(importe_financiar, plazo_meses, tasa_interes_anual, tasa_inflacion_mensual=0.04):
    """
    Calcular cuotas para crédito UVA
    
    Args:
        importe_financiar: Monto a financiar en pesos
        plazo_meses: Cantidad de meses del crédito
        tasa_interes_anual: Tasa de interés anual (%)
        tasa_inflacion_mensual: Tasa de inflación mensual en decimal
    
    Returns:
        dict: Información de la cuota UVA
    """
    # Convertir importe a UVAs al valor actual
    uva_actual = UVA_BASE
    importe_en_uvas = importe_financiar / uva_actual
    
    # Calcular cuota en UVAs (French)
    if tasa_interes_anual > 0:
        tasa_mensual = (tasa_interes_anual / 100) / 12
        cuota_uva = importe_en_uvas * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)
    else:
        cuota_uva = importe_en_uvas / plazo_meses
    
    # Proyectar cuotas en pesos
    proyeccion_uva = proyectar_uva(plazo_meses, tasa_inflacion_mensual)
    
    cuotas_pesos = []
    for mes in range(1, plazo_meses + 1):
        valor_uva_mes = proyeccion_uva[mes]['valor_uva']
        cuota_pesos = cuota_uva * valor_uva_mes
        cuotas_pesos.append({
            'mes': mes,
            'cuota_uva': round(cuota_uva, 2),
            'valor_uva': valor_uva_mes,
            'cuota_pesos': round(cuota_pesos, 2)
        })
    
    return {
        'importe_en_uvas': round(importe_en_uvas, 2),
        'cuota_fija_uva': round(cuota_uva, 2),
        'cuotas': cuotas_pesos,
        'primera_cuota_pesos': round(cuota_uva * uva_actual, 2),
        'ultima_cuota_pesos': cuotas_pesos[-1]['cuota_pesos'] if cuotas_pesos else 0
    }

# Para testing
if __name__ == "__main__":
    print("=" * 60)
    print("PROYECCIÓN UVA")
    print("=" * 60)
    
    # Valor actual
    uva = get_valor_uva_actual()
    print(f"\nUVA Actual:")
    print(f"  Fecha: {uva['fecha']}")
    print(f"  Valor: ${uva['valor']:,.2f}")
    
    # Proyección
    print(f"\nProyección UVA (12 meses al 4% mensual):")
    proyeccion = proyectar_uva(12, 0.04)
    for p in proyeccion[:5]:  # Mostrar primeros 5 meses
        print(f"  Mes {p['mes']:2d}: ${p['valor_uva']:,.2f}")
    print("  ...")
    print(f"  Mes {proyeccion[-1]['mes']:2d}: ${proyeccion[-1]['valor_uva']:,.2f}")
    
    # Ejemplo de crédito
    print(f"\nEjemplo Crédito UVA:")
    print(f"  Monto: $10.000.000")
    print(f"  Plazo: 12 meses")
    print(f"  Tasa: 15% anual")
    print(f"  Inflación: 4% mensual")
    
    resultado = calcular_cuota_uva(10000000, 12, 15, 0.04)
    print(f"\n  Capital en UVAs: {resultado['importe_en_uvas']:,.2f} UVAs")
    print(f"  Cuota fija: {resultado['cuota_fija_uva']:,.2f} UVAs")
    print(f"  Primera cuota: ${resultado['primera_cuota_pesos']:,.2f}")
    print(f"  Última cuota: ${resultado['ultima_cuota_pesos']:,.2f}")
    
    print("=" * 60)
