import os
#se cargan variables globales
from dotenv import load_dotenv
load_dotenv()
#jwt
import jwt
#token
from functools import wraps
# import para hacer solicitudes
import requests
# import del manejo de listas
from typing import List, Dict
# import para el funcionamiento general de flask
from flask import Flask, jsonify
from flask import request
from flask import Response
# import libreria json
import json  
# import de conexion con mysql
import mysql.connector
#para simular lanzar dados
import random
#import para obtener fecha y hora
from datetime import date

error_message = "{'respuesta':'Error'}"
success_message = "{'respuesta': 'Success'}"
app = Flask(__name__)  # creacion de la app en python de flask
#configuracion global de base de datos
config = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'database': 'juegos'
}

scope = ""

def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Mensaje':'Falta el token'}), 403
        try:
            f = open("id_rsa", "r")
            data = jwt.decode(token, str(f.read()), algorithms='RS256')
        except:
            return jsonify({'Mensaje':'Token Invalido'}), 403
        return func(*args, **kwargs)
    return wrapped
    
def updateFinalizarPartida(idjuego):
    try:
        today = date.today()
        # variable de la conexion con la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        #consulta hacia que se utilizara en base de datos
        sql_query = """UPDATE juego SET estado = 2 WHERE  juego = %(juego)s"""
        # ejecucion de consulta hacia la base de datos  
        cursor.execute(sql_query, {'juego': idjuego})
        # creacion de objeto donde se almacenara el contenido de la tabla
        connection.commit()
        cursor.close()
        # se cierra tambien con la conexion hacia la BD
        connection.close()
        return Response(success_message, status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(error_message, status=500,  mimetype='application/json')


def juegos() -> List[Dict]:
    # variable de la conexion con la base de datos
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    # ejecucion de consulta hacia la base de datos
    cursor.execute('''SELECT j.juego, j.estado, j.created_at, p.jugador FROM juego j
                     INNER JOIN posicion p
                        ON p.juego = j.juego''')
    # creacion de objeto donde se almacenara el contenido de la tabla
    results =  cursor.fetchall()
    json_data_list = []
    for row in results:
        data = {}
        data['juego'] = str(row[0])
        data['estado'] = str(row[1])
        data['created_at'] = str(row[2])
        data['jugador'] = str(row[3])
        json_data_list.append(data)
    # se cierra el cursor
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()
    # retorno del objeto con el contenido de la tabla
    return json.dumps(json_data_list)


def obtenerTokenDados():
    parametro = {'id': os.getenv("ID_TOKENDADO"), 'secret' : os.getenv('LLAVE_TOKENDADO')}
    token  = requests.get(os.getenv("JWT_ENDPOINT"), params=parametro)
    return json.loads(token.text)

def tirarDado():
    try:
        solicitud = obtenerTokenDados()
        token  = solicitud["token"]
        header = {'Authorization': 'Bearer ' + token}
        res  = requests.get(os.getenv("DADO_ENDPOINT"), headers=header)
        dadosJson = json.loads(res.text)
        dados = dadosJson["dados"]
        dado1 = dados[0]
        dado2 = dados[1]
        #operacion entre los dados anteriores
        dado3 = dados[2]   
        operacion = 0
        if (dado3 % 2) == 0:
            operacion = dado1 + dado2
        else:
            operacion = abs(dado1 - dado2)
        return operacion
    except Exception as e:
        print(e, flush=True)
        return 0



def simularPartida(idjuego, jugadores):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        pos_jugador1 = 0
        pos_jugador2 = 0    
        generarNuevaPartida(idjuego, jugadores)
        while pos_jugador1 < 32 and pos_jugador2 < 32:
            #turno jugador1
            dado = tirarDado()
            pos_jugador1 += dado
           # guardarBitacoraPartida('SIMULAR', 'JUGADOR ' + jugadores[0] + ' TIRA DADO')
           # guardarBitacoraPartida('SIMULAR', 'JUGADOR ' + jugadores[0] + ' NUEVA POSICION' + str(pos_jugador1))
            #turno jugador2
            dado = tirarDado ()
            pos_jugador2 += dado
            #guardarBitacoraPartida('SIMULAR', 'JUGADOR ' + jugadores[1] + ' TIRA DADO')
            #guardarBitacoraPartida('SIMULAR', 'JUGADOR ' + jugadores[1] + ' NUEVA POSICION' + str(pos_jugador2))

        if pos_jugador1 > 32:
            marcarGanador(idjuego, 1)
            guardarBitacoraPartida('SIMULAR', 'JUGADOR ' + jugadores[0] + 'HA GANADO PARTIDA')
        elif pos_jugador2 > 32:
            marcarGanador(idjuego, 2)
            guardarBitacoraPartida('SIMULAR', 'JUGADOR ' + jugadores[1] + 'HA GANADO PARTIDA')
        return  Response("{'respuesta': 'Juego Simulado con Exito'}", status=201,  mimetype='application/json')
    except Exception as e:
        print(e, flush=True)
        return  Response(error_message, status=500,  mimetype='application/json')

def guardarBitacoraPartida(nombremicro, accion):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    today = date.today()
    #query insert hacia juego
    sql_query = """INSERT INTO bitacora_juego (nombre_microservicio, accion, created_at)
                VALUES (%(nombre)s, %(accion)s, %(created)s)"""
    # ejecucion de consulta hacia la base de datos  
    cursor.execute(sql_query, {'nombre': nombremicro,  'accion': accion, 'created':  today})
    connection.commit()
    cursor.close()
    # se cierra tambien con la conexion hacia la BD
    connection.close()

#se insertar un nuevo registro en la tabla juego
#se inicializan las posiciones y el marcador de los jugadores.
def generarNuevaPartida(idjuego, jugadores):
    #verificar si existen los jugadores
    #verificar jugador 1
    '''
    url = os.getenv("USERS_ENDPOINT") + str(jugadores[0])
    r1 = requests.get(url = os.getenv("USERS_ENDPOINT")) 
    #verificar jugador2

    url = os.getenv("USERS_ENDPOINT") + str(jugadores[1])
    r2 = requests.get(url = os.getenv("USERS_ENDPOINT"))
    if r1.status_code != 200 or r2.status_code != 200:
        return Response("{'Respuesta':'Usuario no encontrado'}", status=404,  mimetype='application/json')'''
    try:

        # obtener la fecha de hoy
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
        return Response(success_message, status=201,  mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(error_message, status=406,  mimetype='application/json')

def cambiarPosicionJugador(idjuego, idjugador, nuevaPosicion):
    try:
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
        return Response(success_message, status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(error_message, status=500,  mimetype='application/json')


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

def obtenerTurnoJuego(idjuego, idjugador):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        #consulta hacia que se utilizara en base de datos
        sql_query = "SELECT turno FROM turno WHERE juego = %(juego)s  AND jugador = %(jugador)s"
        # ejecucion de consulta hacia la base de datos  
        cursor.execute(sql_query, {'juego': idjuego, 'jugador': idjugador})
        results =  cursor.fetchall()    
        data = {}
        for row in results:
            data['turno'] = str(row[0])
        json_data = json.dumps(data)
        # se cierra el cursor
        cursor.close()
        # se cierra tambien con la conexion hacia la BD
        connection.close()
        return Response(json_data, status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(error_message, status=500, mimetype='application/json')
    

def cambiarTurnoJugador(idjuego, jugador):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        #consulta hacia que se utilizara en base de datos
        sql_query = "UPDATE turno set turno = 0  WHERE juego = %(juego)s and jugador = %(jugador)s"
        sql_query_update = "UPDATE turno set turno = 1  WHERE juego = %(juego)s and jugador <> %(jugador)s"
        # ejecucion de consulta hacia la base de datos  
        cursor.execute(sql_query, {'juego': idjuego, 'jugador': jugador})
        connection.commit()
        cursor.execute(sql_query_update, {'juego': idjuego, 'jugador': jugador})
        connection.commit()
        # se cierra el cursor
        cursor.close()
        # se cierra tambien con la conexion hacia la BD
        connection.close()
        return Response("{'respuesta':'turno cambiado'}", status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response("{'respuesta':'Error'}", status=500, mimetype='application/json')

def marcarGanador(idjuego, valor):
    urls = os.getenv("TORNEOS_ENDPOINT") + str(idjuego)
    data = {'marcador': [valor]} 

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r1 = requests.put(urls, data=json.dumps(data), headers=headers)

    if r1.status_code == 201:
        return Response("{'respuesta': 'Marcador guardado en torneos'}", status=201, mimetype='application/json')
    else:
        print(r1.status_code)
        return Response("{'respuesta': 'Error'}", status=r1.status_code, mimetype='application/json')


# se guarda la transaccion
# funcion raiz obtener la posicion de los jugadores dentro de un 
# determinado juego
@app.route('/obtenerPosicion/<idjuego>', methods=['GET'])
def obtenerPosicion(idjuego):
    #se obtiene el id del juego
    posiciones = obtenerPosicionJugadores(idjuego)
    return posiciones


@app.route('/guardarPosicion/<idjuego>/<idjugador>/<posicion>', methods=['POST'])
def guardarPosicion(idjuego, idjugador, posicion):
    #se obtiene el id del juego
    cambiarPosicionJugador(idjuego, idjugador, posicion)
    return Response("{'respuesta': 'Posicion Cambiada'}", status=201, mimetype='application/json')

# funcion que permite obtener el turno de un jugador en
# determinado juego
@app.route('/obtenerTurno/<idjuego>/<idjugador>', methods=['GET'])
def obtenerTurno(idjuego, idjugador):
    #variable de la conexion con la base de datos
    return obtenerTurnoJuego(idjuego, idjugador)
    
    

@app.route('/cambiarTurno/<idjuego>/<idjugador>', methods=['POST'])
def cambiarTurno(idjuego, idjugador):
    return cambiarTurnoJugador(idjuego, idjugador)

# Funcion que permite iniciar un nuevo juego creado desde un torneo
@app.route('/generar', methods=['POST'])
#@check_for_token
def generar():
    inputs = request.get_json(force=True)
    idjuego = inputs['id']
    jugadores = inputs['jugadores']
    valor = generarNuevaPartida(idjuego, jugadores)
    return valor

@app.route('/finalizarPartida/<idjuego>', methods=['POST'])
def finalizarPartida(idjuego):
    return updateFinalizarPartida(idjuego)
    

@app.route('/simular', methods=['POST'])
#@check_for_token
def simular():
    inputs = request.get_json(force=True)
    idjuego = inputs['id']
    jugadores = inputs['jugadores']
    return simularPartida(idjuego, jugadores)



@app.route('/obtenerJuegos', methods=['GET'])
def obtenerJuegos():
    return juegos()

@app.route('/obtenerEnv', methods=['GET'])
def obtenerEnv():
    valor = os.getenv("SECRET_KEY")
    return valor 

@app.route('/ganador/<idjuego>/<valor>', methods=['POST'])
def obtenerGanador(idjuego, valor):
   return marcarGanador(idjuego, valor)



    #verificar jugador2   

if __name__ == '__main__':
    # comando para configurar la ip del servicio
    app.run(debug=True, host='0.0.0.0')
