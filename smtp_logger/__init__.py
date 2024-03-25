"""The smtp_logger package."""

import argparse
import logging
import os
import quopri
import socket
import sys
import threading
import typing as t


def configure_logging(verbose: bool) -> None:
    """Configure logging to go to stdout by default."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stdout)],
    )
    # Set the name
    logging.getLogger().name = "smtp-logger"


def _write_flush(f: t.TextIO, line: str, ending="\r\n") -> None:
    """Write a line to a file using a standard ending and flush it."""
    f.write(line + ending)
    f.flush()


def _process_data_line(
    line: str, data: str, cte: str | None
) -> tuple[bool, str, str | None]:
    """
    Process a line of data in data mode.

    Return a tuple of the (new_data_mode, accumulated_data).
    """
    if line.strip() == ".":
        # Handle the transfer encoding, if supported
        if cte == "quoted-printable":
            data = quopri.decodestring(data).decode("utf-8")
        return (False, data, cte)
    else:
        # Handle a fairly standard content transfer encoding
        if line.startswith("Content-Transfer-Encoding:"):
            cte = line.split(":", 1)[1].strip().lower()
            if cte != "quoted-printable":
                logging.warning(f"unsupported content transfer encoding: {cte}")

        data += line
        return (True, data, cte)


def _process_command_line(f: t.TextIO, line: str) -> bool:
    uline = line.upper()

    if uline.startswith("DATA"):
        _write_flush(f, "354 End data with <CR><LF>.<CR><LF>")
        return True

    if uline.startswith("EHLO") or line.startswith("HELO"):
        _write_flush(f, "250-Hello")
        _write_flush(f, "250-8BITMIME")
        _write_flush(f, "250 OK")
    elif uline.startswith("MAIL FROM:"):
        logging.debug(line)
        _write_flush(f, "250 2.1.0 Ok")
    elif uline.startswith("RCPT TO:"):
        logging.debug(line)
        _write_flush(f, "250 2.1.5 Ok")
    elif uline.startswith("QUIT"):
        _write_flush(f, "221 2.0.0 Bye")
    else:
        _write_flush(f, "500 5.5.1 Command not recognized")
    return False


def _handle_connection(conn: socket.socket, addr: tuple[socket.socket, t.Any]) -> None:
    """Handle an incoming connection."""
    logging.debug(f"connection from {addr}")
    data_mode = False
    cte: str | None = None
    data = ""

    try:
        with conn.makefile("rw", encoding="utf-8", newline=None) as f:
            _write_flush(f, "220 smtp-logger ready")
            for line in f:
                if data_mode:
                    data_mode, data, cte = _process_data_line(line, data, cte)
                    if not data_mode:
                        logging.info(data)
                        _write_flush(f, "250 2.0.0 OK: Queued")
                else:
                    line = line.strip()
                    data_mode = _process_command_line(f, line)
                    if data_mode:
                        data = ""
                        cte = None
    except Exception as e:
        logging.error(f"unexpectedly disconnected from {addr}: {e}")
        raise
    else:
        logging.debug(f"disconnected from {addr}")
    finally:
        conn.close()


def smtp_logger(host: str, port: int, verbose: bool):
    """Run an SMTP logging server."""
    configure_logging(verbose)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((host, port))
        server.listen()
        logging.info(f"smtp-logger listening on {host}:{port}...")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=_handle_connection, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        logging.info("shutting down...")
    except Exception as e:
        logging.error(f"unexpected error: {e}")
    finally:
        server.close()


def _parse_args() -> argparse.Namespace:
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(description="SMTP Logger -- a mock SMTP server.")
    parser.add_argument(
        "-H",
        "--host",
        help="The host to bind to.",
        default=os.getenv("SMTP_LOGGER_HOST", "localhost"),
    )
    parser.add_argument(
        "-p",
        "--port",
        help="The port to bind to.",
        type=int,
        default=int(os.getenv("SMTP_LOGGER_PORT", 8025)),
    )
    parser.add_argument(
        "-v", "--verbose", help="Enable verbose logging.", action="store_true"
    )
    return parser.parse_args()


def cli():
    """Run the SMTP logger from the command-line."""
    args = _parse_args()
    smtp_logger(args.host, args.port, args.verbose)
