"""
Telegram Alert - BeExpand Cash Flow Warning Bot
=================================================
Avisa al CFO cuando la tesoreria peligre en los proximos ~45 dias.

USO:
    1. python telegram_alert.py --setup   (configurar credenciales)
    2. python telegram_alert.py --check   (verificar sin enviar)
    3. python telegram_alert.py           (modo normal: alerta si riesgo)
    4. python telegram_alert.py --test    (enviar mensaje de prueba)
    5. python telegram_alert.py --all     (forzar envio aunque todo normal)

Para programar automaticamente:
    Windows: Programar tarea con Windows Task Scheduler
    Linux:   crontab -e  (ej: 0 9 * * * /ruta/python telegram_alert.py)

DEPENDENCIAS: pip install pandas requests
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

import requests

# --------------------------------------------------
# CONFIGURACION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PREDICCIONES_CSV = BASE_DIR / "data" / "processed" / "predicciones.csv"
CONFIG_FILE = BASE_DIR / "scripts" / "config.json"

UMBRAL_ALERTA = 200_000
UMBRAL_CRITICO = 100_000
HORIZONTE_DIAS = 45


# --------------------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------------------

def p(text):
    """Print seguro para Windows (evita errores de encoding con caracteres especiales)."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: eliminar caracteres no ASCII
        safe = text.encode('ascii', 'replace').decode('ascii')
        print(safe)


def cargar_config():
    """Carga token y chat_id desde config.json o variables de entorno."""
    config = {}

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        p("[OK] Config cargada desde config.json")

    config["TELEGRAM_TOKEN"] = os.getenv("TELEGRAM_TOKEN") or config.get("TELEGRAM_TOKEN", "")
    config["TELEGRAM_CHAT_ID"] = os.getenv("TELEGRAM_CHAT_ID") or config.get("TELEGRAM_CHAT_ID", "")
    config["UMBRAL_ALERTA"] = float(os.getenv("UMBRAL_ALERTA") or config.get("UMBRAL_ALERTA", UMBRAL_ALERTA))
    config["UMBRAL_CRITICO"] = float(os.getenv("UMBRAL_CRITICO") or config.get("UMBRAL_CRITICO", UMBRAL_CRITICO))

    return config


