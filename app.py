from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import mysql.connector
from datetime import datetime
import io
import os
import mysql.connector
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "clave_secreta_bjj"

# 🔌 CONEXIÓN MYSQL
conexion = mysql.connector.connect(
    host=os.getenv("DB_HOST", "autorack.proxy.rlwy.net"),
    port=int(os.getenv("DB_PORT", 14787)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", "TDAsamrOUIXdcXGlThkvIUrDKPmdJhDx"),
    database=os.getenv("DB_NAME", "railway"),
    ssl_disabled=False
)

cursor = conexion.cursor(dictionary=True)


@app.route("/test_db")
def test_db():
    try:
        cursor.execute("SELECT 1")
        return "✅ Conexión a Railway exitosa"
    except Exception as e:
        return f"❌ Error al conectar: {e}"
    
# 🏠 INICIO
@app.route("/")
def index():
    return render_template("Index.html")

# 👥 CLIENTES
@app.route("/clientes")
def clientes():
    cursor.execute("SELECT * FROM Clientes")
    datos = cursor.fetchall()
    return render_template("clientes.html", clientes=datos)

# 📝 REGISTRAR CLIENTE
@app.route("/registrar_cliente")
def registrar_cliente():

    cursor.execute("""
        SELECT nombre, telefono, correo, cedula
        FROM Clientes
        ORDER BY id_cliente DESC
        LIMIT 15
    """)
    clientes = cursor.fetchall()

    return render_template("Registrar_cliente.html", clientes=clientes)

# 💾 GUARDAR CLIENTE
@app.route('/guardar-cliente', methods=["POST"])
def guardar_cliente():

    nombre = request.form.get("nombre")
    telefono = request.form.get("telefono")
    correo = request.form.get("correo")
    cedula = request.form.get("cedula")

    cursor.execute(
        "SELECT * FROM Clientes WHERE nombre = %s OR telefono = %s",
        (nombre, telefono)
    )
    existe = cursor.fetchone()

    if existe:
        flash("Este cliente ya está registrado (Nombre o Teléfono repetido)", "error")
        return redirect(url_for("registrar_cliente"))

    cursor.execute("""
        INSERT INTO Clientes (nombre, telefono, correo, cedula)
        VALUES (%s, %s, %s, %s)
    """, (nombre, telefono, correo, cedula))

    conexion.commit()

    flash("Cliente registrado correctamente", "success")
    return redirect(url_for("registrar_cliente"))

# 📦 PAQUETES
@app.route("/paquetes")
def paquetes():
    return render_template("registrar_paquete.html")

# 💾 GUARDAR PAQUETE
@app.route("/guardar_paquete", methods=["POST"])
def guardar_paquete():

    warehouse = request.form["warehouse"]
    tracking = request.form["tracking"]
    peso = float(request.form["peso"])

    cursor.execute(
        "SELECT id_cliente FROM Clientes WHERE warehouse = %s",
        (warehouse,)
    )
    cliente = cursor.fetchone()

    if cliente:
        id_cliente = cliente["id_cliente"]
        precio = peso * 7
        fecha = datetime.now()

        cursor.execute("""
            INSERT INTO Paquetes (id_cliente, tracking, peso, precio, fecha)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, tracking, peso, precio, fecha))

        conexion.commit()

    return redirect(url_for("paquetes"))

# 🧾 FACTURA
@app.route("/factura/<int:id_paquete>")
def factura(id_paquete):

    cursor.execute("""
        SELECT c.nombre, p.tracking, p.peso, p.precio
        FROM Paquetes p
        JOIN Clientes c ON p.id_cliente = c.id_cliente
        WHERE p.id_paquete = %s
    """, (id_paquete,))

    datos = cursor.fetchone()

    return render_template("factura.html", datos=datos)

# 📲 WHATSAPP
@app.route("/whatsapp/<telefono>/<total>")
def whatsapp(telefono, total):

    mensaje = f"Hola, su factura es de ${total}"
    link = f"https://wa.me/{telefono}?text={mensaje}"

    return redirect(link)

# 📊 ESTADÍSTICAS
@app.route("/estadisticas")
def estadisticas():

    cursor.execute("""
        SELECT MONTH(fecha) as mes, SUM(precio) as total
        FROM Paquetes
        GROUP BY MONTH(fecha)
    """)

    datos = cursor.fetchall()

    return render_template("estadisticas.html", datos=datos)

# 📄 PDF
@app.route("/clientes_pdf")
def clientes_pdf():
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []

    styles = getSampleStyleSheet()
    titulo = Paragraph("Lista de Clientes Registrados", styles['Title'])
    elementos.append(titulo)
    elementos.append(Spacer(1, 20))

    cursor.execute("SELECT nombre, telefono, correo, cedula FROM Clientes")
    clientes = cursor.fetchall()

    data = [["Nombre", "Teléfono", "Correo", "Cédula"]]

    for c in clientes:
        data.append([c["nombre"], c["telefono"], c["correo"], c["cedula"]])

    tabla = Table(data)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))

    elementos.append(tabla)

    doc.build(elementos)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                    download_name="clientes.pdf",
                    mimetype='application/pdf')

# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # usa el puerto de Render
    app.run(host="0.0.0.0", port=port)
    