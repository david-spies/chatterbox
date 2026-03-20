# Quickstart — ChatterBox Web

This guide walks you through running a full **development environment on one machine**: the WebSocket server and one or more browser clients.

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8+ | `python --version` to check |
| pip | any | comes with Python |
| A modern browser | Chrome 90+, Firefox 88+, Edge 90+, Safari 15+ | WebSocket support required |

---

## Step 1 — Clone or download the project

```bash
# If using git:
git clone https://github.com/david-spies/chatterbox.git
cd chatterbox
```

Or unzip the downloaded archive and open a terminal inside the `chatterbox-web/` folder.

---

## Step 2 — Install server dependencies

```bash
# From the project root:
pip install -r server/requirements.txt
```

This installs only one package: `websockets`.

If you prefer a virtual environment (recommended):

```bash
python -m venv .venv

# macOS / Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

pip install -r server/requirements.txt
```

---

## Step 3 — Start the server

```bash
python server/server.py
```

You should see:

```
2025-01-01 12:00:00 [INFO] ChatterBox Web Server starting on ws://0.0.0.0:8765
2025-01-01 12:00:00 [INFO] Press Ctrl+C to stop.
```

The server is now listening for WebSocket connections on port **8765**.

> **Tip:** Leave this terminal open. The server must be running for clients to connect.

---

## Step 4 — Open the client

Navigate to the `client/` folder and double-click `index.html`.

It will open in your default browser. You can also drag it into any open browser window.

No web server is needed — the file opens directly from your filesystem via `file://`.

---

## Step 5 — Connect and chat

1. In the **Handle** field, type a username (2–24 characters).
2. In the **Server** field, confirm the value is `ws://localhost:8765` (it's pre-filled).
3. Click **↳ connect**.
4. You're in! Open a second browser window or tab and connect with a different username to test multi-user messaging.

---

## Running Multiple Clients

To simulate a multi-user environment on one machine:

- Open `index.html` in multiple **browser tabs or windows**
- Connect each with a different username
- Messages, join/leave events, and typing indicators are all shared in real time

---

## LAN / Network Testing

To let other machines on your local network connect:

1. Find your machine's local IP:
   ```bash
   # macOS / Linux:
   hostname -I | awk '{print $1}'

   # Windows:
   ipconfig  # look for IPv4 Address
   ```

2. Share the client file (`index.html`) with others, or serve it with Python's built-in HTTP server:
   ```bash
   cd client
   python -m http.server 3000
   ```
   Then open: `http://<your-ip>:3000`

3. Other clients should enter `ws://<your-ip>:8765` in the Server field.

---

## Configuration

Server defaults are set at the top of `server/server.py`:

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Binds to all interfaces |
| `PORT` | `8765` | WebSocket port |
| `MAX_MESSAGE_LENGTH` | `2000` | Characters per message |
| `MAX_USERNAME_LENGTH` | `24` | Characters for username |
| `MAX_HISTORY` | `50` | Messages sent to new joiners |
| `PING_INTERVAL` | `30` | Seconds between keep-alive pings |

---

## Stopping the Server

Press `Ctrl+C` in the terminal running `server.py`. It will shut down gracefully.

---

## Folder Reference

```
chatterbox-web/
├── client/
│   └── index.html        ← Open this in a browser. That's it.
├── server/
│   ├── server.py         ← Run: python server/server.py
│   └── requirements.txt  ← Run: pip install -r server/requirements.txt
└── docs/
    ├── quickstart.md     ← You are here
    ├── tech-stack.md
    ├── README.md
    └── requirements.txt
```
