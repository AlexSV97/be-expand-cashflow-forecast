"""
GENERADOR DE DATOS FICTICIOS COHERENTES - BeExpand
===================================================
Cash Flow Forecasting - Curso IA en Finanzas y Contabilidad

Genera 4 CSV relacionados:
  1. crm.csv              -> Clientes, proyectos y pipeline
  2. erp.csv              -> Facturas emitidas (ingresos) y recibidas (gastos)
  3. bank_statements.csv  -> Extractos bancarios mensuales
  4. external_data.csv    -> IPC, Euribor, estacionalidad

Periodo: Enero 2023 - Abril 2026
Coherencia: CRM -> ERP -> Bank Statements. Los 4 archivos estan vinculados.
Semilla fija: 42 -> reproducible
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import calendar

# --- Semilla reproducible -------------------------------------------------
np.random.seed(42)

# --- Directorio de salida -------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Periodo de analisis --------------------------------------------------
START = datetime(2023, 1, 1)
END = datetime(2026, 4, 30)

# --- Funciones auxiliares -------------------------------------------------

def generar_meses(inicio, fin):
    """Genera lista de dias 1 de cada mes entre inicio y fin."""
    meses = []
    current = datetime(inicio.year, inicio.month, 1)
    while current <= fin:
        meses.append(current)
        mes_sig = current.month % 12 + 1
        anio_sig = current.year + (1 if mes_sig == 1 else 0)
        current = datetime(anio_sig, mes_sig, 1)
    return meses

def ultimo_dia_mes(fecha):
    """Devuelve el ultimo dia del mes de la fecha dada."""
    _, ultimo = calendar.monthrange(fecha.year, fecha.month)
    return datetime(fecha.year, fecha.month, ultimo)

MESES = generar_meses(START, END)
TOTAL_MESES = len(MESES)  # 40 meses

print(f"Generando datos desde {MESES[0].date()} hasta {MESES[-1].date()}")
print(f"Total meses: {TOTAL_MESES}")

# ===========================================================================
# 1. DATOS EXTERNOS - IPC, EURIBOR, ESTACIONALIDAD
# ===========================================================================

print("\n[1/4] Generando datos externos...")

ipc_valores = {
    2023: [5.8, 6.0, 5.5, 4.8, 4.2, 3.8, 3.5, 3.6, 3.8, 3.5, 3.2, 3.0],
    2024: [3.4, 3.6, 3.3, 3.0, 3.2, 3.5, 3.0, 2.8, 2.6, 2.8, 2.7, 2.9],
    2025: [2.9, 2.7, 2.5, 2.6, 2.8, 2.5, 2.3, 2.4, 2.5, 2.6, 2.5, 2.4],
    2026: [2.5, 2.6, 2.4, 2.3, None, None, None, None, None, None, None, None],
}

euribor_valores = {
    2023: [3.35, 3.55, 3.70, 3.85, 3.90, 4.00, 4.05, 4.10, 4.15, 4.05, 4.00, 3.85],
    2024: [3.70, 3.65, 3.75, 3.80, 3.70, 3.60, 3.55, 3.50, 3.45, 3.30, 3.15, 2.95],
    2025: [2.85, 2.75, 2.70, 2.65, 2.60, 2.55, 2.50, 2.55, 2.60, 2.55, 2.50, 2.45],
    2026: [2.40, 2.35, 2.30, 2.25, None, None, None, None, None, None, None, None],
}

factor_estacional = {
    1: 1.10,   # Enero: planificacion anual
    2: 0.95,   # Febrero
    3: 1.15,   # Marzo: ferias internacionales
    4: 1.20,   # Abril: ferias
    5: 1.05,   # Mayo
    6: 1.00,   # Junio
    7: 0.90,   # Julio: prevacaciones
    8: 0.50,   # Agosto: VACACIONES
    9: 1.15,   # Septiembre: vuelta
    10: 1.20,  # Octubre: ferias otono
    11: 1.00,  # Noviembre
    12: 0.70,  # Diciembre: navidad
}

external_rows = []
for mes in MESES:
    anio = mes.year
    ipc = ipc_valores.get(anio, [None]*12)[mes.month - 1]
    euribor = euribor_valores.get(anio, [None]*12)[mes.month - 1]
    estacional = factor_estacional[mes.month]

    if ipc is None:
        continue

    external_rows.append({
        "fecha": mes.strftime("%Y-%m-%d"),
        "anio": anio,
        "mes": mes.month,
        "mes_nombre": mes.strftime("%B").capitalize(),
        "ipc_interanual_pct": round(ipc, 2),
        "euribor_12m_pct": round(euribor, 2),
        "factor_estacional": round(estacional, 2),
    })

df_external = pd.DataFrame(external_rows)
print(f"  -> {len(df_external)} filas generadas")

# ===========================================================================
# 2. CRM - CLIENTES, PROYECTOS Y PIPELINE
# ===========================================================================
# MODELO DE NEGOCIO DE BEEXPAND (coherente con 50+ empleados):
#   A) Retainers mensuales (70% del ingreso): ~35 clientes con contrato recurrente
#      Cada retainer: 3,000-10,000 EUR/mes, duracion 12-36 meses
#      Total: ~320,000 EUR/mes
#   B) Proyectos one-off (20%): ~40 clientes con proyectos de 15-60K EUR
#      Total: ~60,000 EUR/mes amortizado
#   C) Misiones comerciales (10%): ~25 misiones de 8-25K EUR
#      Total: ~30,000 EUR/mes amortizado
#   INGRESO MENSUAL TOTAL: ~400,000 EUR/mes (vs ~220K gastos = margen saludable)

print("\n[2/4] Generando CRM...")

sectores = [
    "Tecnologia",
    "Agroalimentario",
    "Bienes Industriales",
    "Vinos y Bebidas",
    "Turismo",
    "Bienes de Consumo",
]

# ============================================================
# 2A. CLIENTES RETAINER (ingreso recurrente mensual)
# ============================================================

retainer_names = [
    # Tecnologia
    ("InnovaTech Solutions SL",       "Tecnologia", 8_500),
    ("DataSmart Systems SA",          "Tecnologia", 10_200),
    ("CloudNet Espana SL",            "Tecnologia", 7_800),
    ("Nexus Software Group",          "Tecnologia", 9_500),
    ("CyberSecure Consulting",        "Tecnologia", 11_000),
    ("AppDigital Labs",               "Tecnologia", 6_000),
    ("BioTech Health SL",             "Tecnologia", 8_000),
    # Agroalimentario
    ("CampoVerde Export SA",          "Agroalimentario", 7_200),
    ("Alimentos del Sur SL",          "Agroalimentario", 9_000),
    ("Olivares del Mediterraneo",      "Agroalimentario", 6_500),
    ("Frutas y Hortalizas del Norte", "Agroalimentario", 8_500),
    ("Conservas Artesanas SL",        "Agroalimentario", 5_500),
    ("Aceites y Olivares SL",         "Agroalimentario", 10_000),
    ("Embotellados del Norte SL",     "Agroalimentario", 7_500),
    # Bienes Industriales
    ("InduSteel Components SA",       "Bienes Industriales", 12_500),
    ("Mecanica Precision SL",         "Bienes Industriales", 8_800),
    ("TecniMaquinaria SL",            "Bienes Industriales", 9_200),
    ("AutoParts Iberica SA",          "Bienes Industriales", 10_500),
    ("Construcciones Metalicas ML",   "Bienes Industriales", 7_000),
    ("ElecTech Sistemas SL",          "Bienes Industriales", 8_200),
    ("EnerRenovables Solar SA",        "Bienes Industriales", 9_800),
    ("Soluciones Logisticas ML",      "Bienes Industriales", 7_500),
    # Vinos y Bebidas
    ("Bodegas Montealto SA",          "Vinos y Bebidas", 8_000),
    ("Vinedos del Valle SL",          "Vinos y Bebidas", 6_000),
    ("Destilerias del Sur SL",        "Vinos y Bebidas", 7_800),
    ("Bodegas Solariego SA",          "Vinos y Bebidas", 9_500),
    ("Cervezas Artesanas Gredos",     "Vinos y Bebidas", 5_200),
    ("Gourmet Seleccion Espana",      "Vinos y Bebidas", 7_200),
    # Turismo
    ("Destinos Globales SL",          "Turismo", 10_000),
    ("HotelSun International SA",     "Turismo", 12_000),
    ("Turismo Rural Experience SL",   "Turismo", 7_000),
    ("Viajes y Negocios Globales",    "Turismo", 8_500),
    ("Eventos Corporativos Espana",   "Turismo", 6_500),
    # Bienes de Consumo
    ("ModaExport Iberica SL",         "Bienes de Consumo", 9_000),
    ("Hogar Diseno SL",               "Bienes de Consumo", 7_200),
    ("Cosmeticos Natural SL",         "Bienes de Consumo", 5_000),
    ("Juguetes del Mediterraneo",     "Bienes de Consumo", 7_500),
    ("Calzado Artesano Export SL",    "Bienes de Consumo", 6_000),
    ("Iluminacion Decorativa SL",     "Bienes de Consumo", 8_500),
    ("Textil Hogar Internacional",    "Bienes de Consumo", 7_000),
]

crm_rows = []
erp_income_rows = []

cliente_counter = 0
retainer_clients = []
project_clients = []

# --- Generar retainer clients ---
for i, (nombre, sector, cuota) in enumerate(retainer_names):
    cliente_counter += 1
    cliente_id = f"CLI-{cliente_counter:03d}"

    # Fecha de inicio del retainer (escalonada en el tiempo)
    # Los primeros comienzan en 2022/2023, los ultimos se incorporan mas tarde
    if i < 15:
        mes_inicio = MESES[np.random.randint(0, 6)]  # 2023, primeros meses
    elif i < 28:
        mes_inicio = MESES[np.random.randint(6, 18)]  # 2023-2024
    else:
        mes_inicio = MESES[np.random.randint(18, 30)]  # 2024-2025

    # Duracion: la mayoria siguen activos, algunos han terminado
    if np.random.random() < 0.75:  # 75% siguen activos
        meses_duracion = TOTAL_MESES - MESES.index(mes_inicio) + np.random.randint(0, 4)
        estado = "activo"
        fecha_fin = None
    else:
        meses_duracion = np.random.randint(6, 18)
        # Fecha fin = inicio + duracion
        idx_fin = min(MESES.index(mes_inicio) + meses_duracion, TOTAL_MESES - 1)
        fecha_fin = MESES[idx_fin]
        if fecha_fin > datetime.now():
            estado = "activo"
            fecha_fin = None
        else:
            estado = "finalizado"

    # Calcular meses activos para facturacion
    idx_inicio = MESES.index(mes_inicio)
    if fecha_fin:
        idx_fin = MESES.index(datetime(fecha_fin.year, fecha_fin.month, 1))
    else:
        idx_fin = TOTAL_MESES - 1

    # Registrar en CRM con proyecto tipo "Consultoria recurrente"
    valor_total_estimado = cuota * (idx_fin - idx_inicio + 1)

    crm_rows.append({
        "cliente_id": cliente_id,
        "empresa": nombre,
        "sector": sector,
        "tipo_proyecto": "Consultoria Internacional Recurrente",
        "valor_proyecto_eur": valor_total_estimado,
        "fecha_inicio": mes_inicio.strftime("%Y-%m-%d"),
        "duracion_meses": idx_fin - idx_inicio + 1,
        "estado": estado,
        "probabilidad_pct": 100 if estado == "activo" else 100,
        "fecha_cierre": fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "",
        "es_retainer": True,
        "cuota_mensual": cuota,
    })

    retainer_clients.append({
        "cliente_id": cliente_id,
        "nombre": nombre,
        "sector": sector,
        "cuota": cuota,
        "idx_inicio": idx_inicio,
        "idx_fin": idx_fin,
    })

    # Generar facturas mensuales del retainer
    for idx_mes in range(idx_inicio, idx_fin + 1):
        mes = MESES[idx_mes]

        # Ajuste estacional: la cuota se reduce en agosto y diciembre
        factor_cuota = factor_estacional[mes.month]
        # El factor estacional para retainer se suaviza (no desaparece)
        factor_cuota_retainer = max(0.6, min(1.1, factor_cuota))
        valor_mes = round(cuota * factor_cuota_retainer, -1)

        # Factura a final de mes
        dia = min(28, np.random.randint(25, 28))
        fecha_fac = datetime(mes.year, mes.month, dia)
        if fecha_fac > END:
            continue

        iva = round(valor_mes * 0.21, 2)
        total = valor_mes + iva

        # Pagado? si la fecha ya paso mas de 45 dias
        pagado = fecha_fac < datetime.now() - timedelta(days=45)

        mes_nombre = mes.strftime("%B").capitalize()
        erp_income_rows.append({
            "cliente_id": cliente_id,
            "cliente_nombre": nombre,
            "sector": sector,
            "tipo_ingreso": "retainer",
            "tipo_proyecto": "Consultoria Internacional Recurrente",
            "fecha_factura": fecha_fac.strftime("%Y-%m-%d"),
            "concepto": f"Retainer {mes_nombre} {mes.year} - {nombre}",
            "categoria": "ingreso",
            "base_imponible": valor_mes,
            "iva_21": iva,
            "total": total,
            "pagado": pagado,
        })


# ============================================================
# 2B. CLIENTES PROYECTO (one-off)
# ============================================================

tipos_proyecto = [
    "Plan de Promocion Internacional",
    "Mision Comercial",
    "Campana de Marketing Internacional",
    "Plan Integral de Internacionalizacion",
]

rangos_valor = {
    "Plan de Promocion Internacional":       (15_000, 35_000),
    "Mision Comercial":                       (12_000, 30_000),
    "Campana de Marketing Internacional":     (8_000,  22_000),
    "Plan Integral de Internacionalizacion":  (30_000, 60_000),
}

project_names = [
    ("NexaTech Devices SL",           "Tecnologia"),
    ("SmartAgro Solutions SA",        "Agroalimentario"),
    ("Maquinaria del Sur SL",         "Bienes Industriales"),
    ("Vinedos Solariegos SL",         "Vinos y Bebidas"),
    ("Travel Experience Group",       "Turismo"),
    ("Diseno y Hogar SA",             "Bienes de Consumo"),
    ("Sistemas Embebidos SA",         "Tecnologia"),
    ("Bioagro Export SL",             "Agroalimentario"),
    ("Componentes del Valles SL",     "Bienes Industriales"),
    ("Destileria Artesana SL",        "Vinos y Bebidas"),
    ("Hoteles con Encanto SL",        "Turismo"),
    ("Calzados Deportivos SL",        "Bienes de Consumo"),
    ("Cloud Infrastructure SL",       "Tecnologia"),
    ("Conservas del Atlantico SA",    "Agroalimentario"),
    ("Equipos Industriales ML",       "Bienes Industriales"),
    ("Bodegas del Duero SA",          "Vinos y Bebidas"),
    ("Turismo Activo SL",             "Turismo"),
    ("Muebles de Diseno SL",          "Bienes de Consumo"),
    ("RoboTech Solutions SL",         "Tecnologia"),
    ("Pescados y Mariscos del Norte", "Agroalimentario"),
    ("Talleres Mecanicos del Sur",    "Bienes Industriales"),
    ("Crianza y Venta SL",            "Vinos y Bebidas"),
    ("Resorts Vacacionales SA",       "Turismo"),
    ("Textil Moda Internacional",     "Bienes de Consumo"),
    ("DataCenter Solutions SA",       "Tecnologia"),
    ("Finca Ecologica SL",            "Agroalimentario"),
    ("Metalurgica Avanzada SA",       "Bienes Industriales"),
    ("Espirituosos Premium SL",       "Vinos y Bebidas"),
    ("Agencia de Viajes Global",      "Turismo"),
    ("Complementos de Moda SL",       "Bienes de Consumo"),
    ("Inteligencia Artificial Corp",  "Tecnologia"),
    ("Cultivos Hidroponicos SL",      "Agroalimentario"),
    ("Ingenieria Mecanica SL",        "Bienes Industriales"),
    ("Licores y Destilados SL",       "Vinos y Bebidas"),
    ("Agencia de Negocios Global",    "Turismo"),
    ("Bolsos y Accesorios SL",        "Bienes de Consumo"),
    ("AgriTech Internacional SA",     "Agroalimentario"),
    ("Movilidad Electrica SL",        "Bienes Industriales"),
]

for nombre, sector in project_names:
    cliente_counter += 1
    cliente_id = f"CLI-{cliente_counter:03d}"

    tipo = np.random.choice(tipos_proyecto, p=[0.30, 0.25, 0.25, 0.20])
    min_v, max_v = rangos_valor[tipo]
    valor = round(np.random.uniform(min_v, max_v), -2)

    idx_fecha = np.random.randint(0, len(MESES) - 6)
    fecha_inicio = MESES[idx_fecha]

    duracion_meses = {
        "Plan de Promocion Internacional": np.random.randint(3, 7),
        "Mision Comercial": np.random.randint(1, 3),
        "Campana de Marketing Internacional": np.random.randint(2, 5),
        "Plan Integral de Internacionalizacion": np.random.randint(6, 14),
    }[tipo]

    dias_desde_inicio = (datetime.now() - fecha_inicio).days
    if dias_desde_inicio > duracion_meses * 40:
        if np.random.random() > 0.10:  # 90% ganado
            estado = "ganado"
            probabilidad = 100
            fecha_cierre = fecha_inicio + timedelta(days=duracion_meses * 30)
        else:
            estado = "perdido"
            probabilidad = 0
            fecha_cierre = fecha_inicio + timedelta(days=duracion_meses * 15)
    elif dias_desde_inicio > 0:
        estado = "en_curso"
        probabilidad = np.random.randint(40, 90)
        fecha_cierre = None
    else:
        estado = "en_curso"
        probabilidad = np.random.randint(10, 40)
        fecha_cierre = None

    crm_rows.append({
        "cliente_id": cliente_id,
        "empresa": nombre,
        "sector": sector,
        "tipo_proyecto": tipo,
        "valor_proyecto_eur": valor,
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
        "duracion_meses": duracion_meses,
        "estado": estado,
        "probabilidad_pct": probabilidad,
        "fecha_cierre": fecha_cierre.strftime("%Y-%m-%d") if fecha_cierre else "",
        "es_retainer": False,
        "cuota_mensual": 0,
    })

    project_clients.append({
        "cliente_id": cliente_id,
        "nombre": nombre,
        "sector": sector,
        "tipo": tipo,
        "valor": valor,
        "estado": estado,
        "fecha_inicio": fecha_inicio,
        "duracion_meses": duracion_meses,
    })

    # Generar facturas del proyecto
    if estado in ("ganado", "en_curso"):
        # Numero de facturas segun tipo
        if tipo == "Mision Comercial":
            num_facturas = 1
        elif tipo == "Plan de Promocion Internacional":
            num_facturas = np.random.randint(2, duracion_meses)
        elif tipo == "Campana de Marketing Internacional":
            num_facturas = np.random.randint(1, min(4, duracion_meses + 1))
        else:  # Plan Integral
            num_facturas = np.random.randint(3, min(8, duracion_meses + 1))

        # Repartir el valor entre las facturas
        valores_facturas = []
        resto = valor
        for f in range(num_facturas - 1):
            parte = round(np.random.uniform(0.1, 0.4) * resto, -1)
            parte = max(500, min(parte, resto - 500))
            valores_facturas.append(parte)
            resto -= parte
        valores_facturas.append(round(resto, -1))

        # Fechas de las facturas (repartidas durante la duracion del proyecto)
        for f in range(num_facturas):
            fact_valor = valores_facturas[f]
            dia_factura = int(duracion_meses * 30 * (f + 1) / (num_facturas + 1))
            fecha_factura = fecha_inicio + timedelta(days=dia_factura)
            dia = min(28, max(1, np.random.randint(1, 28)))
            fecha_factura = datetime(fecha_factura.year, fecha_factura.month, dia)
            if fecha_factura > END:
                continue

            iva = round(fact_valor * 0.21, 2)
            total = fact_valor + iva
            pagado = fecha_factura < datetime.now() - timedelta(days=60)

            erp_income_rows.append({
                "cliente_id": cliente_id,
                "cliente_nombre": nombre,
                "sector": sector,
                "tipo_ingreso": "proyecto",
                "tipo_proyecto": tipo,
                "fecha_factura": fecha_factura.strftime("%Y-%m-%d"),
                "concepto": f"{tipo} - {nombre} - Factura {f+1}/{num_facturas}",
                "categoria": "ingreso",
                "base_imponible": fact_valor,
                "iva_21": iva,
                "total": total,
                "pagado": pagado,
            })

df_crm = pd.DataFrame(crm_rows)
print(f"  -> {len(df_crm)} registros en CRM")
print(f"     - Retainer: {len(retainer_clients)} clientes recurrentes")
print(f"     - Proyecto: {len(project_clients)} proyectos one-off")

# ===========================================================================
# 3. ERP - FACTURACION COMPLETA (INGRESOS + GASTOS)
# ===========================================================================

print("\n[3/4] Generando ERP...")

# --- Gastos fijos mensuales ---
gastos_fijos_mensuales = {
    "Nominas":               (170_000, 195_000),
    "Alquiler oficina":      (5_500, 6_500),
    "Suministros":           (800, 1_400),
    "Software y SaaS":       (4_000, 6_500),
    "Seguros":               (1_200, 1_800),
    "Servicios profesionales": (2_500, 4_500),
    "Material de oficina":   (400, 900),
}

# --- Gastos variables ---
gastos_variables = {
    "Viajes y dietas":              (3_000, 18_000),
    "Alquiler stands ferias":       (5_000, 25_000),
    "Marketing y publicidad":       (2_000, 10_000),
    "Traduccion y adaptacion":      (1_000, 6_000),
    "Logistica y envios":           (800, 5_000),
    "Asesoria legal local":         (1_500, 7_000),
    "Hosting y dominios":           (200, 800),
}

erp_expense_rows = []

for mes in MESES:
    # --- Gastos fijos cada mes ---
    for concepto, (min_g, max_g) in gastos_fijos_mensuales.items():
        if concepto == "Nominas":
            dia = np.random.randint(1, 5)
        else:
            dia = np.random.randint(10, 28)

        fecha_gasto = datetime(mes.year, mes.month, dia)
        if fecha_gasto > END:
            continue

        base = round(np.random.uniform(min_g, max_g), -1)
        if concepto == "Nominas":
            iva = 0
        else:
            iva = round(base * 0.21, 2)
        total = base + iva
        pagado = fecha_gasto < datetime.now() - timedelta(days=15)

        erp_expense_rows.append({
            "fecha_factura": fecha_gasto.strftime("%Y-%m-%d"),
            "concepto": concepto,
            "categoria": "gasto_fijo",
            "base_imponible": base,
            "iva_21": iva,
            "total": total,
            "pagado": pagado,
        })

    # --- Gastos variables segun actividad estacional ---
    factor_actividad = factor_estacional[mes.month]

    # Meses de ferias (mar, abr, oct): gasto extra seguro
    if mes.month in (3, 4, 10):
        concepto_extra = np.random.choice([
            "Viajes y dietas",
            "Alquiler stands ferias",
            "Marketing y publicidad",
        ])
        min_g, max_g = gastos_variables[concepto_extra]
        base = round(np.random.uniform(min_g, max_g) * factor_actividad, -1)
        iva = round(base * 0.21, 2)
        total = base + iva
        dia = np.random.randint(5, 25)
        fecha_gasto = datetime(mes.year, mes.month, dia)
        if fecha_gasto <= END:
            pagado = fecha_gasto < datetime.now() - timedelta(days=15)
            erp_expense_rows.append({
                "fecha_factura": fecha_gasto.strftime("%Y-%m-%d"),
                "concepto": concepto_extra,
                "categoria": "gasto_variable",
                "base_imponible": base,
                "iva_21": iva,
                "total": total,
                "pagado": pagado,
            })

    # Otros gastos variables aleatorios
    probabilidad_gasto = 0.5 * factor_actividad
    if np.random.random() < probabilidad_gasto:
        concepto_var = np.random.choice(list(gastos_variables.keys()))
        min_g, max_g = gastos_variables[concepto_var]
        base = round(np.random.uniform(min_g * 0.3, max_g * 0.5) * factor_actividad, -1)
        base = max(500, base)
        iva = round(base * 0.21, 2)
        total = base + iva
        dia = np.random.randint(5, 25)
        fecha_gasto = datetime(mes.year, mes.month, dia)
        if fecha_gasto <= END:
            pagado = fecha_gasto < datetime.now() - timedelta(days=15)
            erp_expense_rows.append({
                "fecha_factura": fecha_gasto.strftime("%Y-%m-%d"),
                "concepto": concepto_var,
                "categoria": "gasto_variable",
                "base_imponible": base,
                "iva_21": iva,
                "total": total,
                "pagado": pagado,
            })

    # --- Gastos trimestrales ---
    if mes.month in (4, 7, 10):
        base = round(np.random.uniform(25_000, 50_000), -1)
        iva = 0
        total = base
        dia = np.random.randint(15, 25)
        fecha_gasto = datetime(mes.year, mes.month, dia)
        if fecha_gasto <= END and fecha_gasto <= datetime.now():
            pagado = fecha_gasto < datetime.now() - timedelta(days=30)
            erp_expense_rows.append({
                "fecha_factura": fecha_gasto.strftime("%Y-%m-%d"),
                "concepto": "IVA Trimestral",
                "categoria": "gasto_trimestral",
                "base_imponible": base,
                "iva_21": iva,
                "total": total,
                "pagado": pagado,
            })

    if mes.month in (4, 10, 12):
        base = round(np.random.uniform(8_000, 18_000), -1)
        iva = 0
        total = base
        dia = np.random.randint(15, 25)
        fecha_gasto = datetime(mes.year, mes.month, dia)
        if fecha_gasto <= END and fecha_gasto <= datetime.now():
            pagado = fecha_gasto < datetime.now() - timedelta(days=30)
            erp_expense_rows.append({
                "fecha_factura": fecha_gasto.strftime("%Y-%m-%d"),
                "concepto": "Pago Fraccionado IS",
                "categoria": "gasto_trimestral",
                "base_imponible": base,
                "iva_21": iva,
                "total": total,
                "pagado": pagado,
            })

# Combinar ingresos y gastos
erp_all = erp_income_rows + erp_expense_rows
df_erp = pd.DataFrame(erp_all)

# Ordenar por fecha
df_erp["fecha_factura_dt"] = pd.to_datetime(df_erp["fecha_factura"])
df_erp = df_erp.sort_values("fecha_factura_dt").reset_index(drop=True)
df_erp = df_erp.drop(columns=["fecha_factura_dt"])

# Anadir ID secuencial
df_erp.insert(0, "factura_id", [f"FAC-{i+1:04d}" for i in range(len(df_erp))])

num_ingresos = len(erp_income_rows)
num_gastos_fijo = sum(1 for r in erp_expense_rows if r["categoria"] == "gasto_fijo")
num_gastos_var = sum(1 for r in erp_expense_rows if r["categoria"] == "gasto_variable")
num_gastos_trime = sum(1 for r in erp_expense_rows if r["categoria"] == "gasto_trimestral")

print(f"  -> {len(df_erp)} facturas totales")
print(f"     - Ingresos: {num_ingresos}")
print(f"     - Gastos fijos: {num_gastos_fijo}")
print(f"     - Gastos variables: {num_gastos_var}")
print(f"     - Gastos trimestrales: {num_gastos_trime}")

# ===========================================================================
# 4. BANK STATEMENTS - EXTRACTOS BANCARIOS
# ===========================================================================

print("\n[4/4] Generando extractos bancarios...")

bank_rows = []
saldo = 500_000  # Saldo inicial en Enero 2023 (colchon de tesoreria realista)

for mes in MESES:
    # Ingresos del mes: facturas de ingreso cuyo cobro estimado cae este mes
    ingresos_del_mes = 0
    ingresos_detalle = []

    for fac in erp_income_rows:
        fecha_fac = datetime.strptime(fac["fecha_factura"], "%Y-%m-%d")

        # Retainer se cobra a 15-30 dias
        # Proyecto se cobra a 30-60 dias
        if fac["tipo_ingreso"] == "retainer":
            dias_cobro = np.random.randint(15, 35)
        else:
            dias_cobro = np.random.randint(30, 65)

        fecha_cobro = fecha_fac + timedelta(days=dias_cobro)
        if fecha_cobro.year == mes.year and fecha_cobro.month == mes.month:
            ingresos_del_mes += fac["total"]
            ingresos_detalle.append({
                "concepto": f"Cobro: {fac['concepto'][:60]}",
                "importe": fac["total"],
            })

    # Gastos del mes: facturas de gasto cuyo pago estimado cae este mes
    gastos_del_mes = 0
    gastos_detalle = []

    for fac in erp_expense_rows:
        fecha_fac = datetime.strptime(fac["fecha_factura"], "%Y-%m-%d")

        if fac["concepto"] == "Nominas":
            # Nominas se pagan el mismo mes (entre dia 1-5)
            fecha_pago = datetime(fecha_fac.year, fecha_fac.month, min(5, fecha_fac.day + 2))
        elif fac["categoria"] == "gasto_trimestral":
            dias_pago = np.random.randint(1, 15)
            fecha_pago = fecha_fac + timedelta(days=dias_pago)
        else:
            dias_pago = np.random.randint(15, 50)
            fecha_pago = fecha_fac + timedelta(days=dias_pago)

        if fecha_pago.year == mes.year and fecha_pago.month == mes.month:
            gastos_del_mes += fac["total"]
            gastos_detalle.append({
                "concepto": f"Pago: {fac['concepto']}",
                "importe": fac["total"],
            })

    # Pequena variacion aleatoria para realismo (+-3%)
    ingresos_del_mes *= np.random.uniform(0.97, 1.03)
    gastos_del_mes *= np.random.uniform(0.98, 1.02)

    ingresos_del_mes = round(ingresos_del_mes, 2)
    gastos_del_mes = round(gastos_del_mes, 2)

    saldo_anterior = saldo
    saldo = saldo + ingresos_del_mes - gastos_del_mes

    # Si el saldo baja de -100K, activa poliza de credito
    if saldo < -100_000:
        ingreso_extra = round(np.random.uniform(150_000, 250_000), -2)
        ingresos_del_mes += ingreso_extra
        ingresos_detalle.append({
            "concepto": "Disposicion poliza de credito",
            "importe": ingreso_extra,
        })
        saldo = round(saldo + ingreso_extra, 2)

    saldo = round(saldo, 2)

    # Registrar los movimientos en el extracto bancario
    ultimo_dia = ultimo_dia_mes(mes)

    if ingresos_detalle:
        for ing in ingresos_detalle:
            dia = np.random.randint(1, min(29, ultimo_dia.day + 1))
            fecha_mov = datetime(mes.year, mes.month, dia)
            if fecha_mov > END:
                continue
            bank_rows.append({
                "fecha": fecha_mov.strftime("%Y-%m-%d"),
                "concepto": ing["concepto"],
                "tipo": "ingreso",
                "importe": round(ing["importe"], 2),
            })
    else:
        # Ingreso minimo si no hay cobros
        bank_rows.append({
            "fecha": f"{mes.year}-{mes.month:02d}-15",
            "concepto": "Ingresos varios del periodo",
            "tipo": "ingreso",
            "importe": round(np.random.uniform(1_000, 5_000), 2),
        })

    if gastos_detalle:
        for gas in gastos_detalle:
            dia = np.random.randint(1, min(29, ultimo_dia.day + 1))
            fecha_mov = datetime(mes.year, mes.month, dia)
            if fecha_mov > END:
                continue
            bank_rows.append({
                "fecha": fecha_mov.strftime("%Y-%m-%d"),
                "concepto": gas["concepto"],
                "tipo": "gasto",
                "importe": round(-gas["importe"], 2),
            })

# Ordenar por fecha
df_bank = pd.DataFrame(bank_rows)
df_bank["fecha_dt"] = pd.to_datetime(df_bank["fecha"])
df_bank = df_bank.sort_values(["fecha_dt", "tipo"]).reset_index(drop=True)
df_bank = df_bank.drop(columns=["fecha_dt"])

# Calcular saldo acumulado
saldo_acum = 500_000
saldos = []
for _, row in df_bank.iterrows():
    saldo_acum += row["importe"]
    saldos.append(round(saldo_acum, 2))
df_bank["saldo_acumulado"] = saldos

print(f"  -> {len(df_bank)} movimientos bancarios generados")
print(f"     Saldo inicial: 500,000.00 EUR")
print(f"     Saldo final:   {saldos[-1]:,.2f} EUR")

# ===========================================================================
# EXPORTAR A CSV
# ===========================================================================

print("\n" + "=" * 60)
print("EXPORTANDO ARCHIVOS CSV...")
print("=" * 60)

# 1. CRM
csv_crm = os.path.join(OUTPUT_DIR, "crm.csv")
df_crm = df_crm.drop(columns=["es_retainer", "cuota_mensual"])
df_crm.to_csv(csv_crm, index=False, encoding="utf-8-sig")
print(f"  OK crm.csv -> {len(df_crm)} registros")

# 2. ERP
csv_erp = os.path.join(OUTPUT_DIR, "erp.csv")
df_erp = df_erp.drop(columns=["tipo_ingreso"])
df_erp.to_csv(csv_erp, index=False, encoding="utf-8-sig")
print(f"  OK erp.csv -> {len(df_erp)} registros")

# 3. Bank Statements
csv_bank = os.path.join(OUTPUT_DIR, "bank_statements.csv")
df_bank.to_csv(csv_bank, index=False, encoding="utf-8-sig")
print(f"  OK bank_statements.csv -> {len(df_bank)} registros")

# 4. External Data
csv_ext = os.path.join(OUTPUT_DIR, "external_data.csv")
df_external.to_csv(csv_ext, index=False, encoding="utf-8-sig")
print(f"  OK external_data.csv -> {len(df_external)} registros")

# --- Resumen financiero ----------------------------------------------------
print("\n" + "=" * 60)
print("RESUMEN FINANCIERO (2023-2026)")
print("=" * 60)

ingresos_totales = df_erp[df_erp["categoria"] == "ingreso"]["total"].sum()
gastos_totales = df_erp[df_erp["categoria"] != "ingreso"]["total"].sum()

# Ingresos mensuales promedio
ingresos_por_mes = {}
for _, row in df_erp[df_erp["categoria"] == "ingreso"].iterrows():
    mes = row["fecha_factura"][:7]
    ingresos_por_mes[mes] = ingresos_por_mes.get(mes, 0) + row["total"]
ingresos_promedio = sum(ingresos_por_mes.values()) / max(len(ingresos_por_mes), 1)

# Gastos mensuales promedio
gastos_por_mes = {}
for _, row in df_erp[df_erp["categoria"] != "ingreso"].iterrows():
    mes = row["fecha_factura"][:7]
    gastos_por_mes[mes] = gastos_por_mes.get(mes, 0) + row["total"]
gastos_promedio = sum(gastos_por_mes.values()) / max(len(gastos_por_mes), 1)

print(f"\n  INGRESOS totales facturados:   {ingresos_totales:>12,.2f} EUR")
print(f"  GASTOS totales recibidos:      {gastos_totales:>12,.2f} EUR")
print(f"  MARGEN bruto total:            {ingresos_totales - gastos_totales:>12,.2f} EUR")
print(f"\n  Ingreso mensual promedio:       {ingresos_promedio:>12,.2f} EUR")
print(f"  Gasto mensual promedio:         {gastos_promedio:>12,.2f} EUR")
print(f"  Margen mensual promedio:        {ingresos_promedio - gastos_promedio:>12,.2f} EUR")
print(f"\n  Saldo final banco:             {saldos[-1]:>12,.2f} EUR")

print(f"\n[*] Archivos generados en: {OUTPUT_DIR}")
print("[*] Listos para usar en Power BI y el modelo de forecasting.")
