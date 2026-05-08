# BeExpand — Cash Flow Forecasting

Modelo de prevision de caja (Cash Flow Forecasting) para **BeExpand**, asesoria de internacionalizacion con sede en Toledo y mas de 50 empleados.

## Objetivo

Construir un modelo de ML que integre datos historicos, datos del CRM y factores externos para predecir la posicion de tesoreria a 90 dias.

## Pipeline

```
ERP + CRM + Banco + Externos
        -> Python (Pandas + IA)
        -> Modelo (Regresion + LSTM)
        -> Dashboard Power BI (forecast 30/60/90 dias)
        -> Alertas automaticas (Slack/Teams)
```

## Datos

Los datasets en `data/raw/` son ficticios pero coherentes, generados para el curso "IA en Finanzas y Contabilidad":

| Archivo | Registros | Descripcion |
|---------|-----------|-------------|
| `crm.csv` | 78 | Clientes, proyectos y pipeline (40 retainers + 38 one-off) |
| `erp.csv` | 1.434 | Facturas emitidas (ingresos) y recibidas (gastos) |
| `bank_statements.csv` | 1.376 | Extractos bancarios con saldo acumulado |
| `external_data.csv` | 40 | IPC, Euribor 12m, factor estacional (2023-2026) |

## Estructura del proyecto

```
be-expand-cashflow-forecast/
├── data/
│   ├── raw/           # Datos fuente (CSV)
│   └── processed/     # Datos limpios para el modelo
├── notebooks/         # Notebook de Python con el modelo
├── dashboard/         # Capturas del dashboard Power BI
├── docs/              # Documento de insights
├── data_generator.py  # Script generador de datos
└── README.md
```

## Tecnologias

- Python (Pandas, NumPy, Prophet/LSTM)
- Power BI + Copilot
- GitHub

## Entregables del reto

1. Notebook de Python con el modelo de forecasting
2. Dataset utilizado (CSV)
3. Captura del dashboard de Power BI con el forecast
4. Captura del Smart Narrative generado por Copilot
5. Documento de 1 pagina con los insights clave del modelo