def guardar_config(token, chat_id):
    """Guarda la configuracion en config.json."""
    os.makedirs(CONFIG_FILE.parent, exist_ok=True)
    config = {
        "TELEGRAM_TOKEN": token,
        "TELEGRAM_CHAT_ID": chat_id,
        "UMBRAL_ALERTA": UMBRAL_ALERTA,
        "UMBRAL_CRITICO": UMBRAL_CRITICO,
        "_nota": "Para mayor seguridad, usa variables de entorno TELEGRAM_TOKEN y TELEGRAM_CHAT_ID"
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    p("[OK] Config guardada en " + str(CONFIG_FILE))
    p("     Para produccion, mejor usa variables de entorno.")


def cargar_predicciones():
    """Carga el CSV de predicciones y devuelve solo las futuras."""
    import pandas as pd

    df = pd.read_csv(PREDICCIONES_CSV, encoding="utf-8-sig")
    df["fecha"] = pd.to_datetime(df["fecha"])
    hoy = pd.Timestamp(date.today())

    futuras = df[(df["tipo"] == "prediccion") & (df["fecha"] >= hoy)].copy()
    return futuras


def analizar_riesgo(futuras, umbral_alerta, umbral_critico):
    """
    Analiza las predicciones y determina el nivel de riesgo.
    Devuelve: (nivel, mensaje_telegram, num_dias, prediccion_cercana)
    """
    if futuras.empty:
        return "sin_datos", "No hay predicciones disponibles.", None, None

    futuras = futuras.sort_values("fecha")
    hoy = date.today()

    mejor_distancia = float("inf")
    prediccion_objetivo = None

    for _, row in futuras.iterrows():
        dias_hasta = (row["fecha"].date() - hoy).days
        distancia = abs(dias_hasta - HORIZONTE_DIAS)
        if distancia < mejor_distancia:
            mejor_distancia = distancia
            prediccion_objetivo = row

    if prediccion_objetivo is None:
        return "sin_datos", "No hay predicciones en el horizonte.", None, None

    dias_hasta = (prediccion_objetivo["fecha"].date() - hoy).days
    predicho = prediccion_objetivo["saldo_predicho"]
    ic_inf = prediccion_objetivo["ic_inferior"]
    ic_sup = prediccion_objetivo["ic_superior"]
    mes = prediccion_objetivo["fecha"].strftime("%B %Y")

    # Determinar nivel de riesgo y recomendacion
    if ic_inf < umbral_critico:
        nivel = "CRITICO"
        recomendacion = (
            "ACTIVAR LINEA DE CREDITO URGENTE.\n"
            "La tesoreria podria caer por debajo del umbral critico. "
            "Contactar con el departamento financiero para activar "
            "financiacion extraordinaria y revisar calendario de pagos."
        )
    elif ic_inf < umbral_alerta:
        nivel = "ALERTA"
        recomendacion = (
            "REVISAR CALENDARIO DE COBROS Y GASTOS.\n"
            "La tesoreria se acerca al umbral de seguridad. "
            "Intentar adelantar cobros pendientes, retrasar gastos "
            "no esenciales y revisar la cartera de proyectos."
        )
    else:
        nivel = "NORMAL"
        recomendacion = (
            "TESORERIA SALUDABLE.\n"
            "No se requiere accion inmediata. La posicion de caja "
            "se mantiene en niveles seguros para los proximos meses."
        )

    # Mensaje para Telegram (admite caracteres Unicode/emojis)
    mensaje = (
        "\U0001f916 BeExpand - Alerta al CFO\n"
        "================================\n\n"
        "Periodo: ~" + str(dias_hasta) + " dias (" + mes + ")\n"
        "Prediccion: " + f"{predicho:,.0f}" + " EUR\n"
        "Peor escenario (IC 95%): " + f"{ic_inf:,.0f}" + " EUR\n"
        "Mejor escenario (IC 95%): " + f"{ic_sup:,.0f}" + " EUR\n\n"
        "Estado: " + nivel + "\n\n"
        "Recomendacion:\n" + recomendacion
    )

    return nivel, mensaje, dias_hasta, prediccion_objetivo


def enviar_telegram(token, chat_id, mensaje):
    """Envia el mensaje via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("ok"):
            p("[OK] Alerta enviada a Telegram (chat_id: " + str(chat_id) + ")")
            return True
        else:
            p("[ERROR] Telegram: " + data.get('description', 'desconocido'))
            return False
    except requests.exceptions.RequestException as e:
        p("[ERROR] Conexion Telegram: " + str(e))
        return False


# --------------------------------------------------
# SETUP ASISTIDO
# --------------------------------------------------

def setup_asistido():
    """Guia al usuario para crear el bot y obtener credenciales."""
    p("")
    p("=" * 55)
    p("  CONFIGURACION DEL BOT DE TELEGRAM")
    p("=" * 55)
    p("")
    p("Sigue estos pasos DESDE TU MOVIL o TELEGRAM WEB:")
    p("")
    p("  1. Abre Telegram y busca @BotFather")
    p("  2. Envia: /newbot")
    p("  3. Ponle nombre: BeExpand Cash Flow Alert")
    p("  4. Ponle usuario: bexpand_cashflow_bot (o el que quieras)")
    p("  5. BotFather te dara un TOKEN. Copialo.")
    p("")
    token = input("  Pega el TOKEN aqui: ").strip()

    p("")
    p("  6. Busca tu bot en Telegram (@tu_bot) y enviarle /start")
    p("  7. Abre este enlace en tu navegador (sustituye TOKEN):")
    p("     https://api.telegram.org/bot" + token + "/getUpdates")
    p("  8. Busca el numero 'chat': {'id': 123456789} y copia el numero")
    p("")
    chat_id = input("  Pega el CHAT_ID aqui: ").strip()

    if token and chat_id:
        guardar_config(token, chat_id)
        p("")
        p("  Configuracion completada.")
        p("  Ahora prueba con: python telegram_alert.py --check")
        return True
    else:
        p("  Configuracion cancelada. Faltan datos.")
        return False


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    import pandas as pd

    args = sys.argv[1:]

    # --setup: configurar credenciales
    if "--setup" in args:
        setup_asistido()
        return

    # --check: verificar sin enviar
    if "--check" in args:
        config = cargar_config()
        futuras = cargar_predicciones()

        if futuras.empty:
            p("No hay predicciones futuras disponibles.")
            return

        p("")
        p("=" * 55)
        p("  VERIFICACION DE ALERTA - " + str(date.today()))
        p("=" * 55)
        p("")

        nivel, mensaje, dias, pred = analizar_riesgo(
            futuras,
            config.get("UMBRAL_ALERTA", UMBRAL_ALERTA),
            config.get("UMBRAL_CRITICO", UMBRAL_CRITICO)
        )

        p("Predicciones futuras:")
        for _, row in futuras.iterrows():
            linea = "   " + row['fecha'].strftime('%b %Y').rjust(8) + " -> "
            linea += f"{row['saldo_predicho']:>12,.0f} EUR  "
            linea += f"[IC: {row['ic_inferior']:,.0f} - {row['ic_superior']:,.0f}]"
            p(linea)

        p("")
        p("Riesgo detectado: " + str(nivel))
        if dias:
            p("Horizonte: ~" + str(dias) + " dias")
        p("")
        p("Mensaje que se enviaria:")
        p("")
        p(mensaje)
        p("")
        return

    # --test: enviar mensaje de prueba
    if "--test" in args:
        config = cargar_config()
        if not config["TELEGRAM_TOKEN"] or not config["TELEGRAM_CHAT_ID"]:
            p("[ERROR] Ejecuta primero: python telegram_alert.py --setup")
            return

        mensaje_test = (
            "PRUEBA del Sistema de Alertas BeExpand\n\n"
            "Si recibes esto, el bot funciona correctamente."
        )

        ok = enviar_telegram(config["TELEGRAM_TOKEN"], config["TELEGRAM_CHAT_ID"], mensaje_test)
        if ok:
            p("[OK] Prueba exitosa!")
        else:
            p("[ERROR] Error en la prueba. Revisa token y chat_id.")
        return

    # Modo normal: evaluar y alertar si procede
    config = cargar_config()

    if not config["TELEGRAM_TOKEN"] or not config["TELEGRAM_CHAT_ID"]:
        p("[WARNING] No hay credenciales configuradas.")
        p("   Ejecuta: python telegram_alert.py --setup")
        sys.exit(1)

    try:
        futuras = cargar_predicciones()
    except Exception as e:
        p("[ERROR] Error al cargar predicciones: " + str(e))
        sys.exit(1)

    if futuras.empty:
        p("[INFO] No hay predicciones futuras. No se envia alerta.")
        return

    nivel, mensaje, dias, pred = analizar_riesgo(
        futuras,
        config.get("UMBRAL_ALERTA", UMBRAL_ALERTA),
        config.get("UMBRAL_CRITICO", UMBRAL_CRITICO)
    )

    p("[INFO] Fecha: " + str(date.today()))
    p("[INFO] Riesgo: " + str(nivel))
    if dias:
        p("[INFO] Horizonte: ~" + str(dias) + " dias")

    solo_criticos = "--all" not in args

    if nivel == "NORMAL" and solo_criticos:
        p("[INFO] Tesoreria saludable. No se envia alerta.")
        p("   Usa --all para forzar envio aunque todo este bien.")
        return

    p("[INFO] Enviando alerta (" + nivel + ")...")
    enviar_telegram(config["TELEGRAM_TOKEN"], config["TELEGRAM_CHAT_ID"], mensaje)


if __name__ == "__main__":
    main()
