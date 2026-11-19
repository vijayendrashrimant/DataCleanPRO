using System.Diagnostics;
using System.Net;
using System.Runtime.InteropServices;

namespace DataCleanPro.Services;

/// <summary>
/// Manages the DataCleanPro FastAPI backend process.
///
/// Launch priority:
///   1. Bundled exe  → frontend/api/datacleanpro_api[.exe]
///   2. Bundled exe  → backend/dist/datacleanpro_api[.exe]
///   3. Python venv  → backend/venv/bin/python -m uvicorn main:app
///   4. System python3/python (last resort)
///
/// StartAsync returns immediately — polling runs in a background Task.
/// </summary>
public sealed class FastApiService : IHostedService, IDisposable
{
    private const int ApiPort   = 8765;
    private const int PollMs    = 500;
    private const int TimeoutMs = 60_000;   // 60 s — exe cold-start can be slow

    private readonly ILogger<FastApiService> _log;

    private static readonly HttpClient _pollClient = new()
    {
        Timeout = TimeSpan.FromMilliseconds(900),
    };

    private Process? _process;
    private bool     _disposed;

    public bool    IsRunning    { get; private set; }
    public string? StartupError { get; private set; }
    public bool    IsExeMode    { get; private set; }

    public FastApiService(ILogger<FastApiService> log) => _log = log;

    public Task StartAsync(CancellationToken ct)
    {
        try
        {
            var (exe, args, workDir, isExe) = ResolveLaunchInfo();
            IsExeMode = isExe;

            _log.LogInformation("[FastAPI] Mode={M} exe={E} args={A}", isExe ? "exe" : "python", exe, args);

            if (!File.Exists(exe) && !IsOnPath(exe))
            {
                StartupError = isExe
                    ? $"Executable not found:\n  {exe}\n\nBuild it first:\n  cd backend && python build_exe.py"
                    : $"Python not found at:\n  {exe}\n\nSet up venv:\n  cd backend && python setup_venv.py";
                _log.LogError("[FastAPI] {E}", StartupError);
                return Task.CompletedTask;
            }

            var psi = new ProcessStartInfo
            {
                FileName               = exe,
                Arguments              = args,
                UseShellExecute        = false,
                CreateNoWindow         = true,
                RedirectStandardOutput = true,
                RedirectStandardError  = true,
            };

            if (workDir != null)
                psi.WorkingDirectory = workDir;

            // Clear Python env vars that confuse PyInstaller's embedded interpreter
            if (isExe)
            {
                psi.Environment["PYTHONPATH"]              = "";
                psi.Environment["PYTHONHOME"]              = "";
                psi.Environment["PYTHONDONTWRITEBYTECODE"] = "1";
            }
            else
            {
                psi.Environment["PYTHONUNBUFFERED"] = "1";
            }

            _process = new Process { StartInfo = psi, EnableRaisingEvents = true };
            _process.OutputDataReceived += (_, e) => { if (e.Data != null) _log.LogDebug("[API] {L}", e.Data); };
            _process.ErrorDataReceived  += (_, e) => { if (e.Data != null) _log.LogDebug("[API] {L}", e.Data); };
            _process.Exited += (_, _) =>
            {
                if (!_disposed) { IsRunning = false; _log.LogWarning("[FastAPI] Exited unexpectedly"); }
            };

            _process.Start();
            _process.BeginOutputReadLine();
            _process.BeginErrorReadLine();

            _log.LogInformation("[FastAPI] PID={Pid} polling :8765 in background", _process.Id);
            _ = Task.Run(() => WaitReadyAsync(ct), ct);
        }
        catch (Exception ex)
        {
            StartupError = $"Failed to start API engine: {ex.Message}";
            _log.LogError(ex, "[FastAPI] Spawn failed");
        }

        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken _) { Kill(); return Task.CompletedTask; }
    public void Dispose() { if (_disposed) return; _disposed = true; Kill(); }

