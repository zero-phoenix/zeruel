#!/usr/bin/env python3
import sys
import win32process

def launch_brave(url):
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
