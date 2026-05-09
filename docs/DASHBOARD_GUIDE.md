# BeExpand — Dashboard Power BI
## Paso 4: Visualizacion del Cash Flow Forecast

---

## INDICE

1. [Requisitos](#1-requisitos)
2. [Estructura de datos](#2-estructura-de-datos)
3. [Carga de datos en Power BI](#3-carga-de-datos-en-power-bi)
4. [Modelo de datos](#4-modelo-de-datos)
5. [Pagina 1: Resumen Ejecutivo](#5-pagina-1-resumen-ejecutivo)
6. [Pagina 2: Forecast a 30/60/90](#6-pagina-2-forecast-a-306090)
7. [Pagina 3: Analisis Detallado](#7-pagina-3-analisis-detallado)
8. [Medidas DAX](#8-medidas-dax)
9. [Smart Narratives con Copilot](#9-smart-narratives-con-copilot)
10. [Formato y estilo](#10-formato-y-estilo)
11. [Exportar y compartir](#11-exportar-y-compartir)

---

## 1. Requisitos

- **Power BI Desktop** (gratuito): [descargar](https://powerbi.microsoft.com/desktop/)
- **Archivos de datos** (ya generados):
  - `data/processed/be_expand_consolidado.csv` — 40 meses historicos
  - `data/processed/predicciones.csv` — Historicos + predicciones a 3 meses

> Si no tienes Power BI Desktop instalado, descargalo e instalalo antes de continuar.

---

## 2. Estructura de datos

### be_expand_consolidado.csv (tabla hechos historicos)

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `anio_mes` | Fecha (Periodo) | Mes de la serie (ej. 2023-01) |
| `recurrente` | Numero | Ingresos por retainers |
| `proyecto` | Numero | Ingresos por proyectos one-off |
| `total_ingresos` | Numero | Suma ingresos del mes |
| `Estructura`, `Marketing`, ... | Numero | Gastos por categoria |
| `total_gastos` | Numero | Suma gastos del mes |
| `saldo_cierre_mes` | Numero | **Target**: posicion de tesoreria |
| `ipc_interanual_pct` | Numero | IPC interanual (%) |
| `euribor_12m_pct` | Numero | Euribor 12 meses (%) |
| `factor_estacional` | Numero | Estacionalidad (0.5 - 1.2) |
| `cash_flow_neto` | Numero | Ingresos - Gastos |
| `ratio_cobertura` | Porcentaje | (Ingresos/Gastos)*100 |
| `variacion_saldo` | Numero | Diferencia saldo respecto mes anterior |

### predicciones.csv (tabla hechos + forecast)

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `fecha` | Fecha | Dia 1 de cada mes |
| `saldo_real` | Numero | Saldo real (si existe) |
| `ingresos` | Numero | Ingresos reales (si existen) |
| `gastos` | Numero | Gastos reales (si existen) |
| `tipo` | Texto | "historico" o "prediccion" |
| `saldo_predicho` | Numero | Prediccion del modelo |
| `ic_inferior` | Numero | Intervalo confianza inferior (95%) |
| `ic_superior` | Numero | Intervalo confianza superior (95%) |

---

## 3. Carga de datos en Power BI

### Paso 3.1: Obtener datos

1. Abre **Power BI Desktop**
2. Ve a **Inicio > Obtener datos > Texto/CSV**
3. Selecciona `data/processed/be_expand_consolidado.csv`
4. En la ventana de preview, asegurate de que:
   - `anio_mes` se detecte como **Fecha** (o texto)
   - Las columnas numericas se detecten como **Numero decimal**
5. Haz clic en **Cargar**

6. Repite: **Inicio > Obtener datos > Texto/CSV**
7. Selecciona `data/processed/predicciones.csv`
8. Asegurate de que `fecha` se detecte como **Fecha**
9. Haz clic en **Cargar**

### Paso 3.2: Crear tabla calendario (IMPORTANTE)

Power BI necesita una tabla de fechas para las funciones de inteligencia de tiempo.

Ve a **Modelado > Nueva tabla** y pega:

```
Calendario = 
CALENDAR(
    DATE(2023, 1, 1),
    DATE(2026, 7, 1)
)
```

Luego anade estas columnas calculadas:

```
Anio = YEAR(Calendario[Date])

Mes = FORMAT(Calendario[Date], "MMMM")

MesNumero = MONTH(Calendario[Date])

Trimestre = "T" & FORMAT(Calendario[Date], "Q")

AnioMes = FORMAT(Calendario[Date], "YYYY-MM")
```

---

## 4. Modelo de datos

### Paso 4.1: Establecer relaciones

Ve a la pestaña **Modelo** (icono de diagrama a la izquierda) y crea estas relaciones:

| Tabla 1 | Tabla 2 | Columna | Cardinalidad |
|---------|---------|---------|--------------|
| `Calendario` | `be_expand_consolidado` | Calendario[Date] → be_expand_consolidado[anio_mes] | 1:N |
| `Calendario` | `predicciones` | Calendario[Date] → predicciones[fecha] | 1:N |

**IMPORTANTE**: La columna `anio_mes` en `be_expand_consolidado` esta en formato "YYYY-MM". Puede que necesites crear una columna de fecha en esa tabla para la relacion:

En Power Query (Editor avanzado), selecciona `be_expand_consolidado` y anade una columna personalizada:
```
= #date(Number.FromText(Text.Start([anio_mes], 4)), Number.FromText(Text.Mid([anio_mes], 5, 2)), 1)
```

O alternativamente, crea una columna calculada en la tabla:

```
Fecha = DATE(LEFT(be_expand_consolidado[anio_mes], 4), MID(be_expand_consolidado[anio_mes], 6, 2), 1)
```

### Paso 4.2: Marcar tabla como fecha

En el panel **Campos**, selecciona la tabla `Calendario` y ve a **Herramientas de tabla > Marcar como tabla de fechas**.

---

## 5. Pagina 1: Resumen Ejecutivo

Esta pagina da una vision general rapida de la salud financiera.

### Layout propuesto:

```
+--------------------------------------------------+
|  BEEXPAND - CASH FLOW FORECAST     [Filtros]     |
+--------------------------------------------------+
| [KPI]       | [KPI]        | [KPI]        | [KPI]|
| Saldo Actual| Ingreso Med  | Gasto Med    | Dias |
| 2,600,097   | 273,528/mes  | 224,685/mes  | Cober|
+--------------------------------------------------+
|                                                    |
|  [Line Chart: Saldo Bancario Historico + Forecast] |
|                                                    |
+--------------------------------------------------+
| [Bar Chart: Ingresos vs Gastos por Mes]           |
|                                                    |
+--------------------------------------------------+
```

### Visuales a anadir:

#### KPI 1 — Saldo Actual
- **Tipo**: Tarjeta (Card)
- **Valor**: `LASTNONBLANK(be_expand_consolidado[saldo_cierre_mes], ...)` o crea medida:
  ```
  Saldo Actual = 
  VAR UltimoMes = MAX(be_expand_consolidado[anio_mes])
  RETURN CALCULATE(SUM(be_expand_consolidado[saldo_cierre_mes]), be_expand_consolidado[anio_mes] = UltimoMes)
  ```
- **Formato**: "#,###,### EUR"

#### KPI 2 — Ingreso Promedio Mensual
- **Tipo**: Tarjeta
- **Medida**:
  ```
  Ingreso Promedio = AVERAGE(be_expand_consolidado[total_ingresos])
  ```
- **Formato**: "#,### EUR/mes"

#### KPI 3 — Gasto Promedio Mensual
- **Tipo**: Tarjeta
- **Medida**:
  ```
  Gasto Promedio = AVERAGE(be_expand_consolidado[total_gastos])
  ```
- **Formato**: "#,### EUR/mes"

#### KPI 4 — Ratio de Cobertura
- **Tipo**: Tarjeta
- **Medida**:
  ```
  Ratio Cobertura = 
  DIVIDE(
      AVERAGE(be_expand_consolidado[total_ingresos]),
      AVERAGE(be_expand_consolidado[total_gastos])
  ) * 100
  ```
- **Formato**: "0.0%"

#### Grafico 1 — Evolucion del Saldo Bancario
- **Tipo**: Grafico de lineas (Line chart)
- **Eje X**: Calendario[Date]
- **Valores**: `be_expand_consolidado[saldo_cierre_mes]` (linea azul)
- **Valores (linea 2)**: `predicciones[saldo_predicho]` (linea roja discontinua)
- **Valores (banda)**: `predicciones[ic_inferior]` + `predicciones[ic_superior]` como banda de sombreado
- **Eje Y**: Miles EUR (formato "#,###K")

Para la banda de confianza, usa el visual **Line and clustered column chart** o anade dos lineas adicionales con formato de area.

#### Grafico 2 — Ingresos vs Gastos
- **Tipo**: Grafico de columnas agrupadas
- **Eje X**: Calendario[Date]
- **Columnas**: `be_expand_consolidado[total_ingresos]` (verde) y `be_expand_consolidado[total_gastos]` (rojo)

#### Segmentadores (Slicers):
- **Periodo**: Basado en Calendario[Date], tipo "Between" (rango de fechas)
- **Tipo**: (Opcional) Segmentador para filtrar entre historico/prediccion

---

## 6. Pagina 2: Forecast a 30/60/90

### Layout propuesto:

```
+--------------------------------------------------+
|  FORECAST A 30/60/90 DIAS          [Filtros]     |
+--------------------------------------------------+
| [30 DIAS]     | [60 DIAS]      | [90 DIAS]       |
| Saldo:        | Saldo:         | Saldo:          |
| 4,170,855 EUR | 3,375,884 EUR  | 2,541,214 EUR   |
| IC: 4.1M-4.2M | IC: 3.2M-3.4M | IC: 2.4M-2.6M  |
+--------------------------------------------------+
|                                                    |
|  [Waterfall / Line Chart: Forecast Timeline]       |
|                                                    |
+--------------------------------------------------+
| [Tabla: Detalle del Forecast]                      |
+--------------------------------------------------+
| [Indicador de Riesgo]                             |
+--------------------------------------------------+
```

### Visuales:

#### 3 Tarjetas de Prediccion (30/60/90 dias)

Crea medidas DAX para cada horizonte:

```
Prediccion 30d = 
VAR Fecha30d = DATE(2026, 5, 1)
RETURN CALCULATE(MAX(predicciones[saldo_predicho]), predicciones[fecha] = Fecha30d)
```

```
Prediccion 60d = 
VAR Fecha60d = DATE(2026, 6, 1)
RETURN CALCULATE(MAX(predicciones[saldo_predicho]), predicciones[fecha] = Fecha60d)
```

```
Prediccion 90d = 
VAR Fecha90d = DATE(2026, 7, 1)
RETURN CALCULATE(MAX(predicciones[saldo_predicho]), predicciones[fecha] = Fecha90d)
```

Para las tarjetas, usa el visual **Card** con formato condicional:
- Si la prediccion > saldo actual → flecha verde
- Si la prediccion < saldo actual → flecha roja

#### Grafico de Forecast Timeline
- **Tipo**: Combinado (lineas + area)
- **Eje X**: predicciones[fecha]
- **Linea**: predicciones[saldo_predicho] (roja discontinua, ancho 3)
- **Area**: IC inferior a IC superior (sombreado gris claro)
- **Puntos**: Solo mostrar los 3 meses de prediccion

#### Tabla de Detalle
- **Tipo**: Tabla
- **Columnas**: Mes, Saldo Real, Prediccion, IC Inferior, IC Superior, Variacion
- Formato condicional en la columna Variacion

#### Indicador de Riesgo
- **Tipo**: Gauge visual o KPI
- **Valor**: `MIN(predicciones[ic_inferior])` (el peor escenario)
- **Objetivo**: 200,000 EUR (umbral de alerta)
- **Target**: 100,000 EUR (umbral critico)

---

## 7. Pagina 3: Analisis Detallado

### Layout propuesto:

```
+--------------------------------------------------+
|  ANALISIS DETALLADO               [Filtros]      |
+--------------------------------------------------+
| [Slicer: Mes]  | [Slicer: Categoria Gasto]       |
+--------------------------------------------------+
|                                                    |
|  [Stacked Bar: Gasto por Categoria]               |
|                                                    |
+--------------------------------------------------+
| [Scatter: Ingreso vs Gasto por Mes]               |
|                                                    |
+--------------------------------------------------+
| [Tabla: Datos Consolidados]                       |
+--------------------------------------------------+
```

### Visuales:

#### Desglose de Gastos por Categoria
- **Tipo**: Grafico de barras apiladas 100%
- **Eje X**: Calendario[Date]
- **Valores**: Todas las columnas de gasto (Estructura, Marketing, Personal, etc.)
- Activa opcion "Mostrar como tabla" para ver porcentajes

#### Dispersion Ingreso vs Gasto
- **Tipo**: Grafico de dispersion (Scatter)
- **Eje X**: `be_expand_consolidado[total_ingresos]`
- **Eje Y**: `be_expand_consolidado[total_gastos]`
- **Detalles**: Calendario[Anio]
- **Leyenda**: Anadir linea de referencia 45° (y=x) para ver meses con superavit/deficit

#### Tabla Consolidada
- **Tipo**: Tabla o Matrix
- **Filas**: Calendario[Date]
- **Valores**: Ingresos, Gastos, Cash Flow Neto, Saldo, Ratio Cobertura, IPC, Euribor

---

## 8. Medidas DAX

Aqui tienes todas las medidas DAX necesarias copiables directamente.

### Medidas basicas

```
Saldo Actual = 
VAR UltimoMes = MAX(be_expand_consolidado[anio_mes])
RETURN CALCULATE(SUM(be_expand_consolidado[saldo_cierre_mes]), be_expand_consolidado[anio_mes] = UltimoMes)
```

```
Saldo Promedio = AVERAGE(be_expand_consolidado[saldo_cierre_mes])
```

```
Saldo Minimo = MIN(be_expand_consolidado[saldo_cierre_mes])
```

```
Saldo Maximo = MAX(be_expand_consolidado[saldo_cierre_mes])
```

```
Ingreso Total = SUM(be_expand_consolidado[total_ingresos])
```

```
Gasto Total = SUM(be_expand_consolidado[total_gastos])
```

```
Cash Flow Neto Promedio = AVERAGE(be_expand_consolidado[cash_flow_neto])
```

### Medidas de forecast

```
Prediccion 30d = 
VAR Fecha30d = DATE(2026, 5, 1)
RETURN CALCULATE(MAX(predicciones[saldo_predicho]), predicciones[fecha] = Fecha30d)
```

```
Prediccion 60d = 
VAR Fecha60d = DATE(2026, 6, 1)
RETURN CALCULATE(MAX(predicciones[saldo_predicho]), predicciones[fecha] = Fecha60d)
```

```
Prediccion 90d = 
VAR Fecha90d = DATE(2026, 7, 1)
RETURN CALCULATE(MAX(predicciones[saldo_predicho]), predicciones[fecha] = Fecha90d)
```

```
IC Inferior 30d = 
CALCULATE(MAX(predicciones[ic_inferior]), predicciones[fecha] = DATE(2026, 5, 1))
```

```
IC Superior 30d = 
CALCULATE(MAX(predicciones[ic_superior]), predicciones[fecha] = DATE(2026, 5, 1))
```

```
Variacion Forecast = 
VAR Actual = [Saldo Actual]
VAR Predicho = [Prediccion 30d]
RETURN DIVIDE(Predicho - Actual, Actual) * 100
```

### Medidas de riesgo

```
Umbral Alerta = 200000
```

```
Umbral Critico = 100000
```

```
Estado Riesgo = 
VAR PeorCaso = MIN(predicciones[ic_inferior])
RETURN SWITCH(
    TRUE(),
    PeorCaso < 100000, "CRITICO - Activar linea de credito",
    PeorCaso < 200000, "ALERTA - Revisar calendario de cobros",
    "NORMAL - Tesoreria saludable"
)
```

```
Dias Cobertura = 
VAR GastoDiario = AVERAGE(be_expand_consolidado[total_gastos]) / 30
RETURN DIVIDE([Saldo Actual], GastoDiario)
```

### Medidas de tendencia

```
Tendencia Ingresos (3m) = 
CALCULATE(
    AVERAGE(be_expand_consolidado[total_ingresos]),
    DATESINPERIOD(Calendario[Date], LASTDATE(Calendario[Date]), -3, MONTH)
)
```

```
Tendencia Gastos (3m) = 
CALCULATE(
    AVERAGE(be_expand_consolidado[total_gastos]),
    DATESINPERIOD(Calendario[Date], LASTDATE(Calendario[Date]), -3, MONTH)
)
```

---

## 9. Smart Narratives con Copilot

Power BI Copilot puede generar resumenes automaticos. Para activarlo:

### Paso 9.1: Habilitar Copilot
1. En Power BI Desktop, ve a la pestaña **Vista > Panel de Copilot**
2. Si no aparece, asegurate de tener la ultima version de Power BI Desktop

### Paso 9.2: Anadir visual Smart Narrative
1. En cualquier pagina, haz clic en **Insertar > Smart Narrative** (o busca "Narrativa inteligente")
2. Se generara automaticamente un resumen basado en los visuales de la pagina

### Paso 9.3: Personalizar la narrativa
Puedes editar el texto generado para que diga algo como:

> **Resumen Ejecutivo - BeExpand**
> 
> A fecha de Abril 2026, la posicion de tesoreria es de **2,6M EUR**, con una tendencia claramente alcista desde mediados de 2024. El ingreso mensual promedio es de **273,528 EUR** frente a gastos de **224,685 EUR**, generando un margen mensual de **+48,843 EUR** (ratio de cobertura del 121%).
> 
> El modelo Prophet proyecta una posicion de **4,17M EUR a 30 dias**, aunque se espera un descenso estacional a **2,54M EUR a 90 dias** (Julio 2026). En el peor escenario (IC inferior), la tesoreria se mantiene siempre por encima de 2,4M EUR, muy por encima del umbral critico de 100K EUR.
> 
> **Recomendacion:** No se requiere accion urgente. La tesoreria se mantiene en niveles saludables para los proximos 90 dias.

### Paso 9.4: Anadir insights automaticos
1. Haz clic derecho en cualquier grafico de lineas
2. Selecciona **Analytics > Find anomalies** (si esta disponible en tu version)
3. Power BI resaltara automaticamente puntos anomalos en la serie

---

## 10. Formato y estilo

### Tema de colores recomendado

| Elemento | Color | Hex |
|----------|-------|-----|
| Fondo del informe | Gris muy claro | #F8F9FA |
| Fondo de tarjeta | Blanco | #FFFFFF |
| Titulos | Azul corporativo | #1B2A4A |
| Ingresos | Verde | #2ECC71 |
| Gastos | Rojo | #E74C3C |
| Saldo/Linea | Azul | #3498DB |
| Prediccion | Rojo oscuro | #E74C3C |
| Alerta | Naranja | #F39C12 |
| Critico | Rojo | #E74C3C |

### Formato de numeros

| Tipo | Formato |
|------|---------|
| Saldos | #,###,##0 EUR |
| Predicciones | #,###,##0 EUR |
| Porcentajes | 0.0% |
| Ratios | 0.0x |
| Miles (graficos) | #,##0,K |

### Logotipo
- Descarga el logo de BeExpand desde https://expansionempresas.com
- Insertalo en la esquina superior izquierda de cada pagina

---

## 11. Exportar y compartir

### Paso 11.1: Guardar el archivo
1. **Archivo > Guardar como** → `dashboard/be_expand_forecast.pbix`

### Paso 11.2: Capturar pantalla (para la rubrica)
1. Ve a cada pagina del dashboard
2. Presiona `Windows + Shift + S` (Recorte y anotaciones)
3. Selecciona la ventana de Power BI
4. Guarda cada captura como:
   - `dashboard/captura_resumen.png`
   - `dashboard/captura_forecast.png`
   - `dashboard/captura_detalle.png`

### Paso 11.3: Publicar en Power BI Service (opcional)
1. Haz clic en **Publicar** en la cinta de opciones
2. Selecciona tu espacio de trabajo
3. Comparte el enlace con tu profesor o equipo

### Paso 11.4: Checklist de entregables
- [ ] Dashboard con 3 paginas (Resumen, Forecast, Detalle)
- [ ] KPIs en la pagina principal
- [ ] Grafico de forecast a 30/60/90 dias con intervalos de confianza
- [ ] Segmentadores de fecha y tipo
- [ ] Smart Narrative generada con Copilot
- [ ] Capturas de pantalla en `dashboard/`
- [ ] Archivo .pbix guardado en `dashboard/`

---

## Checklist de validacion (para la rubrica)

| Criterio | % | Hecho |
|----------|---|-------|
| Conectar Power BI a los datos | 5% | ☐ |
| Dashboard con forecast 30/60/90 | 7% | ☐ |
| Segmentadores por periodo y tipo | 3% | ☐ |
| Smart Narrative con Copilot | 3% | ☐ |
| Captura de pantalla del dashboard | 2% | ☐ |
| **TOTAL** | **20%** | |

---

*Guia generada para el proyecto BeExpand Cash Flow Forecasting*
*Curso: IA en Finanzas y Contabilidad — Mayo 2026*
