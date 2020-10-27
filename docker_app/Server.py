#se cargan variables globales
from dotenv import load_dotenv
load_dotenv()
# import del manejo de listas
from typing import List, Dict
# import para el funcionamiento general de flask
from flask import Flask
from flask import request
# import libreria json
import json  
# import de conexion con mysql
import mysql.connector
#para simular lanzar dados
import random
#import para obtener fecha y hora
from datetime import date


app = Flask(__name__)  # creacion de la app en python de flask
#configuracion global de base de datos
config = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'database': 'juegos'
}

def juegos() -> List[Dict]:
    # variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    # ejecucion de consulta hacia la base de datos
    cursor.execute('SELECT * FROM juego')
    # creacion de objeto donde se almacenara el contenido de la tabla
    results =  cursor.fetchall()
    data = ''
    for row in results:
      data += "juego = " +  str(row[0]) 
      data += "jugador1 = " + str(row[1])
      data += "posicion_jugador1  = " + str(row[2])
      data += "jugador2 = " + str(row[3])
      data += "posicion_jugador2 = " + str(row[4])
      data += "estado = " + str(row[5])
      data += "created_at = " + str(row[6]) +  "\n"
    # se cierra el cursor
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()
    # retorno del objeto con el contenido de la tabla
    return data


def simularPartida(idJuego, jugadores):
    return 1

#se insertar un nuevo registro en la tabla juego
#se inicializan las posiciones y el marcador de los jugadores.
def generarNuevaPartida(idjuego, jugadores):
    today = date.today()
     # variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    #query insert hacia juego
    sql_query = """INSERT INTO juego (juego, estado, created_at)
                   VALUES (%(id_juego)s, %(estado)s, %(created)s)"""
    # ejecucion de consulta hacia la base de datos  
    cursor.execute(sql_query, {'id_juego': idjuego,  'estado': 0, 'created':  today})
    #query insert hacia posicion
    connection.commit()
    sql_query = """INSERT INTO posicion (jugador, posicion, juego)
                   VALUES (%(jugador)s, %(posicion)s, %(id_juego)s)"""
    cursor.execute(sql_query, {'jugador': str(jugadores[0]), 'posicion': 0, 'id_juego': idjuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    connection.commit()
    #se inserta jugador2
    sql_query = """INSERT INTO posicion (jugador, posicion, juego)
                   VALUES (%(jugador)s, %(posicion)s, %(id_juego)s)"""
    cursor.execute(sql_query, {'jugador': str(jugadores[1]), 'posicion': 0, 'id_juego': idjuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    connection.commit()
    #se inserta turno jugador 1, inicia partida
    sql_query = """INSERT INTO turno (jugador, turno, juego)
                   VALUES (%(jugador)s, %(turno)s, %(id_juego)s)"""
    cursor.execute(sql_query, {'jugador': str(jugadores[0]), 'turno': True, 'id_juego': idjuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    connection.commit()
    #se inserta turno jugador 1, inicia partida
    sql_query = """INSERT INTO turno (jugador, turno, juego)
                   VALUES (%(jugador)s, %(turno)s, %(id_juego)s)"""
    cursor.execute(sql_query, {'jugador': str(jugadores[1]), 'turno': False, 'id_juego': idjuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    connection.commit()
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()
    # retorno del objeto con el contenido de la tabla
    return "1"

def cambiarPosicionJugador(idjuego, idjugador, nuevaPosicion):
    today = date.today()
     # variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    #consulta hacia que se utilizara en base de datos
    sql_query = """UPDATE posicion SET posicion = %(posicion)s WHERE jugador = %(jugador)s and juego = %(juego)s"""
    # ejecucion de consulta hacia la base de datos  
    cursor.execute(sql_query, {'posicion': nuevaPosicion, 'jugador': idjugador, 'juego': idjuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    connection.commit()
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()
    # retorno del objeto con el contenido de la tabla
    return "1"


def obtenerPosicionJugadores(idjuego):
    # variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    #consulta hacia que se utilizara en base de datos
    sql_query = "SELECT jugador, posicion FROM posicion WHERE juego = %(juego)s"
    # ejecucion de consulta hacia la base de datos  
    cursor.execute(sql_query, {'juego': idjuego})
    # creacion de objeto donde se almacenara el contenido de la tabla
    results =  cursor.fetchall()
    json_data_list = []
    for row in results:
        data = {}
        data['jugador'] = str(row[0])
        data['posicion'] = str(row[1])
        json_data_list.append(data)
    # se cierra el cursor
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()
    # retorno del objeto con el contenido de la tabla
    json_data = json.dumps(json_data_list)
    return json_data


# funcion raiz obtener la posicion de los jugadores dentro de un 
# determinado juego
@app.route('/obtenerPosicion/<idjuego>', methods=['GET'])
def obtenerPosicion(idjuego):
    #se obtiene el id del juego
    posiciones = obtenerPosicionJugadores(idjuego)
    return posiciones

'''
@app.route('/guardarPosicion/<idjuego>', methods=['GET'])
def guardarPosicion(idjuego, idjugador):
    #se obtiene el id del juego
    #posiciones = cambiarPosicionJugador(idjuego)
    return json.dumps()
'''
# funcion que permite obtener el turno de un jugador en
# determinado juego
@app.route('/obtenerTurno/<idjuego>', methods=['GET'])
def obtenerTurno(idjuego):
    #variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    #consulta hacia que se utilizara en base de datos
    sql_query = "SELECT * FROM turno WHERE juego = %(id_juego)s"
    return 1

# Funcion que permite iniciar un nuevo juego creado desde un torneo
@app.route('/generar', methods=['POST'])
def generar():
    inputs = request.get_json(force=True)
    idjuego = inputs['id']
    jugadores = inputs['jugadores']
    valor = generarNuevaPartida(idjuego, jugadores)
    return valor

@app.route('/simular', methods=['POST'])
def simular():
    inputs = request.get_json(force=true)
    idjuego = inputs['id']
    jugadores = inputs['jugadores']
    valor = simularPartida(idjuego, jugadores)
    return "1"

@app.route('/obtenerJuegos', methods=['GET'])
def obtenerJuegos():
    return juegos()


if __name__ == '__main__':
    # comando para configurar la ip del servicio
    app.run(host='0.0.0.0')
