# BeExpand — Cash Flow Forecasting
## Guia completa del proyecto (Curso IA en Finanzas y Contabilidad)

---

## INDICE

1. [¿Que es este proyecto?](#1-que-es-este-proyecto)
2. [Estructura del repositorio](#2-estructura-del-repositorio)
3. [Que hemos hecho hasta ahora](#3-que-hemos-hecho-hasta-ahora)
4. [Los datos generados](#4-los-datos-generados)
5. [Pipeline completo del reto](#5-pipeline-completo-del-reto)
6. [Proximos pasos](#6-proximos-pasos)
7. [Comandos utiles](#7-comandos-utiles)
8. [Notas importantes](#8-notas-importantes)

---

## 1. ¿Que es este proyecto?

Proyecto de **Cash Flow Forecasting** para **BeExpand** (expansionempresas.com),
una asesoria de internacionalizacion con sede en Toledo y mas de 50 empleados.

**Objetivo del reto:** Construir un modelo de prevision de caja que integre datos
historicos (ERP, CRM, banco) y factores externos (IPC, Euribor, estacionalidad)
para predecir la posicion de tesoreria a 30/60/90 dias.

**Empresa:** BeExpand (https://expansionempresas.com)
- Asesoria y ejecucion en comercio exterior
- Servicios: planes de promocion internacional, misiones comerciales, ferias, marketing internacional
- Sectores: tecnologia, agroalimentario, bienes industriales, vinos y bebidas, turismo, bienes de consumo
- 50+ empleados
- Ubicacion: C/Dinamarca 4, Vivero de empresas, Toledo

---

## 2. Estructura del repositorio

```
be-expand-cashflow-forecast/
├── data/
│   ├── raw/                        # Datos fuente (generados)
│   │   ├── crm.csv                 # 78 clientes y proyectos
│   │   ├── erp.csv                 # 1.434 facturas (ingresos + gastos)
│   │   ├── bank_statements.csv     # 1.376 movimientos bancarios
│   │   └── external_data.csv       # 40 meses IPC, Euribor, estacionalidad
│   └── processed/                  # Datos limpios para el modelo
│       ├── .gitkeep
│       └── be_expand_consolidado.csv  # (se genera al ejecutar el notebook)
├── notebooks/
│   └── 01_transformacion.ipynb     # Paso 2: Limpieza y transformacion
├── dashboard/                      # Capturas de Power BI (pendiente)
├── docs/                           # Documento de insights (pendiente)
├── data_generator.py               # Script que genera los 4 CSVs
├── .gitignore
└── README.md
```

---

## 3. Que hemos hecho hasta ahora

### Paso 1: Creacion del repositorio y datos (COMPLETADO)

1. Analizamos la pagina web de BeExpand para entender el negocio
2. Disenamos un modelo de datos coherente:
   - 40 clientes con contrato recurrente (retainer) de 5.000 a 12.500 EUR/mes
   - 38 proyectos one-off de 8.000 a 60.000 EUR
   - Gastos operativos realistas para 50+ empleados (~225.000 EUR/mes)
3. Creamos `data_generator.py` que genera los 4 CSV con semilla fija (42)
4. Los datos son coherentes entre si (CRM -> ERP -> Banco)
5. Verificamos que la empresa es rentable: ~273K ingresos vs ~225K gastos por mes

### Paso 2: Transformacion de datos (COMPLETADO)

1. Notebook `01_transformacion.ipynb` con 28 celdas
2. Carga y exploracion de los 4 datasets
3. Clasificacion automatica de transacciones:
   - Ingresos: recurrentes (retainers) vs proyectos
   - Gastos: Personal, Estructura, Tecnologia, Viajes y Ferias, Marketing, Tributario...
   - Movimientos bancarios por naturaleza
4. Deteccion de anomalias:
   - Z-score en facturas de ingreso y gasto
   - IQR en saldos bancarios mensuales
   - Graficos de visualizacion
5. Consolidacion en dataset unico mensual:
   - `data/processed/be_expand_consolidado.csv`
   - Con metricas derivadas: cash flow neto, ratio cobertura, variacion saldo
   - Incluye datos externos (IPC, Euribor, estacionalidad)

---

## 4. Los datos generados

### Resumen financiero (2023-2026)

| Concepto | Valor |
|----------|-------|
| Ingresos totales facturados | 10.941.122,50 EUR |
| Gastos totales recibidos | 8.987.404,80 EUR |
| Margen bruto total | +1.953.717,70 EUR |
| Ingreso mensual promedio | 273.528 EUR/mes |
| Gasto mensual promedio | 224.685 EUR/mes |
| Margen mensual promedio | +48.843 EUR/mes |
| Saldo bancario inicial | 500.000 EUR |
| Saldo bancario final | ~2.600.000 EUR |

### Archivos CSV

**crm.csv** (78 registros):
- cliente_id, empresa, sector, tipo_proyecto, valor_proyecto_eur, fecha_inicio, duracion_meses, estado, probabilidad_pct, fecha_cierre

**erp.csv** (1.434 registros):
- factura_id, cliente_id, cliente_nombre, sector, tipo_proyecto, fecha_factura, concepto, categoria, base_imponible, iva_21, total, pagado

**bank_statements.csv** (1.376 registros):
- fecha, concepto, tipo, importe, saldo_acumulado

**external_data.csv** (40 registros):
- fecha, anio, mes, mes_nombre, ipc_interanual_pct, euribor_12m_pct, factor_estacional

### Dataset consolidado (output del notebook):
- Columnas: anio_mes, recurrente, proyecto, total_ingresos, [grupos_gasto...], total_gastos, saldo_cierre_mes, ipc, euribor, estacionalidad, cash_flow_neto, ratio_cobertura, variacion_saldo

---

## 5. Pipeline completo del reto

```
[PASO 1]                         [PASO 2]                         [PASO 3]
EXTRACCION                       TRANSFORMACION                   MODELADO
                              ╔══════════════════════════╗     ╔════════════════╗
ERP ────────────────────────→  ║                          ║     ║                ║
CRM ────────────────────────→  ║  Python (Pandas) + IA    ║     ║  Prophet /     ║
Banco ──────────────────────→  ║  para:                   ║ ──→║  LSTM          ║
Datos Externos ─────────────→  ║  - Clasificacion         ║     ║  (Forecasting  ║
                              ║  - Deteccion anomalias    ║     ║   a 90 dias)   ║
                              ║  - Normalizacion          ║     ║                ║
                              ╚══════════════════════════╝     ╚════════════════╝
                                          │                              │
                                          ▼                              ▼
                                   be_expand_consolidado.csv      Modelo entrenado
                                                                           
[PASO 4]                         [PASO 5]
VISUALIZACION                    ACCION
╔══════════════════════════╗     ╔══════════════════════════════════╗
║  Power BI + Copilot      ║     ║  Alerta automatica:             ║
║  - Dashboard forecast    ║     ║  "La caja caera por debajo      ║
║  - Smart Narratives      ║     ║   del umbral en 45 dias.        ║
║  - Alertas               ║     ║   Recomendacion: Activar        ║
╚══════════════════════════╝     ║   linea de credito."            ║
                                 ╚══════════════════════════════════╝
```

---

## 6. Proximos pasos

### Pendiente de hacer (POR ORDEN):

#### PASO 3: Modelo de Forecasting (30% de la nota)
Crear un notebook `02_modelo_forecasting.ipynb` que:

1. Cargue `data/processed/be_expand_consolidado.csv`
2. Divida en train/test (80/20)
3. Entrene Prophet y/o LSTM
4. Prediga la posicion de tesoreria a 30/60/90 dias
5. Evalue el modelo (MAE, RMSE, MAPE)
6. Visualice predicciones vs reales
7. Guarde el modelo entrenado

**Librerias necesarias:** `pip install prophet scikit-learn tensorflow` (opcional LSTM)

#### PASO 4: Dashboard Power BI (20% de la nota)
1. Conectar Power BI a `be_expand_consolidado.csv`
2. Crear dashboard con forecast a 30/60/90 dias
3. Anadir segmentadores por periodo y tipo
4. Generar Smart Narrative con Copilot
5. Capturar pantalla del dashboard

#### PASO 5: Documento de insights (10% de la nota)
1. Resumen ejecutivo de una pagina
2. Principales hallazgos del modelo
3. Recomendaciones para BeExpand

#### PASO EXTRA: Alertas con Make
1. Integrar con Make (antes Integromat)
2. Enviar alerta a Slack cuando la caja caiga de un umbral

### Entregables del reto (resumen de la rubrica):

| Entregable | % | Estado |
|------------|---|--------|
| Extraccion de datos | 20% | COMPLETADO |
| Notebook con modelo forecasting | 30% | PENDIENTE |
| Deteccion de anomalias | 20% | COMPLETADO |
| Dashboard Power BI | 20% | PENDIENTE |
| Smart Narratives | 10% | PENDIENTE |

---

## 7. Comandos utiles

### Para continuar en casa

```bash
# 1. Clonar el repositorio
git clone https://github.com/AlexSV97/be-expand-cashflow-forecast.git
cd be-expand-cashflow-forecast

# 2. (Opcional) Crear y activar entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install pandas numpy matplotlib seaborn scipy jupyter

# Para el modelo de forecasting:
pip install prophet scikit-learn

# Opcional para LSTM:
pip install tensorflow

# 4. Arrancar Jupyter
jupyter notebook
# o
jupyter lab
```

### Para regenerar los datos desde cero (si hace falta)
```bash
python data_generator.py
```

### Para subir cambios a GitHub
```bash
git add .
git commit -m "feat: descripcion del cambio"
git push
```

### Para ver el repositorio en GitHub
```
https://github.com/AlexSV97/be-expand-cashflow-forecast
```

---

## 8. Notas importantes

### Sobre los datos
- Los datos son **100% ficticios**, creados para el curso
- Usan semilla fija (42) -> son reproducibles
- Los 4 CSV estan **relacionados entre si** (CRM genera facturas en ERP, que generan movimientos en Banco)
- Los valores son **coherentes** con una empresa de 50+ empleados del sector

### Sobre el notebook de transformacion
- Todas las celdas son independientes (se pueden ejecutar de arriba a abajo)
- El notebook carga los datos desde `../data/raw/` (relativo a la carpeta notebooks/)
- Al final genera `../data/processed/be_expand_consolidado.csv`

### Sobre el entorno
- Python 3.12+
- Se recomienda entorno virtual (venv)
- Jupyter Notebook o Jupyter Lab

### Creditos
- Curso: IA en Finanzas y Contabilidad
- Alumno: AlexSV97
- Fecha: Mayo 2026
