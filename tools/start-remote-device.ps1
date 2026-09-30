param([switch]$AllowAdditionalProcesses, [switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
if (!$AllowAdditionalProcesses -and !$CheckOnly) { throw 'Falta permiso explicito para procesos adicionales.' }
$zrNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$zrNpx = Join-Path $env:USERPROFILE '.zeruel-tools\npm-10.9.4\package\bin\npx-cli.js'
foreach ($zrFile in @($zrNode, $zrNpx)) {
    if (!(Test-Path -LiteralPath $zrFile -PathType Leaf)) { throw 'Falta Node o npm portable.' }
}
$zrChromePaths = @(
    'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),
    'C:\Program Files\Chromium\Application\chrome.exe',
    'C:\Program Files (x86)\Chromium\Application\chrome.exe'
)
if (!($zrChromePaths | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })) {
    throw 'Chrome instalado no encontrado. Detener para evitar una descarga adicional del servidor MCP.'
}
function Assert-ZrFreeMemory([double]$AvailableBytes, [double]$RequiredBytes) {
    if ($AvailableBytes -lt $RequiredBytes) {
        throw ('RAM libre insuficiente: {0} MiB disponibles; se requieren {1} MiB; faltan {2} MiB. No iniciar.' -f
            [Math]::Floor($AvailableBytes / 1MB), [Math]::Ceiling($RequiredBytes / 1MB),
            [Math]::Ceiling(($RequiredBytes - $AvailableBytes) / 1MB))
    }
}
# One initial WMI read protects the small native-helper compilation; no WMI polling.
$zrInitial = Get-CimInstance -Query 'SELECT FreePhysicalMemory,TotalVisibleMemorySize FROM Win32_OperatingSystem'
$zrMinFree = [Math]::Max(768MB, [double]$zrInitial.TotalVisibleMemorySize * 1KB * 0.15)
Assert-ZrFreeMemory -AvailableBytes ([double]$zrInitial.FreePhysicalMemory * 1KB) -RequiredBytes ($zrMinFree + 512MB)
if (!('ZeruelResourceGuardV1' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
public sealed class ZeruelResourceGuardV1 : IDisposable {
    [StructLayout(LayoutKind.Sequential)] struct FT { public uint Low, High; }
    [StructLayout(LayoutKind.Sequential)] struct MS {
        public uint Length, Load;
        public ulong TotalPhysical, AvailablePhysical, TotalPage, AvailablePage, TotalVirtual, AvailableVirtual, ExtendedVirtual;
    }
    [StructLayout(LayoutKind.Sequential)] struct Basic {
        public long ProcessTime, JobTime;
        public uint Flags;
        public UIntPtr MinWS, MaxWS;
        public uint ActiveProcesses;
        public UIntPtr Affinity;
        public uint Priority, Scheduling;
    }
    [StructLayout(LayoutKind.Sequential)] struct IO { public ulong ReadOps, WriteOps, OtherOps, ReadBytes, WriteBytes, OtherBytes; }
    [StructLayout(LayoutKind.Sequential)] struct Limits {
        public Basic Basic;
        public IO Counters;
        public UIntPtr ProcessMemory, JobMemory, PeakProcessMemory, PeakJobMemory;
    }
    [StructLayout(LayoutKind.Sequential)] struct CpuLimits { public uint Flags, Rate; }
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)] struct Startup {
        public uint Size;
        public string Reserved, Desktop, Title;
        public uint X, Y, Width, Height, CharsX, CharsY, Fill, Flags;
        public ushort Show, ReservedSize;
        public IntPtr ReservedData, Input, Output, Error;
    }
    [StructLayout(LayoutKind.Sequential)] struct PI { public IntPtr Process, Thread; public uint Pid, Tid; }
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool GetSystemTimes(out FT idle, out FT kernel, out FT user);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool GlobalMemoryStatusEx(ref MS status);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern IntPtr CreateJobObject(IntPtr attrs, string name);
    [DllImport("kernel32.dll", EntryPoint="SetInformationJobObject", SetLastError=true)] static extern bool SetLimits(IntPtr job, int kind, ref Limits info, uint size);
    [DllImport("kernel32.dll", EntryPoint="SetInformationJobObject", SetLastError=true)] static extern bool SetCpu(IntPtr job, int kind, ref CpuLimits info, uint size);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool QueryInformationJobObject(IntPtr job, int kind, IntPtr buffer, uint size, out uint returned);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool IsProcessInJob(IntPtr process, IntPtr job, out bool member);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool TerminateJobObject(IntPtr job, uint code);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool CreateProcess(string app, StringBuilder cmd, IntPtr pa, IntPtr ta, bool inherit, uint flags, IntPtr env, string cwd, ref Startup startup, out PI info);
    [DllImport("kernel32.dll", SetLastError=true)] static extern uint ResumeThread(IntPtr thread);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool TerminateProcess(IntPtr process, uint code);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool GetExitCodeProcess(IntPtr process, out uint code);
    [DllImport("kernel32.dll", SetLastError=true)] static extern uint WaitForSingleObject(IntPtr handle, uint timeout);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool CloseHandle(IntPtr handle);
    IntPtr job, process;
    static void Check(bool ok) { if (!ok) throw new Win32Exception(Marshal.GetLastWin32Error()); }
    static ulong Ticks(FT t) { return ((ulong)t.High << 32) | t.Low; }
    public static ulong[] Memory() {
        MS m = new MS(); m.Length = (uint)Marshal.SizeOf(typeof(MS)); Check(GlobalMemoryStatusEx(ref m));
        return new ulong[] { m.TotalPhysical, m.AvailablePhysical };
    }
    public static ulong[] Cpu() {
        FT idle, kernel, user; Check(GetSystemTimes(out idle, out kernel, out user));
        return new ulong[] { Ticks(idle), Ticks(kernel) + Ticks(user) };
    }
    public static string Quote(string value) {
        StringBuilder b = new StringBuilder("\""); int slashes = 0;
        foreach (char c in value) {
            if (c == '\\') { slashes++; continue; }
            if (c == '"') { b.Append('\\', slashes * 2 + 1); b.Append('"'); }
            else { b.Append('\\', slashes); b.Append(c); }
            slashes = 0;
        }
        b.Append('\\', slashes * 2); b.Append('"'); return b.ToString();
    }
    public ZeruelResourceGuardV1(uint percent, ulong bytes) {
        if (percent < 1 || percent > 100) throw new ArgumentOutOfRangeException("percent");
        if (Marshal.SizeOf(typeof(MS)) != 64 || Marshal.SizeOf(typeof(IO)) != 48 ||
            Marshal.SizeOf(typeof(Basic)) != (IntPtr.Size == 8 ? 64 : 48) ||
            Marshal.SizeOf(typeof(Limits)) != (IntPtr.Size == 8 ? 144 : 112) ||
            Marshal.SizeOf(typeof(Startup)) != (IntPtr.Size == 8 ? 104 : 68))
            throw new InvalidOperationException("Unsupported native layout");
        job = CreateJobObject(IntPtr.Zero, null); Check(job != IntPtr.Zero);
        try {
            Limits limits = new Limits(); limits.Basic.Flags = 0x200 | 0x2000; limits.JobMemory = new UIntPtr(bytes);
            Check(SetLimits(job, 9, ref limits, (uint)Marshal.SizeOf(typeof(Limits))));
            CpuLimits cpu = new CpuLimits(); cpu.Flags = 1 | 4; cpu.Rate = percent * 100;
            Check(SetCpu(job, 15, ref cpu, (uint)Marshal.SizeOf(typeof(CpuLimits))));
        } catch { Dispose(); throw; }
    }
    public void Start(string executable, string[] args, string cwd) {
        if (process != IntPtr.Zero) throw new InvalidOperationException("Already started");
        StringBuilder cmd = new StringBuilder(Quote(executable));
        foreach (string a in args) cmd.Append(" ").Append(Quote(a));
        Startup s = new Startup(); s.Size = (uint)Marshal.SizeOf(typeof(Startup)); PI p;
        // Same console, no inherited handles. Assign while suspended, then resume.
        Check(CreateProcess(executable, cmd, IntPtr.Zero, IntPtr.Zero, false, 4, IntPtr.Zero, cwd, ref s, out p));
        try {
            Check(AssignProcessToJobObject(job, p.Process));
            if (ResumeThread(p.Thread) == UInt32.MaxValue) Check(false);
            process = p.Process;
        } catch { TerminateProcess(p.Process, 125); CloseHandle(p.Process); throw; }
        finally { CloseHandle(p.Thread); }
    }
    public bool Running {
        get { if (process == IntPtr.Zero) return false;
            uint state = WaitForSingleObject(process, 0); if (state == UInt32.MaxValue) Check(false); return state == 258; }
    }
    public uint ExitCode { get { uint c; Check(GetExitCodeProcess(process, out c)); return c; } }
    public long WorkingBytes() {
        int capacity = 32;
        while (capacity <= 4096) {
            IntPtr buffer = Marshal.AllocHGlobal(8 + IntPtr.Size * capacity);
            try {
                uint returned;
                if (!QueryInformationJobObject(job, 3, buffer, (uint)(8 + IntPtr.Size * capacity), out returned)) {
                    int error = Marshal.GetLastWin32Error(); if (error == 234) { capacity *= 2; continue; }
                    throw new Win32Exception(error);
                }
                int count = Marshal.ReadInt32(buffer, 4);
                if (count < 0 || count > capacity) throw new InvalidOperationException("Invalid job list");
                long total = 0;
                for (int i = 0; i < count; i++) {
                    int pid = checked((int)Marshal.ReadIntPtr(buffer, 8 + IntPtr.Size * i).ToInt64());
                    try { using (Process p = Process.GetProcessById(pid)) {
                        bool member; Check(IsProcessInJob(p.Handle, job, out member));
                        if (member) total += p.WorkingSet64;
                    } }
                    catch (ArgumentException) { /* exited */ }
                    catch (InvalidOperationException) { /* exited */ }
                }
                return total;
            } finally { Marshal.FreeHGlobal(buffer); }
        }
        throw new InvalidOperationException("Too many children");
    }
    public void Dispose() {
        if (job != IntPtr.Zero) { TerminateJobObject(job, 125); CloseHandle(job); job = IntPtr.Zero; }
        if (process != IntPtr.Zero) { CloseHandle(process); process = IntPtr.Zero; }
    }
}
'@
}
$zrMemory = [ZeruelResourceGuardV1]::Memory()
Assert-ZrFreeMemory -AvailableBytes $zrMemory[1] -RequiredBytes ($zrMinFree + 512MB)
Write-Host ('REAL local: RAM libre {0:N0} MiB; reserva {1:N0} MiB.' -f ($zrMemory[1] / 1MB), ($zrMinFree / 1MB))
Write-Host 'Grupo: CPU limitada al 40%; memoria comprometida limitada a 512 MiB.'
Write-Host 'Cada 3 s: detener solo nuestro grupo si falta reserva RAM o CPU global >85% durante 12 s.'
$zrProbe = [ZeruelResourceGuardV1]::new(40, 512MB)
$zrProbe.Dispose()
if ($CheckOnly) { Write-Host 'Comprobacion previa correcta; agente no iniciado.'; return }

