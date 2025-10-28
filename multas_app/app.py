from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import get_db_connection
from datetime import datetime

app = Flask(__name__)

# ---------- PÁGINA PRINCIPAL ----------
@app.route('/')
def index():
    return render_template('index.html')



    # Traer asistencias
    cursor.execute("""
        SELECT a.id AS asamblea_id, a.nombre AS asamblea_nombre, a.fecha, a.costo,
               COALESCE(s.presente, 0) AS presente
        FROM asambleas a
        LEFT JOIN asistencias s ON a.id = s.asamblea_id AND s.colegiatura_id = %s
        ORDER BY a.fecha
    """, (colegiatura_id,))
    registros = cursor.fetchall()

    multa_total = sum(float(r['costo']) for r in registros if not bool(r['presente']))

    detalles = [{
        "asamblea_id": r['asamblea_id'],
        "asamblea_nombre": r['asamblea_nombre'],
        "fecha": r['fecha'].isoformat() if isinstance(r['fecha'], datetime) else str(r['fecha']),
        "costo": round(float(r['costo']), 2),
        "presente": bool(r['presente'])
    } for r in registros]

    conn.close()
    return jsonify({
        "existe": True,
        "matricula": colegiatura['nombre'],
        "unidad_multa": round(unidad, 2),
        "multa_total": round(multa_total, 2),
        "detalles": detalles
    })


# ---------- PANEL ADMIN ----------
@app.route('/admin')
def admin():
    return render_template('admin.html')


# ---------- API DE DATOS EN TIEMPO REAL ----------
@app.route('/api/datos')
def api_datos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, fecha, costo FROM asambleas ORDER BY fecha ASC")
    asambleas = cursor.fetchall()

    cursor.execute("SELECT id, nombre, estado, observaciones FROM colegiaturas ORDER BY id ASC")
    colegiaturas = cursor.fetchall()

    cursor.execute("""
        SELECT a.id AS asamblea_id, a.nombre AS asamblea_nombre, c.id AS colegiatura_id, 
               c.nombre AS colegiatura_nombre, s.presente
        FROM asistencias s
        JOIN asambleas a ON s.asamblea_id = a.id
        JOIN colegiaturas c ON s.colegiatura_id = c.id
    """)
    asistencias = cursor.fetchall()

    conn.close()
    return jsonify({
        "asambleas": asambleas,
        "colegiaturas": colegiaturas,
        "asistencias": asistencias
    })


# ---------- CREAR ASAMBLEA ----------
@app.route('/crear_asamblea', methods=['POST'])
def crear_asamblea():
    nombre = request.form.get('nombre', '').strip()
    fecha = request.form.get('fecha', '').strip()
    costo = request.form.get('costo', '').strip()

    if not nombre or not fecha or not costo:
        return "Faltan datos", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO asambleas (nombre, fecha, costo) VALUES (%s, %s, %s)", (nombre, fecha, costo))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/api/asambleas')
def api_asambleas():
    conn = get_db_connection()
    asambleas = conn.execute("SELECT * FROM asambleas").fetchall()
    conn.close()
    return jsonify([dict(a) for a in asambleas])

# ---------- BORRAR ASAMBLEA ----------
@app.route('/borrar_asamblea/<int:id>', methods=['DELETE'])
def borrar_asamblea(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM asistencias WHERE asamblea_id = ?", (id,))
    conn.execute("DELETE FROM asambleas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Asamblea eliminada correctamente"}), 200


