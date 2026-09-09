import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from server import crear_servidor, PORT, NODO  # noqa: E402


def main():
    servidor = crear_servidor()
    print(f"[{NODO}] Backend UP, conectado a Redis y SQLite")
    print(f"[{NODO}] Escuchando en :{PORT}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.shutdown()


if __name__ == "__main__":
    main()