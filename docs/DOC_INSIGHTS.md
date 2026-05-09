# BeExpand — Documento de Insights
## Cash Flow Forecasting & Analisis Financiero

**Fecha:** Mayo 2026
**Periodo analizado:** Enero 2023 — Julio 2026 (43 meses)
**Modelo:** Prophet con regresores externos

---

## 1. Resumen Ejecutivo

BeExpand mantiene una **salud financiera solida** con una posicion de tesoreria de **2,6M €** a cierre de Abril 2026, reflejando un crecimiento sostenido desde mediados de 2024. La empresa genera un margen mensual promedio de **+48.843 €** (ratio de cobertura del **122,9%**), lo que indica que los ingresos cubren holgadamente los gastos operativos.

El modelo de forecasting Prophet proyecta una posicion de **4,17M € a 30 dias** con un posterior descenso estacional a **2,54M € a 90 dias** (Julio 2026), manteniendose siempre en niveles muy por encima de los umbrales de riesgo.

| Indicador | Valor |
|-----------|-------|
| Saldo actual (Abr 2026) | 2.600.097 € |
| Ingreso mensual promedio | 273.528 €/mes |
| Gasto mensual promedio | 224.685 €/mes |
| Margen mensual promedio | +48.843 €/mes |
| Ratio de cobertura | 122,9% |
| Crecimiento de tesoreria (2023-2026) | +2.270.118 € |

---

## 2. Principales Hallazgos

### 2.1 Estructura de Ingresos

El **90,5%** de los ingresos provienen de **contratos recurrentes (retainers)**, lo que proporciona una base predecible y estable. Solo el **9,5%** corresponde a proyectos one-off. Esto es una fortaleza: la empresa no depende de ventas puntuales para cubrir sus costes fijos.

### 2.2 Estructura de Gastos

Los gastos de **Personal** representan el **82%** del total (7,37M € en 40 meses), algo esperable para una empresa de servicios con 50+ empleados. El resto se distribuye entre Estructura (7,1%), Tributario (5,8%), Tecnologia (2,8%), Viajes y Ferias (1,4%) y Marketing (0,9%).

### 2.3 Estacionalidad

El analisis revela un **patron estacional marcado**:

| Trimestre | Estacionalidad | Impacto en tesoreria |
|-----------|---------------|---------------------|
| Ene-Mar | 1,07 (alta) | Mayor actividad comercial |
| Abr-Jun | 1,08 (alta) | Pico de proyectos |
| Jul-Sep | **0,85** (baja) | **Descenso estacional por vacaciones** |
| Oct-Dic | 0,97 (media) | Recuperacion |

**Agosto** es el mes de menor actividad (factor 0,50), consistente con el cierre estival tipico en empresas espanolas.

### 2.4 Precision del Modelo Prophet

| Métrica | Valor |
|---------|-------|
| Error absoluto medio (MAE) | Ver notebook para valor exacto |
| Raiz error cuadratico medio (RMSE) | Ver notebook para valor exacto |
| Error porcentual absoluto (MAPE) | Ver notebook para valor exacto |
| R² | Ver notebook para valor exacto |

> Las metricas exactas estan disponibles en `notebooks/02_modelo_forecasting.ipynb` (celda 5b).

### 2.5 Prediccion a 30/60/90 Dias

| Horizonte | Mes | Prediccion | IC 95% Inferior | IC 95% Superior |
|-----------|-----|------------|-----------------|-----------------|
| **30 dias** | Mayo 2026 | **4.170.855 €** | 4.118.852 € | 4.225.958 € |
| **60 dias** | Junio 2026 | **3.375.884 €** | 3.286.153 € | 3.457.843 € |
| **90 dias** | Julio 2026 | **2.541.214 €** | 2.438.064 € | 2.646.131 € |

La prediccion muestra un pico a 30 dias seguido de un descenso estacional. Este comportamiento es coherente con la estacionalidad historica: Mayo suele ser un mes de alta actividad, mientras que Julio entra en el periodo de menor facturacion.

**Punto clave:** Incluso en el **peor escenario** (IC inferior a 90 dias: 2,44M €), la tesoreria se mantiene muy por encima del umbral de alerta de 200.000 €.

---

## 3. Recomendaciones para BeExpand

### 3.1 Mantener la base recurrente

El modelo de retainer (90,5% de ingresos) es el mayor activo financiero de BeExpand. Se recomienda:
- Establecer un **sistema de alerta temprana** si la proporcion de ingresos recurrentes cae por debajo del 80%
- Priorizar la retencion de clientes retainer sobre la captacion de proyectos one-off

### 3.2 Planificar el descenso estacional de verano

Julio-Agosto muestran consistentemente los factores estacionales mas bajos (0,90 y 0,50). Se recomienda:
- Acumular **colchon de tesoreria adicional** en el segundo trimestre para cubrir el verano
- Negociar con clientes el calendario de pagos para evitar concentrar gastos en periodos bajos

### 3.3 Monitorear los margenes

El ratio de cobertura actual (122,9%) es saludable pero sensible. Se recomienda:
- Establecer un **umbral minimo del 110%** como objetivo
- Si el ratio cobertura cae por debajo del 100% durante dos meses consecutivos, revisar estructura de costes

### 3.4 Usar el modelo de forecasting como herramienta de decision

El modelo Prophet proporciona predicciones con intervalos de confianza a 90 dias. Se recomienda:
- Actualizar el modelo **trimestralmente** con nuevos datos
- Integrar las predicciones en el dashboard de Power BI para monitorizacion continua
- Configurar **alertas automaticas** (via Make/Integromat) cuando la prediccion caiga por debajo de 200.000 €

### 3.5 Proxima expansion

Con una tesoreria de 2,6M € y tendencia alcista, BeExpand tiene **capacidad para financiar crecimiento** sin necesidad de financiacion externa a corto plazo. Opciones a considerar:
- Expansion de plantilla o nuevas lineas de servicio
- Inversion en tecnologia y automatizacion
- Apertura de nuevos mercados internacionales

---

## 4. Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Concentracion de ingresos en retainers | Baja | Medio | Diversificar con proyectos |
| Estacionalidad verano | Alta | Bajo | Colchon de tesoreria |
| Subida de IPC/Euribor | Media | Medio | Revisar margenes trimestralmente |
| Dependencia de Personal (82% gastos) | Media | Alto | Automatizacion de procesos |

---

*Documento generado para el proyecto BeExpand Cash Flow Forecasting*
*Curso: IA en Finanzas y Contabilidad — Mayo 2026*
