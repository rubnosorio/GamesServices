CREATE DATABASE juegos;
use juegos;


CREATE TABLE estado (
	estado  int, 
	descripcion varchar(50),
	PRIMARY KEY (estado)	
);

insert into estado(estado, descripcion)
values (0, 'Creado');

insert into estado(estado, descripcion)
values(1, 'Inicializado');

insert into estado(estado, descripcion)
values(2, 'Finalizado');

CREATE TABLE juego(
    juego varchar(200),
    estado int,
    created_at timestamp,
    PRIMARY KEY (juego),
    FOREIGN KEY (estado) REFERENCES estado(estado)
);


CREATE TABLE posicion(
    jugador varchar(200),
    posicion int,
    juego varchar(200),
    FOREIGN KEY (juego) REFERENCES juego(juego)

);

CREATE TABLE turno(
    jugador varchar(200),
    turno boolean,
    juego varchar(200),
    FOREIGN KEY (juego) REFERENCES juego(juego)
);

CREATE TABLE bitacora_juego(
	id int NOT NULL AUTO_INCREMENT, 
	nombre_microservicio varchar(50),
	accion varchar(50),
	created_at timestamp, 
    PRIMARY KEY (id)	
);

