from django.http import HttpResponse, HttpRequest
import socket

def toggle_enabled(request):
    # Establish connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5000))

    # Send commands to toggle output
    client_socket.sendall("on".encode())  # Enable output
    client_socket.sendall("off".encode())  # Disable output

    # Close the connection
    client_socket.close()
    return HttpResponse("Affirmative")