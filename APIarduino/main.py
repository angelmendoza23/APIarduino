from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Si tienes una contraseña, ponla aquí
    'database': 'barberia',
    'use_pure': True
}

# Endpoint para recibir el servicio realizado
@app.route('/api/barberservice', methods=['POST'])
def add_service():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    barber_name = data.get('barber_name')
    service_name = data.get('service_name')
    service_value = data.get('service_value')

    if not (barber_name and service_name and service_value):
        return jsonify({"error": "Missing fields"}), 400

    try:
        # Conectar y guardar en la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO services (barber_name, service_name, service_value, service_date)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (barber_name, service_name, service_value, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Service added successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(err)}"}), 500
    
@app.route('/api/barberservice', methods=['GET'])
def get_services():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM services"
        cursor.execute(query)
        services = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(services), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(err)}"}), 500
    
@app.route('/api/barberservice/<barber_name>', methods=['GET'])
def get_barber_services(barber_name):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Consulta para obtener servicios de un barbero específico
        query = """
            SELECT service_name, service_value
            FROM services
            WHERE barber_name = %s
        """
        cursor.execute(query, (barber_name,))
        services = cursor.fetchall()
        
        # Calcular el total del valor de los servicios
        total_value = sum(service['service_value'] for service in services)
        
        cursor.close()
        conn.close()
        
        # Respuesta con la lista de servicios y el total
        return jsonify({
            "barber_name": barber_name,
            "services": services,
            "total_value": total_value
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(err)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)


