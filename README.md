# AI Trading Ops — Personal Infrastructure

## Purpose
This project supports a personally-owned, 24/7 AI-model trading setup running
on Windows 11. It covers:

- **Google Workspace** — docs, sheets, and email used for trade logs, reports,
  and research notes.
- **Microsoft Edge** — browser environment for broker dashboards, exchange
  consoles, and Workspace access.
- **Windows 11 host** — the machine running the trading model/server
  continuously.
- **Home network (multiple SSIDs / WLAN, WLAN1, WLAN2)** — separate wireless
  networks used to segment traffic (e.g., trading server on an isolated SSID,
  general devices on another).
- **Local file agent** — a command-line tool (`agent.py`) for managing trading
  data on this machine: reading logs, creating new files/reports, compressing
  archives, and encrypting sensitive data at rest.

## Scope and boundaries
- Everything here operates **on the local machine only**. There is no
  remote-control, remote-monitoring, or cross-device command execution.
- Multi-device administration (if you manage more than one PC on your
  network) should go through **Windows-native tools**:
  - PowerShell Remoting (`Enter-PSSession`, `Invoke-Command`) for scripted
    admin tasks on machines you own and have credentials for.
  - Group Policy or Microsoft Intune/Endpoint Manager for fleet-wide config
    and security policy.
  - Windows Admin Center for a GUI-based multi-machine dashboard.
  These are Microsoft's supported, auditable paths for device administration
  and are safer/more maintainable than custom scripts.
- Network segmentation (separate SSIDs) is configured on your router/AP
  firmware directly — this repo doesn't need to touch that.

## Components
| Component | Role |
|---|---|
| `agent.py` | Local CLI: read, create, compress, encrypt files |
| Google Workspace | Reporting, shared logs, documentation |
| Edge | Browser access to broker/exchange platforms and Workspace |
| Trading server (Windows 11) | Runs the AI trading model continuously |

## Local Agent — Usage
See `agent.py`. Commands:
```
python agent.py read <file>
python agent.py create <file> --content "..."
python agent.py compress <output.zip> <file1> <file2> ...
python agent.py encrypt <file> --password "..."
python agent.py decrypt <file.enc> --password "..."
```

## Security notes
- Encryption uses a password-derived key (PBKDF2 + Fernet/AES). Keep your
  password somewhere safe — there is no recovery if it's lost.
- Encrypted/compressed archives are written locally; nothing is transmitted
  over the network by this tool.
- Treat trading credentials and API keys separately (e.g., environment
  variables or a secrets manager), never hard-coded into scripts.
