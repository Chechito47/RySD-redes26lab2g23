# Laboratorio 2: Servidor HFTP - Redes y Sistemas Distribuidos 2026

**Grupo 23**
- Álvarez, Lis Ailín
- Pinilla, Lautaro
- Sabino, Lucas

Este proyecto consiste en el diseño e implementación de un servidor de archivos robusto que utiliza el protocolo **HFTP** (Home-made File Transfer Protocol) sobre TCP.

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

## Testeos parte D
### Para los testeos de la cátedra:
Con el servidor arriba, ejecutar en otra pestaña:
```bash
python3 server-test.py TestHFTPServer.test_get_slice_raw TestHFTPServer.test_get_slice_raw_partial TestHFTPServer.test_get_slice_rejects_bad_raw_token
```
En esta etapa se obtuvo:

```text
In method test_get_slice_raw:
.
In method test_get_slice_raw_partial:
.
In method test_get_slice_rejects_bad_raw_token:
.
----------------------------------------------------------------------
Ran 3 tests in 0.004s

OK
```

## Testeos parte E
### Para los testeos de la cátedra:
Con el servidor arriba, ejecutar en otra pestaña:
```bash
python3 server-test.py TestHFTPErrors TestHFTPHard
```
En esta etapa se obtuvo:

```text
In method test_bad_argument_count:
.
In method test_bad_argument_count_2:
.
In method test_bad_argument_type:
.
In method test_bad_command:
.
In method test_bad_eol:
.
In method test_bad_offset:
.
In method test_empty_command_line_bad_request:
.
In method test_file_not_found:
.
In method test_file_not_found_get_slice:
.
In method test_internal_error_unreadable_file:
.
In method test_big_file:
.
In method test_big_filename:
.
In method test_command_in_pieces:
.
In method test_data_with_nulls:
.
In method test_long_file_listing:
.
In method test_multiple_commands:
.
----------------------------------------------------------------------
Ran 16 tests in 1.399s

OK
```

## Testeos parte F
### Para los testeos de la cátedra:
Con el servidor arriba, ejecutar en otra pestaña:
```bash
python3 server-test.py TestHFTPMultiClient
```
En esta etapa se obtuvo:

```text
In method test_two_concurrent_file_listing:
.
In method test_two_concurrent_help:
.
----------------------------------------------------------------------
Ran 2 tests in 0.004s

OK
```

## Testeos parte G
### Configuración de Tor:
```bash
# Instalar Tor y torsocks
sudo apt install tor torsocks
 
# Configuramos el servicio en /etc/tor/torrc
sudo nano /etc/tor/torrc
# Agregamos al final esto:
HiddenServiceDir /var/lib/tor/hftp_service/
HiddenServicePort 19500 127.0.0.1:19500
 
# Reiniciar Tor
sudo systemctl restart tor@default
 
# Obtener dirección .onion
sudo cat /var/lib/tor/hftp_service/hostname
```
### Testeos de Tor:
```bash
export ONION=tu_direccion.onion
make test-tor
```

### Pruebas de extremo a extremo:
```bash
# Terminal 1 - servidor:
python server.py -d testdata -p 19500 -a 127.0.0.1
 
# Terminal 2 - cliente:
torsocks python3 client.py -p 19500 <tu_direccion.onion>
# Cliente elige que archivo descargar

# Es necesario que haya algun archivo en el directorio "testdata" del servidor
```

## Testeo general
### Para el testeo general:
Con el servidor arriba, ejecutar en otra pestaña:
```bash
python3 server-test.py
```
Se obtuvo:
```text
n method test_bad_argument_count:
.
In method test_bad_argument_count_2:
.
In method test_bad_argument_type:
.
In method test_bad_command:
.
In method test_bad_eol:
.
In method test_bad_offset:
.
In method test_empty_command_line_bad_request:
.
In method test_file_not_found:
.
In method test_file_not_found_get_slice:
.
In method test_internal_error_unreadable_file:
.
In method test_big_file:
.
In method test_big_filename:
.
In method test_command_in_pieces:
.
In method test_data_with_nulls:
.
In method test_long_file_listing:
.
In method test_multiple_commands:
.
In method test_two_concurrent_file_listing:
.
In method test_two_concurrent_help:
.
In method test_connect_and_quit:
.
In method test_context_manager:
.
In method test_empty_file_listing:
.
In method test_get_full_slice:
.
In method test_get_metadata:
.
In method test_get_metadata_empty:
.
In method test_get_slice_raw:
.
In method test_get_slice_raw_partial:
.
In method test_get_slice_rejects_bad_raw_token:
.
In method test_help:
.
In method test_lookup:
.
In method test_partial_slices:
.
In method test_quit_answers_ok:
.
In method test_retrieve_full_file:
.
----------------------------------------------------------------------
Ran 32 tests in 1.787s

OK
```

