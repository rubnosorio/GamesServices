# creacion de imagen de python 
FROM python:3.6

EXPOSE 80
# Configuro la carpeta de trabajo
WORKDIR /app
# copia todos los archivos a la carpeta app para la instalacion de flask y el conector y paso del proyecto
ADD . /app
# actualizar pip
RUN python3 -m pip install --upgrade pip
# instalacion de los requeriemientos en la imagen
RUN pip install -r ./docker_app/requirements.txt
# configuracion del comando para correr la aplicacion
CMD python ./docker_app/Server.py
