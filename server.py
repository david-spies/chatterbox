#!/usr/bin/env python3
"""
ChatterBox Web — WebSocket Chat Server
Replaces the original TCP socket server with a modern async WebSocket server.
"""

import asyncio
import json
import hashlib
import time
import logging
import signal
from datetime import datetime, timezone
from typing import Optional

import websockets

# ── Configuration ──────────────────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8765
MAX_MESSAGE_LENGTH = 2000
MAX_USERNAME_LENGTH = 24
MIN_USERNAME_LENGTH = 2
PING_INTERVAL = 30
PING_TIMEOUT = 10

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("chatterbox")

# ── State ──────────────────────────────────────────────────────────────────────
clients: dict = {}                                   # ws → {username, id, joined_at}
message_history: list = []                           # last N messages for late joiners
MAX_HISTORY = 50


def generate_user_id(username: str) -> str:
    salt = str(time.time())
    return hashlib.md5(f"{username}{salt}".encode()).hexdigest()[:8]


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M")


def build(event: str, **kwargs) -> str:
    return json.dumps({"event": event, "ts": timestamp(), **kwargs})


async def broadcast(message: str, exclude=None):
    if not clients:
        return
    targets = [ws for ws in clients if ws != exclude]
    if targets:
        await asyncio.gather(*[ws.send(message) for ws in targets], return_exceptions=True)


async def broadcast_all(message: str):
    await broadcast(message, exclude=None)


def user_list() -> list:
    return [{"username": v["username"], "id": v["id"]} for v in clients.values()]


async def handle_client(ws):
    username = None
    user_id = None

    try:
        # ── Handshake: expect a join message first ──────────────────────────
        raw = await asyncio.wait_for(ws.recv(), timeout=15)
        data = json.loads(raw)

        if data.get("event") != "join":
            await ws.send(build("error", message="Expected join event."))
            return

        username = str(data.get("username", "")).strip()

        # Validate username
        if not (MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH):
            await ws.send(build("error", message=f"Username must be {MIN_USERNAME_LENGTH}–{MAX_USERNAME_LENGTH} characters."))
            return

        # Check uniqueness
        existing_names = {v["username"].lower() for v in clients.values()}
        if username.lower() in existing_names:
            await ws.send(build("error", message=f"Username '{username}' is already taken."))
            return

        user_id = generate_user_id(username)
        clients[ws] = {"username": username, "id": user_id, "joined_at": time.time()}

        log.info(f"[+] {username} ({user_id}) connected. Online: {len(clients)}")

        # Send welcome + history to new client
        await ws.send(build("welcome",
            user_id=user_id,
            username=username,
            users=user_list(),
            history=message_history[-MAX_HISTORY:]
        ))

        # Notify everyone else
        system_msg = build("system", message=f"{username} has entered the chat.", users=user_list())
        await broadcast(system_msg, exclude=ws)

        # ── Main message loop ───────────────────────────────────────────────
        async for raw in ws:
            try:
                data = json.loads(raw)
                event = data.get("event", "")

                if event == "message":
                    text = str(data.get("text", "")).strip()
                    if not text:
                        continue
                    text = text[:MAX_MESSAGE_LENGTH]

                    msg = build("message",
                        user_id=user_id,
                        username=username,
                        text=text
                    )
                    message_history.append(json.loads(msg))
                    if len(message_history) > MAX_HISTORY * 2:
                        message_history[:] = message_history[-MAX_HISTORY:]

                    await broadcast_all(msg)
                    log.info(f"[MSG] {username}: {text}")

                elif event == "ping":
                    await ws.send(build("pong"))

                elif event == "typing":
                    state = bool(data.get("state", False))
                    await broadcast(build("typing", user_id=user_id, username=username, state=state), exclude=ws)

            except json.JSONDecodeError:
                await ws.send(build("error", message="Invalid JSON."))

    except asyncio.TimeoutError:
        log.warning("Client timed out during handshake.")
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except websockets.exceptions.ConnectionClosedError as e:
        log.warning(f"Connection closed with error: {e}")
    except Exception as e:
        log.exception(f"Unexpected error: {e}")
    finally:
        if ws in clients:
            del clients[ws]
        if username:
            log.info(f"[-] {username} disconnected. Online: {len(clients)}")
            farewell = build("system", message=f"{username} has left the chat.", users=user_list())
            await broadcast(farewell)


async def main():
    log.info(f"ChatterBox Web Server starting on ws://{HOST}:{PORT}")
    log.info("Press Ctrl+C to stop.\n")

    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    def _shutdown(sig):
        log.info(f"Received {signal.Signals(sig).name}, shutting down...")
        if not stop.done():
            stop.set_result(None)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown, sig)

    async with websockets.serve(
        handle_client,
        HOST,
        PORT,
        ping_interval=PING_INTERVAL,
        ping_timeout=PING_TIMEOUT,
        max_size=64 * 1024,
    ):
        await stop

    log.info("Server stopped.")


if __name__ == "__main__":
    asyncio.run(main())
