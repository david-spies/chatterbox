import socket
import threading
import tkinter as tk

# Function to receive messages from the server
def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            message_list.insert(tk.END, message)
        except:
            # Handle exceptions or client disconnect
            break

# Function to send messages to the server
def send(event=None):
    message = entry_field.get("1.0", tk.END).strip()
    entry_field.delete("1.0", tk.END)  # Clear the input field
    client_socket.send(message.encode('utf-8'))
    if message == "/quit":
        client_socket.close()
        root.quit()

# Function to connect to the server
def connect_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((entry_ip.get(), 5555))

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # Get username from entry_username field
    username = entry_username.get()
    client_socket.send(username.encode('utf-8'))

# GUI setup
root = tk.Tk()
root.geometry("400x580")
root.title("Chatterbox")

# Color palette
m1c = '#00ffff'
bgc = '#494949'
dbg = '#474747'
fgc = '#111111'

root.tk_setPalette(background=bgc, foreground=m1c, activeBackground=fgc,
                   activeForeground=bgc, highlightColor=m1c, highlightBackground=m1c)

# Label for Chat name and description
messages_label = tk.Label(root, text="Chatterbox", font=8, bg='#494949', fg="#00f000")
messages_label.pack()

# Label for IP address

ip_label = tk.Label(root, text="Server IP:", bg=bgc, fg=m1c)
ip_label.pack()
entry_ip = tk.Entry(root, bg='#383838', fg='#00f000')
entry_ip.pack()

message_frame = tk.Frame(root)
scrollbar = tk.Scrollbar(message_frame)
message_list = tk.Text(message_frame, bg='#383838', fg='#00f000', height=20, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar.config(command=message_list.yview)
message_list.pack(side=tk.LEFT, fill=tk.BOTH)
message_frame.pack(padx=20, pady=20)

entry_field = tk.Text(root, bg='#383838', fg='#00f000', height=4, width=50)
entry_field.bind("<Return>", send)
entry_field.pack(padx=20, pady=0)

# Add Entry widget for username
username_label = tk.Label(root, text="Username:", bg=bgc, fg=m1c)
username_label.pack()
entry_username = tk.Entry(root, bg='#383838', fg='#00f000')
entry_username.pack()

# Repositioning buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)

send_button = tk.Button(button_frame, text="Send", command=send)
send_button.pack(side=tk.RIGHT, padx=20, pady=4)

connect_button = tk.Button(button_frame, text="Connect", command=connect_server)
connect_button.pack(side=tk.LEFT, padx=20, pady=4)

tk.mainloop()
