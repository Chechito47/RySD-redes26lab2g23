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
        """Devuelve una línea completa sin CRLF, o None si aún no hay datos."""
        while True:
            pos = self.buffer.find(b"\n")
            if pos == -1:
                return None
            if pos == 0 or self.buffer[pos - 1 : pos] != b"\r":
                self._send_status(BAD_EOL)
                return ""
            raw = self.buffer[: pos - 1]
            self.buffer = self.buffer[pos + 1 :]
            return raw.decode("ascii", errors="strict")

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

    def _handle_get_slice(self, args: list[str]) -> None:
        # respuesta provisional
        self._send_status(INVALID_COMMAND)

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
        """
        Atiende eventos de la conexión hasta que termina.
        """
        try:
            while not self.closed:
                line = self._next_line()
                if line is None:
                    if not self._read_chunk():
                        break
                    continue
                if line == "":
                    break
                self._dispatch(line)
        except (UnicodeDecodeError, OSError):
            if not self.closed:
                self._send_status(BAD_REQUEST)
        finally:
            self._close()
