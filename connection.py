# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import os
import socket
from base64 import b64encode

from constants import (
    BAD_EOL,
    BAD_OFFSET,
    BAD_REQUEST,
    CODE_OK,
    COMMANDS,
    CONTENT_LENGTH_PREFIX,
    EOL,
    FILE_NOT_FOUND,
    INTERNAL_ERROR,
    INVALID_ARGUMENTS,
    INVALID_COMMAND,
    VALID_CHARS,
    error_messages,
    fatal_status,
)


class Connection:
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, sock: socket.socket, directory: str) -> None:
        self.sock = sock
        self.directory = directory
        self.buffer = b""
        self.closed = False

    def _close(self) -> None:
        if not self.closed:
            self.closed = True
        try:
            self.sock.close()
        except OSError:
            pass

    def _send_line(self, line: str) -> None:
        self.sock.sendall((line + EOL).encode("ascii"))

    def _send_status(self, status: int) -> None:
        self._send_line(f"{status} {error_messages[status]}")
        if fatal_status(status):
            self._close()

    def _send_ok_with_payload(self, lines: list[str]) -> None:
        self._send_status(CODE_OK)
        if self.closed:
            return
        for line in lines:
            self._send_line(line)
        self._send_line("")

    def _read_chunk(self) -> bool:
        data = self.sock.recv(4096)
        if not data:
            return False
        self.buffer += data
        return True

    def _next_line(self) -> str | None:
        """
        Devuelve la siguiente línea completa sin CRLF, o None si todavía
        no llegaron suficientes datos.
        Envía BAD_EOL (100) y retorna "" si encuentra \\n sin \\r previo.
        """
        while True:
            pos = self.buffer.find(b"\n")
            if pos == -1:
                return None  # todavía no hay línea completa

            # \n suelto
            if pos == 0 or self.buffer[pos - 1 : pos] != b"\r":
                self._send_status(BAD_EOL)
                return ""   # señal de error 

            raw = self.buffer[: pos - 1]   # sin el \r
            self.buffer = self.buffer[pos + 1 :]  # descarta hasta después del \n

            # Protección contra líneas enormes
            if len(raw) > 4096:
                self._send_status(BAD_REQUEST)
                return ""

            try:
                return raw.decode("ascii")
            except UnicodeDecodeError:
                self._send_status(BAD_REQUEST)
                return ""
    
    def _handle_get_metadata(self, args: list[str]) -> None:
        if len(args) != 1:
            self._send_status(INVALID_ARGUMENTS)
            return
        filename = args[0]
        if not self._is_valid_filename(filename):
            self._send_status(INVALID_ARGUMENTS)
            return
        path = os.path.join(self.directory, filename)
        if not os.path.isfile(path):
            self._send_status(FILE_NOT_FOUND)
            return
        try:
            size = os.path.getsize(path)
        except OSError:
            self._send_status(INTERNAL_ERROR)
            return
        self._send_status(CODE_OK)
        if self.closed:
            return
        self._send_line(str(size))

    def _is_valid_filename(self, filename: str) -> bool:
        return bool(filename) and all(ch in VALID_CHARS for ch in filename)

    def _handle_help(self, args: list[str]) -> None:
        if args:
            self._send_status(INVALID_ARGUMENTS)
            return
        self._send_ok_with_payload(COMMANDS)

    def _handle_file_listing(self, args: list[str]) -> None:
        if args:
            self._send_status(INVALID_ARGUMENTS)
            return
        try:
            names = [entry.name for entry in os.scandir(self.directory) if entry.is_file()]
        except OSError:
            self._send_status(INTERNAL_ERROR)
            return
        names.sort()
        self._send_ok_with_payload(names)

    def _handle_get_slice(self, args: list[str]) -> None:
        # Acepta 3 argumentos (base64) o 4 (raw)
        if len(args) not in (3, 4):
            self._send_status(INVALID_ARGUMENTS)
            return

        filename = args[0]
        if not self._is_valid_filename(filename):
            self._send_status(INVALID_ARGUMENTS)
            return

        # Si hay cuarto argumento debe ser  "raw"
        raw_mode = False
        if len(args) == 4:
            if args[3] != "raw":
                self._send_status(INVALID_ARGUMENTS)
                return
            raw_mode = True

        try:
            offset = int(args[1])
            size = int(args[2])
        except ValueError:
            self._send_status(INVALID_ARGUMENTS)
            return

        if offset < 0 or size < 0:
            self._send_status(INVALID_ARGUMENTS)
            return

        path = os.path.join(self.directory, filename)
        if not os.path.isfile(path):
            self._send_status(FILE_NOT_FOUND)
            return

        try:
            file_size = os.path.getsize(path)
            if offset + size > file_size:
                self._send_status(BAD_OFFSET)
                return

            with open(path, "rb") as f:
                f.seek(offset)
                data = f.read(size)
        except OSError:
            self._send_status(INTERNAL_ERROR)
            return

        if len(data) != size:
            self._send_status(INTERNAL_ERROR)
            return

        self._send_status(CODE_OK)
        if self.closed:
            return

        if raw_mode:
            # Content-Length: N\r\n  +  \r\n  +  N bytes binarios
            header = f"{CONTENT_LENGTH_PREFIX}{size}{EOL}{EOL}"
            self.sock.sendall(header.encode("ascii") + data)
        else:
            self._send_line(b64encode(data).decode("ascii"))

    def _dispatch(self, line: str) -> None:
        parts = line.split()
        if not parts:
            self._send_status(BAD_REQUEST)
            return

        command = parts[0]
        args = parts[1:]

        if command == "quit":
            if args:
                self._send_status(INVALID_ARGUMENTS)
                return
            self._send_status(CODE_OK)
            self._close()
            return

        if command == "help":
            self._handle_help(args)
            return

        if command == "get_file_listing":
            self._handle_file_listing(args)
            return

        if command == "get_metadata":
            self._handle_get_metadata(args)
            return

        if command == "get_slice":
            self._handle_get_slice(args)
            return

        self._send_status(INVALID_COMMAND)

    def handle(self) -> None:
        try:
            while not self.closed:
                line = self._next_line()

                if line is None:
                    if not self._read_chunk():
                        break
                    continue

                if line == "":
                    break

                # comando irreconocible
                stripped = line.strip()
                if not stripped:
                    self._send_status(BAD_REQUEST)
                    # BAD_REQUEST (101)
                    break

                self._dispatch(line)

        except OSError:
            pass  # socket cerrado por el otro lado
        finally:
            self._close()