function Invoke-ZrMonitored([string[]]$Arguments) {
    $zrMemory = [ZeruelResourceGuardV1]::Memory()
    Assert-ZrFreeMemory -AvailableBytes $zrMemory[1] -RequiredBytes ($zrMinFree + 512MB)
    $zrGuard = [ZeruelResourceGuardV1]::new(40, 512MB)
    try {
        $zrBefore = [ZeruelResourceGuardV1]::Cpu()
        $zrClock = [Diagnostics.Stopwatch]::StartNew()
        $zrBusySince = $null
        $zrPreviousSeconds = 0
        $zrGuard.Start($zrNode, $Arguments, $env:USERPROFILE)
        while ($zrGuard.Running) {
            Start-Sleep -Seconds 3
            $zrNow = [ZeruelResourceGuardV1]::Cpu()
            $zrElapsed = [double]$zrNow[1] - [double]$zrBefore[1]
            if ($zrElapsed -le 0) { throw 'No se pudo medir CPU. Detener grupo.' }
            $zrCpu = 100 * (1 - (([double]$zrNow[0] - [double]$zrBefore[0]) / $zrElapsed))
            $zrBefore = $zrNow
            $zrMemory = [ZeruelResourceGuardV1]::Memory()
            $zrWorking = $zrGuard.WorkingBytes()
            Write-Host ('REAL local: CPU {0:N0}% | RAM libre {1:N0} MiB | grupo {2:N0} MiB.' -f $zrCpu, ($zrMemory[1] / 1MB), ($zrWorking / 1MB))
            if ($zrMemory[1] -lt $zrMinFree -or $zrWorking -gt 512MB) { throw 'LIMITE RAM: detener solo nuestro grupo.' }
            if ($zrCpu -gt 85) {
                if ($null -eq $zrBusySince) { $zrBusySince = $zrPreviousSeconds }
                if ($zrClock.Elapsed.TotalSeconds - $zrBusySince -ge 12) { throw 'LIMITE CPU: detener solo nuestro grupo.' }
            } else { $zrBusySince = $null }
            $zrPreviousSeconds = $zrClock.Elapsed.TotalSeconds
        }
        if ($zrGuard.ExitCode -ne 0) { throw 'El proceso termino con error. No reintentar automaticamente.' }
    } finally { $zrGuard.Dispose() }
}
$zrCache = Join-Path $env:USERPROFILE '.zeruel-tools\remote-cache'
$zrOldPath = $env:Path
$zrOldSkip = $env:PUPPETEER_SKIP_DOWNLOAD
try {
    $env:Path = [IO.Path]::GetDirectoryName($zrNode) + ';' + $env:Path
    $env:PUPPETEER_SKIP_DOWNLOAD = 'true'
    Write-Host 'Preparando Desktop Commander 0.2.52 bajo vigilancia. Otras dependencias se instalan.'
    Invoke-ZrMonitored -Arguments @($zrNpx, '--yes', ('--cache=' + $zrCache), '--registry=https://registry.npmjs.org',
        '@wonderwhy-er/desktop-commander@0.2.52', 'remote', '--help')
    # Only one directory level, with fixed package paths; no recursive disk search.
    $zrIndexes = @()
    foreach ($zrDir in (Get-ChildItem -LiteralPath (Join-Path $zrCache '_npx') -Directory)) {
        $zrPackage = Join-Path $zrDir.FullName 'node_modules\@wonderwhy-er\desktop-commander'
        $zrManifest = Join-Path $zrPackage 'package.json'
        $zrIndex = Join-Path $zrPackage 'dist\index.js'
        if ((Test-Path -LiteralPath $zrManifest -PathType Leaf) -and (Test-Path -LiteralPath $zrIndex -PathType Leaf)) {
            $zrInfo = Get-Content -LiteralPath $zrManifest -Raw | ConvertFrom-Json
            if ($zrInfo.name -eq '@wonderwhy-er/desktop-commander' -and $zrInfo.version -eq '0.2.52') { $zrIndexes += $zrIndex }
        }
    }
    if ($zrIndexes.Count -ne 1) { throw 'No se encontro una unica instalacion verificada. Detener.' }
    Write-Host 'Autoriza en tu navegador. No compartas codigos, enlaces de autorizacion ni tokens.'
    Write-Host 'Consola abierta: Ctrl+C detiene nuestro grupo, sin apagar ni reiniciar el equipo.'
    # Direct launch leaves only agent + MCP, without a persistent npx wrapper.
    Invoke-ZrMonitored -Arguments @($zrIndexes[0], 'remote', '--no-persist-session', '--disable-no-sleep')
} finally {
    $env:Path = $zrOldPath
    if ($null -eq $zrOldSkip) { Remove-Item Env:PUPPETEER_SKIP_DOWNLOAD -ErrorAction SilentlyContinue }
    else { $env:PUPPETEER_SKIP_DOWNLOAD = $zrOldSkip }
}
