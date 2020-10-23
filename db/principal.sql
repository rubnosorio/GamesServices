CREATE DATABASE juegos;
use juegos;


CREATE TABLE estado (
	estado  int, 
	descripcion varchar(50),
	PRIMARY KEY (estado)	
);


CREATE TABLE juego(
    juego int,
    jugador1 int, 
    posicion_jugador1 int,
    jugador2 int, 
    posicion_jugador2 int,
    estado int,
    created_at timestamp,
    PRIMARY KEY (juego),
    FOREIGN KEY (estado) REFERENCES estado(estado)
);

