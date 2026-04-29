# Laboratorio 2: Servidor HFTP - Redes y Sistemas Distribuidos 2026

**Grupo 23**
- Álvarez, Lis Ailín
- Pinilla, Lautaro
- Sabino, Lucas

Este proyecto consiste en el diseño e implementación de un servidor de archivos robusto que utiliza el protocolo **HFTP** (Home-made File Transfer Protocol) sobre TCP.

## Video de defensa:
[Link al video](https://drive.google.com/file/d/1xHo_KvawRaaxXOIAPJk0Xrl0PuOMhzOP/view?usp=sharing)


## Requisitos
* Python 3
* Entorno Linux/Ubuntu 

## Configuración del Entorno 

Para preparar el entorno virtual y las dependencias necesarias:

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate

# Instalar dependencias 
pip install -r requirements.txt
```

## Testeos parte B 
### Para los testeos manuales de la parte B: 

```bash
#Crear la carpeta 
mkdir testdata

#Crear archivo de prueba
gedit pruebaB.txt &
# Escribir un poco de texto, ctrl+s y cerrar

#Activar entorno virtual
source venv/bin/activate

#Levantar servidor
python3 server.py -d testdata -p 19500
```

En otra pestaña, ejecutar: 

```bash
telnet localhost 19500
```

Y dentro de la app probar los distintos comandos: 
* help: debería devolver el listado de comandos
* get_file_listing: debería devolver listado de archivos dentro de la carpeta testdata
* get_metadata pruebaB.txt: Debería dar el tamaño de bytes del archivo
* aslk: para probar error por comando incorrecto (200)
* get_metadata fail: probar error por falta de archivo (202)
* quit: cierra la conexión 

### Para los testeos de la cátedra: 

Con el servidor arriba, ejecutar en otra pestaña: 

```bash
python3 server-test.py TestHFTPServer.test_connect_and_quit TestHFTPServer.test_help TestHFTPServer.test_quit_answers_ok TestHFTPServer.test_lookup TestHFTPServer.test_empty_file_listing TestHFTPServer.test_get_metadata TestHFTPServer.test_get_metadata_empty TestHFTPServer.test_context_manager
```

En esta etapa se obtuvo: 

```text
In method test_connect_and_quit:
.
In method test_help:
.
In method test_quit_answers_ok:
.
In method test_lookup:
.
In method test_empty_file_listing:
.
In method test_get_metadata:
.
In method test_get_metadata_empty:
.
In method test_context_manager:
.
----------------------------------------------------------------------
Ran 8 tests in 0.002s

OK
```

## Testeos parte C 
### Para los testeos manuales de la parte C: 

```bash
#Activar entorno virtual 
source venv/bin/activate

#Crear la carpeta 
mkdir testdata

#Crear archivo de prueba
gedit pruebaC &
# Escribir un poco de texto, ctrl+s y cerrar

#Levantar servidor 
python3 server.py -d testdata -p 19500
```
En otra pestaña, ejecutar el cliente:

```bash
telnet localhost 19500
```
Probar el nuevo comando: 
* `get_slice pruebaC 0 4` para ver cómo el servidor responde con el `0 OK` y el bloque de texto crudo en base64

Y por otro lado ejecutar: 

```bash
python3 client.py -p 19500 localhost

#Ingresar el nombre del archivo creado
pruebaC

#Correr un ls
ls 
```
Debería verse el archivo de la carpeta testdata en el nuevo directorio! (por favor no commitearlo)

### Para los testeos de la cátedra: 

Con el servidor arriba, ejecutar en otra pestaña: 

```bash
python3 server-test.py TestHFTPServer.test_get_full_slice TestHFTPServer.test_partial_slices TestHFTPServer.test_retrieve_full_file
```

En esta etapa se obtuvo: 

```text
In method test_get_full_slice:
.
In method test_partial_slices:
.
In method test_retrieve_full_file:
.
----------------------------------------------------------------------
Ran 3 tests in 0.167s

OK
```