    // ── Launch resolution ────────────────────────────────────────────────────
    private (string exe, string args, string? workDir, bool isExe) ResolveLaunchInfo()
    {
        var baseDir = AppContext.BaseDirectory;
        var exeName = RuntimeInformation.IsOSPlatform(OSPlatform.Windows)
                      ? "datacleanpro_api.exe"
                      : "datacleanpro_api";

        // 1. Exe alongside the .NET output: frontend/bin/.../api/datacleanpro_api
        var exeSideBySide = Path.Combine(baseDir, "api", exeName);
        if (File.Exists(exeSideBySide))
            return (exeSideBySide, $"--port {ApiPort}", null, true);

        // 2. Exe in backend/dist/ (produced by build_exe.py)
        foreach (var root in ParentRoots(baseDir))
        {
            var exeDist = Path.Combine(root, "backend", "dist", exeName);
            if (File.Exists(exeDist))
                return (exeDist, $"--port {ApiPort}", null, true);
        }

        // 3. Python venv
        var backendDir = FindBackendDir(baseDir);

        string venvPy;
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            venvPy = Path.Combine(backendDir, "venv", "Scripts", "python.exe");
        else
        {
            venvPy = Path.Combine(backendDir, "venv", "bin", "python");
            if (!File.Exists(venvPy))
                venvPy = Path.Combine(backendDir, "venv", "bin", "python3");
        }

        if (File.Exists(venvPy))
            return (venvPy,
                    $"-m uvicorn main:app --host 127.0.0.1 --port {ApiPort} --log-level warning",
                    backendDir, false);

        // 4. System Python fallback
        var sysPy = RuntimeInformation.IsOSPlatform(OSPlatform.Windows) ? "python" : "python3";
        return (sysPy,
                $"-m uvicorn main:app --host 127.0.0.1 --port {ApiPort} --log-level warning",
                backendDir, false);
    }

    private static string FindBackendDir(string baseDir)
    {
        foreach (var root in ParentRoots(baseDir))
        {
            var bd = Path.Combine(root, "backend");
            if (Directory.Exists(bd)) return bd;
        }
        return Path.GetFullPath(Path.Combine(baseDir, "..", "..", "..", "..", "backend"));
    }

    private static IEnumerable<string> ParentRoots(string start)
    {
        yield return Path.GetFullPath(Path.Combine(start, "..", "..", "..", ".."));
        yield return Path.GetFullPath(Path.Combine(start, ".."));
        yield return start;
    }

    private static bool IsOnPath(string name)
    {
        // For bare names like "python3" check if they're resolvable
        if (Path.IsPathRooted(name)) return false;
        var paths = (Environment.GetEnvironmentVariable("PATH") ?? "").Split(Path.PathSeparator);
        var exts  = RuntimeInformation.IsOSPlatform(OSPlatform.Windows)
                    ? new[] { "", ".exe", ".cmd" }
                    : new[] { "" };
        return paths.SelectMany(p => exts.Select(e => Path.Combine(p, name + e))).Any(File.Exists);
    }

    // ── Health poll (background) ─────────────────────────────────────────────
    private async Task WaitReadyAsync(CancellationToken ct)
    {
        var elapsed = 0;
        while (elapsed < TimeoutMs && !ct.IsCancellationRequested)
        {
            try
            {
                var r = await _pollClient.GetAsync($"http://127.0.0.1:{ApiPort}/health", ct);
                if (r.StatusCode == HttpStatusCode.OK)
                {
                    IsRunning = true;
                    _log.LogInformation("[FastAPI] Ready :{Port} mode={M}", ApiPort, IsExeMode ? "exe" : "python");
                    return;
                }
            }
            catch (OperationCanceledException) { return; }
            catch { /* not ready yet */ }

            if (_process is { HasExited: true })
            {
                StartupError = $"API engine exited (code={_process.ExitCode}) before becoming ready." +
                               (IsExeMode ? "\nRebuild: cd backend && python build_exe.py --clean" : "");
                _log.LogError("[FastAPI] {E}", StartupError);
                return;
            }

            await Task.Delay(PollMs, ct).ConfigureAwait(false);
            elapsed += PollMs;
        }

        if (!IsRunning)
            StartupError = $"API engine not ready within {TimeoutMs / 1000}s on port {ApiPort}.";
    }

    // ── Kill process tree ────────────────────────────────────────────────────
    private void Kill()
    {
        if (_process == null) return;
        try
        {
            if (!_process.HasExited)
            {
                _process.Kill(entireProcessTree: true);
                if (!_process.WaitForExit(3000))
                {
                    _log.LogWarning("[FastAPI] WaitForExit timed out — force-killing");
                    try { _process.Kill(entireProcessTree: true); } catch { /* best effort */ }
                }
                _log.LogInformation("[FastAPI] Terminated");
            }
        }
        catch (Exception ex) { _log.LogWarning(ex, "[FastAPI] Kill error"); }
        finally { _process.Dispose(); _process = null; IsRunning = false; }
    }
}
