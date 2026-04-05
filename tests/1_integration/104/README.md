# IEC 60870-5-104 Master – Linux TUI

A fully featured IEC 60870-5-104 master station for Linux with a live
ncurses terminal interface.

---

## Features

| Feature | Details |
|---------|---------|
| TCP connection | Non-blocking connect with automatic STARTDT handshake |
| General Interrogation | `gi` command – sends C_IC_NA_1 with QOI=20 |
| Double Command | `dc <ioa> <1\|2> [sel]` – sends C_DC_NA_1 (select/execute) |
| Spontaneous events | Parsed and displayed live with colour-coded COT |
| CP56Time2a | Decoded and shown in the Timestamp column |
| T1 / T2 / T3 timers | Automatic TESTFR keepalive, S-frame acknowledgement |
| I / S / U frames | Full send/receive with sequence number tracking |
| Event log | Ring buffer of 500 events; PageUp/PageDn scrolling |
| Command history | ↑↓ arrow keys to recall previous commands |

### Decoded ASDU types

- M_SP_NA_1 (1) – Single-point information
- M_DP_NA_1 (3) – Double-point information
- M_ST_NA_1 (5) – Step position
- M_BO_NA_1 (7) – Bitstring 32 bit
- M_ME_NA_1 (9) – Measured normalised value
- M_ME_NB_1 (11) – Measured scaled value
- M_ME_NC_1 (13) – Measured short float
- M_IT_NA_1 (15) – Integrated totals
- M_SP_TB_1 (30) – Single-point with CP56Time2a
- M_DP_TB_1 (31) – Double-point with CP56Time2a
- M_ME_TD_1 (34) – Normalised + time
- M_ME_TE_1 (35) – Scaled + time
- M_ME_TF_1 (36) – Short float + time
- M_EI_NA_1 (70) – End of initialisation
- C_IC_NA_1 (100) – GI confirmations
- C_DC_NA_1 (46) – Double command confirmations

Unknown types show the first 8 raw bytes in hex.

---

## Build

### Requirements

```
gcc  (any modern version)
ncurses development library
```

On Debian/Ubuntu:
```bash
sudo apt install build-essential libncurses-dev
```

On RHEL/Fedora/CentOS:
```bash
sudo dnf install gcc ncurses-devel
```

### Compile

```bash
make
```

---

## Usage

### Launch

```bash
# Interactive – enter connect command manually
./iec104_master

# Auto-connect on start
./iec104_master <ip> [port] [common-address]

# Examples
./iec104_master 192.168.1.10
./iec104_master 192.168.1.10 2404 1
./iec104_master 10.0.0.1 2404 100
```

### Commands

| Command | Description |
|---------|-------------|
| `connect <ip> [port=2404] [ca=1]` | Connect to RTU/IED |
| `disconnect` | Close connection |
| `gi` | Send General Interrogation |
| `dc <ioa> <1\|2> [sel=0]` | Double Command – 1=OFF, 2=ON, sel=1 for select-before-execute |
| `ca <value>` | Change Common Address used for commands |
| `clear` | Clear the event log |
| `quit` / `exit` | Quit the application |

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `PgUp` / `PgDn` | Scroll event log |
| `↑` / `↓` | Command history |
| `←` / `→` | Move cursor in command line |
| `Home` / `End` | Jump to start/end of command |
| `F5` / resize | Force redraw |
| `Ctrl+C` | Quit |

---

## Event log columns

```
#     – sequential event counter
Time  – local time of reception
Type  – ASDU type identifier name
COT   – cause of transmission
CA    – common address
IOA   – information object address
Value – decoded value (state, float, bitstring, etc.)
Quality – quality descriptor flags (IV, NT, SB, BL, OV)
Timestamp – CP56Time2a decoded (if present in ASDU)
```

### Colour coding

| Colour | Meaning |
|--------|---------|
| Yellow | Spontaneous (COT=3) |
| Magenta | Activation / Deactivation |
| Green | ActCon / DeactCon / ActTerm (confirmations) |
| White | Other (background scan, periodic, etc.) |

---

## Notes

- The master uses the default IEC 104 parameters:
  - T1 = 15 s (acknowledgement timeout)
  - T2 = 10 s (idle S-frame timeout)
  - T3 = 20 s (test frame interval)
  - W  = 8   (max un-acknowledged I-frames before sending S)
- All these can be changed in `iec104.h` defaults or directly in the `iec104_master_t` struct before connecting.
- The connection is non-blocking; the UI remains responsive while connecting.
- STARTDT_ACT is sent automatically upon successful TCP connect.

---

## File structure

```
iec104.h        – protocol constants, types, API
iec104.c        – master implementation (framing, parsing, timers)
main.c          – ncurses TUI + command processor
Makefile
README.md
```
