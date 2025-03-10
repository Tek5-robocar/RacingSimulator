import socket


def send_command_to_unity(command: str, host: str = '127.0.0.1', port: int = 5000) -> str:
    """Send a command to the Unity server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            s.sendall(command.encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            return response
        except ConnectionRefusedError:
            print("Could not connect to Unity server. Is it running?")
            return ""
