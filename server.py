#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import argparse
import socket
import sys
import threading
import connection
from constants import DEFAULT_ADDR, DEFAULT_DIR, DEFAULT_PORT


class Server:
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(
        self,
        addr: str = DEFAULT_ADDR,
        port: int = DEFAULT_PORT,
        directory: str = DEFAULT_DIR,
    ) -> None:
        print(f"Serving {directory} on {addr}:{port}.")
        self.directory = directory
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((addr, port))
        self.sock.listen()

    def serve(self) -> None:
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        while True:
            client_sock, client_addr = self.sock.accept()
            print(f"Conexión recibida de {client_addr}")
            conn = connection.Connection(client_sock, self.directory)
            threading.Thread(target=conn.handle, daemon=True).start()


def main() -> None:
    """Parsea los argumentos y lanza el server"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar",
        type=int,
        default=DEFAULT_PORT,
    )
    parser.add_argument(
        "-a", "--address",
        help="Dirección donde escuchar",
        default=DEFAULT_ADDR,
    )
    parser.add_argument(
        "-d", "--datadir",
        help="Directorio compartido",
        default=DEFAULT_DIR,
    )
    args = parser.parse_args()
    try:
        server = Server(args.address, args.port, args.datadir)
        server.serve()
    except OSError as e:
        sys.stderr.write(f"Error al iniciar el servidor: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