# ---------- ACTUALIZAR ASISTENCIA ----------
@app.route('/actualizar_asistencia/<int:colegiatura_id>/<int:asamblea_id>', methods=['POST'])
def actualizar_asistencia(colegiatura_id, asamblea_id):
    presente = request.json.get('presente', False)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO asistencias (asamblea_id, colegiatura_id, presente)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE presente = VALUES(presente)
    """, (asamblea_id, colegiatura_id, presente))
    conn.commit()
    conn.close()
    return ('', 204)


# ---------- ACTUALIZAR OBSERVACIONES ----------
@app.route('/actualizar_observacion/<int:colegiatura_id>', methods=['POST'])
def actualizar_observacion(colegiatura_id):
    data = request.get_json()
    observacion = data.get('observacion', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE colegiaturas SET observaciones = %s WHERE id = %s", (observacion, colegiatura_id))
    conn.commit()
    conn.close()
    return ('', 204)

@app.route('/buscar', methods=['POST'])
def buscar():
    data = request.get_json()
    matricula = str(data.get('matricula', '')).strip()

    # intentar interpretar como número (caj)
    try:
        caj_num = int(matricula)
    except ValueError:
        caj_num = None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener todas las asambleas (para la unidad/matriz)
    cursor.execute("SELECT id, nombre, fecha, costo FROM asambleas ORDER BY fecha ASC")
    asambleas = cursor.fetchall()

    if not asambleas:
        conn.close()
        return jsonify({"error": "No hay asambleas registradas."}), 400

    unidad = float(asambleas[0]['costo'])

    # Buscar por caj (número). Si no se pasó número, devolver "no existe"
    if caj_num is None:
        conn.close()
        return jsonify({
            "existe": False,
            "mensaje": "La búsqueda debe ser por número de CAJ (ej. 1).",
            "unidad_multa": round(unidad, 2),
            "multa_total": 0.0,
            "detalles": []
        })

    # Buscar colegiatura por campo caj
    cursor.execute("SELECT id, caj, nombre, estado, observaciones FROM colegiaturas WHERE caj = %s", (caj_num,))
    colegiatura = cursor.fetchone()

    if not colegiatura:
        # Si no existe la colegiatura por número caj
        total_multa = sum(float(a['costo']) for a in asambleas)
        conn.close()
        return jsonify({
            "existe": False,
            "mensaje": f"No se encontró la colegiatura con CAJ '{caj_num}'.",
            "unidad_multa": round(unidad, 2),
            "multa_total": round(total_multa, 2),
            "detalles": [
                {"asamblea_nombre": a['nombre'], "fecha": str(a['fecha']), "presente": False, "costo": float(a['costo'])}
                for a in asambleas
            ]
        })

    colegiatura_id = colegiatura['id']

    # Traer asistencias de esa colegiatura (LEFT JOIN para mostrar todas las asambleas)
    cursor.execute("""
        SELECT a.id AS asamblea_id, a.nombre AS asamblea_nombre, a.fecha, a.costo,
               COALESCE(s.presente, 0) AS presente
        FROM asambleas a
        LEFT JOIN asistencias s ON a.id = s.asamblea_id AND s.colegiatura_id = %s
        ORDER BY a.fecha
    """, (colegiatura_id,))
    registros = cursor.fetchall()

    multa_total = sum(float(r['costo']) for r in registros if not bool(r['presente']))

    detalles = [{
        "asamblea_id": r['asamblea_id'],
        "asamblea_nombre": r['asamblea_nombre'],
        "fecha": r['fecha'].isoformat() if isinstance(r['fecha'], datetime) else str(r['fecha']),
        "costo": round(float(r['costo']), 2),
        "presente": bool(r['presente'])
    } for r in registros]

    resp = {
        "existe": True,
        "caj": colegiatura['caj'],
        "matricula": colegiatura['nombre'],
        "estado": colegiatura.get('estado', ''),
        "observaciones": colegiatura.get('observaciones', ''),
        "unidad_multa": round(unidad, 2),
        "multa_total": round(multa_total, 2),
        "detalles": detalles
    }

    conn.close()
    return jsonify(resp)


@app.route('/agregar_colegiado', methods=['POST'])
def agregar_colegiado():
    data = request.json
    nombre = data.get('nombre')
    caj = data.get('caj')

    conn = get_db_connection()
    conn.execute("INSERT INTO colegiaturas (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Colegiado agregado exitosamente"}), 201


if __name__ == '__main__':
    app.run(debug=True)
