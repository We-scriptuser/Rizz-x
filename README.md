# RIZZ-X — Consent-based Remote Support

RIZZ-X is a cross-platform, browser-based remote-support starter for Windows, Linux, and macOS hosts. A supported mobile/desktop browser can join as a viewer.

## Included
- Host-created, short-lived pairing PINs
- Host must explicitly click **Start screen sharing**
- Viewer can only view the shared screen; no hidden access, remote keyboard/mouse, shell, persistence, or background agent
- WebRTC peer-to-peer screen streaming
- LAN use, or internet use through a private VPN such as Tailscale/WireGuard
- Session expiry and basic rate limiting

## Requirements
- Python 3.10+
- Windows, Linux, or macOS
- Modern browser with `getDisplayMedia` support for the host (Chrome/Edge/Firefox; browser support varies)
- HTTPS is required by browsers for screen capture, except localhost. For LAN/internet use, put RIZZ-X behind a trusted HTTPS reverse proxy or use a VPN setup that provides HTTPS.

## Install and run (Windows PowerShell)
```powershell
cd RIZZ-X
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```
Open `http://127.0.0.1:8765` on the host computer.

## Install and run (Linux/macOS)
```bash
cd RIZZ-X
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

## LAN use
1. Connect both devices to the same trusted Wi-Fi/LAN.
2. Configure your firewall to allow the chosen port only on the private network.
3. Host opens the app using its LAN IP and port.
4. Viewer opens the same address and enters the PIN displayed by the host.

Do not expose port 8765 directly to the public internet.

## Internet use
Use a private overlay VPN such as Tailscale or WireGuard:
1. Install and sign in to the VPN on both devices.
2. Confirm both devices can reach each other over the VPN.
3. Open RIZZ-X using the host's VPN address.
4. Use HTTPS for screen capture. A VPN protects network reachability; it does not automatically make a plain HTTP origin secure for browser screen-capture APIs. Use a trusted HTTPS reverse proxy/certificate or a VPN solution with HTTPS certificates.

## Security notes
- The host controls when screen sharing starts and stops.
- Pairing PINs expire after 10 minutes and are single-use for the viewer.
- Sessions expire after 30 minutes.
- WebRTC uses DTLS-SRTP encryption for media in transit.
- The built-in STUN server helps peer connectivity. Some NATs require a TURN relay; this project intentionally does not bundle a public relay.
- Use only with devices and people who have explicitly authorized the session.
- This starter does not implement remote input, arbitrary command execution, file-system browsing, or unattended access.

## Troubleshooting
- If screen sharing is unavailable, use `localhost` or configure HTTPS. Browsers restrict screen capture on insecure origins.
- If the viewer stays on "Connecting", check VPN/LAN reachability and browser console messages. Some networks require a TURN server.
- If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again.
