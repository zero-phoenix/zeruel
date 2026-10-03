#!/usr/bin/env python3
import re
import sys
import win32process

ALLOWED = re.compile(r"https://zeruel-synthetic-probe\.onrender\.com/[A-Za-z0-9#=&%._@+/-]*")


def launch_brave(url):
    # Solo la URL de la sonda y sin comillas ni espacios: no puede inyectar argumentos a Brave.
    if not ALLOWED.fullmatch(url):
        raise SystemExit("URL no permitida")
    brave_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    si = win32process.STARTUPINFO()
    si.lpDesktop = r"WinSta0\Default"
    cmd = f'"{brave_exe}" {url}'
    hp, ht, pid, tid = win32process.CreateProcess(None, cmd, None, None, False, 0, None, None, si)
    return pid

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://zeruel-synthetic-probe.onrender.com/"
    pid = launch_brave(url)
    print(f"Launched Brave with WinSta0\\Default, PID: {pid}")