## Autoevaluacion
### Para la autoevaluacion:
Con el servidor arriba, ejecutar en otra pestaña:

```bash
pytest -v
```
Se obtuvo:

```text
server-test.py::TestHFTPServer::test_connect_and_quit PASSED             [  2%]
server-test.py::TestHFTPServer::test_context_manager PASSED              [  5%]
server-test.py::TestHFTPServer::test_empty_file_listing PASSED           [  8%]
server-test.py::TestHFTPServer::test_get_full_slice PASSED               [ 11%]
server-test.py::TestHFTPServer::test_get_metadata PASSED                 [ 14%]
server-test.py::TestHFTPServer::test_get_metadata_empty PASSED           [ 17%]
server-test.py::TestHFTPServer::test_get_slice_raw PASSED                [ 20%]
server-test.py::TestHFTPServer::test_get_slice_raw_partial PASSED        [ 22%]
server-test.py::TestHFTPServer::test_get_slice_rejects_bad_raw_token PASSED [ 25%]
server-test.py::TestHFTPServer::test_help PASSED                         [ 28%]
server-test.py::TestHFTPServer::test_lookup PASSED                       [ 31%]
server-test.py::TestHFTPServer::test_partial_slices PASSED               [ 34%]
server-test.py::TestHFTPServer::test_quit_answers_ok PASSED              [ 37%]
server-test.py::TestHFTPServer::test_retrieve_full_file PASSED           [ 40%]
server-test.py::TestHFTPErrors::test_bad_argument_count PASSED           [ 42%]
server-test.py::TestHFTPErrors::test_bad_argument_count_2 PASSED         [ 45%]
server-test.py::TestHFTPErrors::test_bad_argument_type PASSED            [ 48%]
server-test.py::TestHFTPErrors::test_bad_command PASSED                  [ 51%]
server-test.py::TestHFTPErrors::test_bad_eol PASSED                      [ 54%]
server-test.py::TestHFTPErrors::test_bad_offset PASSED                   [ 57%]
server-test.py::TestHFTPErrors::test_empty_command_line_bad_request PASSED [ 60%]
server-test.py::TestHFTPErrors::test_file_not_found PASSED               [ 62%]
server-test.py::TestHFTPErrors::test_file_not_found_get_slice PASSED     [ 65%]
server-test.py::TestHFTPErrors::test_internal_error_unreadable_file PASSED [ 68%]
server-test.py::TestHFTPMultiClient::test_two_concurrent_file_listing PASSED [ 71%]
server-test.py::TestHFTPMultiClient::test_two_concurrent_help PASSED     [ 74%]
server-test.py::TestHFTPHard::test_big_file PASSED                       [ 77%]
server-test.py::TestHFTPHard::test_big_filename PASSED                   [ 80%]
server-test.py::TestHFTPHard::test_command_in_pieces PASSED              [ 82%]
server-test.py::TestHFTPHard::test_data_with_nulls PASSED                [ 85%]
server-test.py::TestHFTPHard::test_long_file_listing PASSED              [ 88%]
server-test.py::TestHFTPHard::test_multiple_commands PASSED              [ 91%]
test_metrics.py::test_cyclomatic_complexity PASSED                       [ 94%]
test_metrics.py::test_static_analysis_ruff PASSED                        [ 97%]
test_metrics.py::test_coverage_is_checked_by_grade_py PASSED             [100%]

============================== 35 passed in 2.06s ==============================
```

### Resumen único
Luego, cerrando el servidor ejecutar:
```bash
python3 grade.py
```
Se obtuvo:

```text
============================================================
  Lab 2 — Autoevaluación (grade.py)
============================================================

1. Tests y cobertura (servidor bajo coverage) ... OK
    Tests OK. Cobertura connection+server: 84.0% (mínimo 75%).

2. Complejidad ciclomática ... OK
    Ninguna función supera complejidad 17.

3. Análisis estático (ruff) ... OK
    Ruff: sin errores en connection.py ni server.py.

============================================================
  RESULTADO: CUMPLE todas las condiciones de aprobación
============================================================
```

