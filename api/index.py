from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
# Enable CORS for all routes to allow frontend to call backend
CORS(app)

# --- CONFIGURACIÓN TELEGRAM ---
TELEGRAM_TOKEN = "8588350915:AAGgWE76AZII47Op4XsUmbMfoWuvk6_Ruts"
CHAT_ID = "8307455090"

# --- CONFIGURACIÓN CORREO (GMAIL) ---
EMAIL_ORIGEN = "tecsoleproyectos@gmail.com"
EMAIL_PASSWORD = "clwy jaff odav ilzu"
EMAIL_DESTINO = "ingenieria@tecsole.com"

@app.route('/api/enviar', methods=['POST'])
def enviar_cotizacion():
    # 1. Obtener datos del JSON enviado por el frontend
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "mensaje": "No se recibieron datos JSON"}), 400

    nombre = data.get('nombre', 'Sin Nombre')
    correo = data.get('correo', 'Sin Correo')
    celular = data.get('celular', 'Sin Celular')
    
    ubicacion = data.get('ubicacion', 'N/A')
    tipo = data.get('tipo', 'N/A')
    estrato = data.get('estrato', 'N/A')
    consumo = data.get('consumo', '0')
    costo_fijo = data.get('costoFijo', '0')
    
    # Resultados calculados
    potencia = data.get('potencia', '0')
    paneles = data.get('paneles', '0')
    inversion = data.get('inversion', '0')
    ahorro = data.get('ahorro', '0')
    payback = data.get('payback', '0')
    tir = data.get('tir', '0')
    co2 = data.get('co2', '0')

    # 2. Formatear Mensaje para Telegram (Texto plano)
    msg_telegram = (
        f"☀️ *NUEVA COTIZACIÓN SOLAR*\n\n"
        f"👤 *Cliente:* {nombre}\n"
        f"📧 *Correo:* {correo}\n"
        f"📱 *Celular:* {celular}\n\n"
        f"📍 *Ubicación:* {ubicacion}\n"
        f"🏠 *Tipo:* {tipo} (Estrato {estrato})\n"
        f"⚡ *Consumo:* {consumo} kWh/mes\n"
        f"💰 *Costo Fijo:* {costo_fijo}\n\n"
        f"📊 *RESULTADOS:* \n"
        f"✅ Potencia: {potencia}\n"
        f"✅ Paneles: {paneles}\n"
        f"✅ Inversión: {inversion}\n"
        f"✅ Ahorro Año 1: {ahorro}\n"
        f"✅ Retorno: {payback}\n"
        f"✅ TIR: {tir}\n"
        f"✅ CO2 Evitado: {co2} Ton"
    )

    # 3. Formatear Mensaje para Correo (HTML)
    msg_html = f"""
    <html>
    <body>
        <h2 style="color: #f59e0b;">Nueva Cotización Solar Expert</h2>
        <hr>
        <h3>Datos del Cliente</h3>
        <ul>
            <li><b>Nombre:</b> {nombre}</li>
            <li><b>Correo:</b> {correo}</li>
            <li><b>Celular:</b> {celular}</li>
        </ul>
        <h3>Datos del Proyecto</h3>
        <ul>
            <li><b>Ubicación:</b> {ubicacion}</li>
            <li><b>Tipo Usuario:</b> {tipo} - Estrato {estrato}</li>
            <li><b>Consumo Mensual:</b> {consumo} kWh</li>
            <li><b>Costo Fijo (Alumbrado/Aseo):</b> {costo_fijo}</li>
        </ul>
        <hr>
        <h3>Resultados Preliminares</h3>
        <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%; border-color: #ddd;">
            <tr style="background-color: #f8fafc;">
                <td><b>Potencia Instalada</b></td>
                <td>{potencia}</td>
            </tr>
            <tr>
                <td><b>Número de Paneles</b></td>
                <td>{paneles}</td>
            </tr>
            <tr style="background-color: #f8fafc;">
                <td><b>Inversión Estimada</b></td>
                <td>{inversion}</td>
            </tr>
            <tr>
                <td><b>Ahorro Año 1</b></td>
                <td>{ahorro}</td>
            </tr>
            <tr style="background-color: #f8fafc;">
                <td><b>Retorno Inversión</b></td>
                <td>{payback}</td>
            </tr>
            <tr>
                <td><b>TIR</b></td>
                <td>{tir}</td>
            </tr>
             <tr style="background-color: #f8fafc;">
                <td><b>Impacto Ambiental</b></td>
                <td>{co2} Ton CO2</td>
            </tr>
        </table>
        <br>
        <p style="font-size: 10px; color: #888;">Este correo fue generado automáticamente por la Calculadora web.</p>
    </body>
    </html>
    """

    resultado = {"telegram": "No intentado", "email": "No intentado"}

    # 4. ENVIAR A TELEGRAM
    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg_telegram, "parse_mode": "Markdown"}
        req = requests.post(telegram_url, json=payload)
        resultado["telegram"] = "OK" if req.status_code == 200 else f"Error: {req.text}"
    except Exception as e:
        resultado["telegram"] = f"Fallo: {str(e)}"

    # 5. ENVIAR CORREO
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ORIGEN
        msg['To'] = EMAIL_DESTINO
        msg['Subject'] = f"Nueva Cotización Solar: {nombre}"
        msg.attach(MIMEText(msg_html, 'html'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        resultado["email"] = "OK"
    except Exception as e:
        resultado["email"] = f"Fallo: {str(e)}"

    # 6. Responder al Frontend
    return jsonify({"status": "procesado", "detalles": resultado})

# Handler para Vercel
app = app