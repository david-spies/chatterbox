# Tech Stack — ChatterBox Web

A breakdown of every technology choice and the reasoning behind it.

---

## Overview

| Layer | Technology | Why |
|---|---|---|
| Transport | WebSocket (RFC 6455) | Replaces raw TCP; browser-native, full-duplex |
| Server runtime | Python 3.8+ | Same language as original project, minimal friction |
| Server library | `websockets` (Python) | Async, lightweight, no framework overhead |
| Client | Vanilla HTML + CSS + JS | Zero build toolchain — open with double-click |
| Fonts | Google Fonts CDN | Share Tech Mono · Rajdhani · Exo 2 |
| State management | JS in-memory (plain objects) | No framework needed for this scope |
| Persistence | None (by design) | Messages live in the session only, matching original |

---

## Server

### Python + `websockets`

The original server used Python's built-in `socket` module over raw TCP. The replacement uses the `websockets` library, which:

- Runs on Python's `asyncio` event loop — handles hundreds of concurrent connections with a single thread
- Implements the WebSocket handshake and framing automatically
- Provides clean `async for message in websocket` iteration
- Weighs almost nothing (`websockets` is ~100KB, zero transitive dependencies)

**Message format:** All communication is JSON over WebSocket. Events are typed with an `event` key:

```json
// Client → Server
{ "event": "join",    "username": "alice" }
{ "event": "message", "text": "hello!" }
{ "event": "typing",  "state": true }
{ "event": "ping" }

// Server → Client
{ "event": "welcome",  "user_id": "a1b2c3d4", "username": "alice", "users": [...], "history": [...] }
{ "event": "message",  "user_id": "...", "username": "alice", "text": "hello!", "ts": "14:32" }
{ "event": "system",   "message": "alice has entered the chat.", "users": [...] }
{ "event": "typing",   "user_id": "...", "username": "alice", "state": true }
{ "event": "error",    "message": "Username already taken." }
{ "event": "pong" }
```

---

## Client

### Single-file HTML (`index.html`)

The entire client — markup, styles, and logic — lives in one HTML file. This is a deliberate choice:

- **No build step** — no Node.js, no npm, no webpack, no bundler
- **No server required for the client** — open from `file://` directly in a browser
- **Portable** — share the file via USB drive, email, or a simple `python -m http.server`
- **Auditable** — everything is readable in one place

### Vanilla JavaScript

No React, Vue, Svelte, or any framework. For a chat app of this scope (one screen, one channel, real-time events), the browser's native APIs are sufficient:

- `WebSocket` API for the connection
- `localStorage` for remembering server URL and username
- `requestAnimationFrame` for smooth scroll
- DOM manipulation for rendering messages

The JS is ~300 lines, fully readable without tooling.

### CSS Architecture

- **CSS custom properties** for the entire palette and spacing scale
- **No utility framework** (no Tailwind) — all styles are purposeful and scoped
- Animations use `@keyframes` and CSS transitions only — no JS animation library
- Scanline effect and noise texture are pure CSS / inline SVG — no image assets

---

## Design System

### Color Palette

| Token | Value | Usage |
|---|---|---|
| `--green` | `#39FF14` | Primary accent, own messages, active states |
| `--green-dim` | `#2cb80f` | Hover states, secondary green |
| `--slate` | `#7B9CC4` | Hyperlinks, info badges |
| `--slate-deep` | `#1E2D45` | Background accents |
| `--black` / `--void` | `#0A0B0D` / `#050607` | Base backgrounds |
| `--surface-0..3` | various dark grays | Layered surfaces |
| `--gray-1..5` | `#A8B5C4` → `#2C323C` | Text, borders, dividers |
| `--danger` | `#FF3B5C` | Errors, disconnect warnings |
| `--warn` | `#F5A623` | Leave events, caution states |

### Typography

| Font | Role | Personality |
|---|---|---|
| **Share Tech Mono** | Labels, timestamps, system text | Terminal / hacker aesthetic |
| **Rajdhani** | UI headings, buttons, usernames | Geometric, technical, slightly military |
| **Exo 2** | Message body text | Readable at small sizes, sci-fi feel |

---

## What Was Removed vs. Original

| Original feature | Status | Notes |
|---|---|---|
| `hashlib` password/token | Kept (server-side user ID) | Used for anonymous session IDs |
| `tkinter` GUI | Replaced | HTML/CSS/JS is the new GUI |
| Raw TCP socket | Replaced | WebSocket over port 8765 |
| File dialog (`filedialog`) | Not implemented | Out of scope for MVP |
| Desktop window management | N/A | Browser handles windowing |

---

## Potential Extensions

These features are not in scope for v2.0 but are natural next steps:

- **Multiple rooms / channels** — add a `room` field to the message protocol
- **Private messages** — extend the protocol with `target_user_id`
- **TLS / WSS** — run the server behind nginx or Caddy for encrypted connections
- **Persistent history** — swap in SQLite or Redis for message storage
- **User avatars** — let users upload a profile image
- **Markdown in messages** — parse and render a safe subset of Markdown
- **Electron wrapper** — bundle `index.html` into a proper desktop app with title bar
