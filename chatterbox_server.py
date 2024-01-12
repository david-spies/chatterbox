import socket
import threading

# Server setup
host = '127.0.0.1'
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

clients = []
usernames = []

# Function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Function to handle client connections
def handle_client(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)  # Display client's chat messages in server terminal
            broadcast(message.encode('utf-8'))  # Broadcast the message to all clients
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} has left the chat\n'.encode('utf-8'))  # Notify clients when someone leaves
            print(f"{username} has left the chat")
            usernames.remove(username)
            break

# Function to receive incoming connections
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('CONNECTED\n'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        broadcast(f'{username} has joined the chat\n'.encode('utf-8'))  # Notify clients when someone joins
        print(f"{username} has joined the chat")
        
        # Display all connected clients in server terminal
        print("Connected clients:")
        for user in usernames:
            print(user)
        
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Server running...")
server.listen(5)
receive()
