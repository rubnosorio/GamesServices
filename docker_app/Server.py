# import del manejo de listas
from typing import List, Dict
# import para el funcionamiento general de flask
from flask import Flask
# import libreria json
import json  
# import de conexion con mysql
import mysql.connector


app = Flask(__name__)  # creacion de la app en python de flask

def obtenerPosicionJugadores(idJuego):
    # Variable utilizada para la conexion con la base de datos
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'juegos'
    }
    # variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    #consulta hacia que se utilizara en base de datos
    sql_query = "SELECT * FROM juego where juego = %(id_juego)s"
    # ejecucion de consulta hacia la base de datos  
    cursor.execute(sql_query, {'id_juego': idJuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    results =  cursor.fetchall()
    data = ''
    for row in results:
        data = {"jugador1" : str(row[0]),
                "posicion_jugador1": str(row[1]),
                "jugador2" : str(row[2]), 
                "posicion_jugador2": str(row[3])}
    # se cierra el cursor
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()
    # retorno del objeto con el contenido de la tabla
    return data


# funcion raiz obtener la posicion de los jugadores dentro de un 
# determinado juego
@app.route('/obtenerPosicion/<idjuego>', methods=['GET'])
def index(idjuego):
    #se obtiene el id del juego
    posiciones = obtenerPosicionJugadores(idjuego)
    return json.dumps()


if __name__ == '__main__':
    # comando para configurar la ip del servicio
    app.run(host='0.0.0.0')
