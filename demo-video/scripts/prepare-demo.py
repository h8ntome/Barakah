#!/usr/bin/env python3
"""Own isolated demo processes; never touch the default DB or teammate servers."""
import json, os, pathlib, signal, socket, subprocess, sys, time, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[2]
VIDEO = ROOT / 'demo-video'
RUNTIME = VIDEO / '.runtime'
RUNTIME.mkdir(exist_ok=True, mode=0o700)
PYTHON = ROOT / 'backend/.venv/bin/python'

def start(name, args, cwd, env):
    pidfile = RUNTIME / f'{name}.pid'
    if pidfile.exists():
        try:
            os.kill(int(pidfile.read_text()), 0)
            raise RuntimeError(f'{name}: already running; reuse it explicitly or stop only the owned process first')
        except ProcessLookupError:
            pass
    with (RUNTIME / f'{name}.log').open('ab') as log:
        p = subprocess.Popen(args, cwd=cwd, env=env, stdout=log, stderr=log,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    pidfile.write_text(str(p.pid))
    print(f'{name}: started pid {p.pid}')
    return p

action = sys.argv[1] if len(sys.argv) > 1 else 'start'
if action == 'stop':
    for name in ['app', 'studio']:
        p = RUNTIME / f'{name}.pid'
        if p.exists():
            pid = int(p.read_text())
            command = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True).stdout
            # Only stop a matching process owned by this script.
            if ('uvicorn app.main:app' in command and '--port 8095' in command) or ('remotion' in command and '3095' in command):
                os.killpg(pid, signal.SIGTERM)
            p.unlink()
    sys.exit()
assert action in ('start', 'studio'), 'Use start, studio or stop'
env = os.environ.copy()
if action == 'start':
    # Fail before building or migrating if another process owns the capture port.
    with socket.socket() as probe:
        try:
            probe.bind(('127.0.0.1', 8095))
        except OSError:
            raise SystemExit('Port 8095 is occupied; refusing to reuse an unverified app.') from None
    env.update(DATABASE_URL=f'sqlite:///{RUNTIME}/demo.sqlite', AI_MODE='unavailable',
               ALLOWED_ORIGINS='http://127.0.0.1:8095,http://localhost:8095',
               FRONTEND_DIST=str(RUNTIME / 'app-dist'), ENVIRONMENT='development',
               COOKIE_SECURE='false', VITE_API_BASE_URL='/api/v1')
    subprocess.run(['npm', 'run', 'build', '--', '--outDir', str(RUNTIME / 'app-dist')], cwd=ROOT/'barakah-ui', env=env, check=True)
    subprocess.run([str(PYTHON), '-m', 'alembic', 'upgrade', 'head'], cwd=ROOT/'backend', env=env, check=True)
    process = start('app', [str(PYTHON), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8095', '--no-access-log'], ROOT/'backend', env)
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError('Owned app exited before readiness; inspect .runtime/app.log')
        try:
            with urllib.request.urlopen('http://127.0.0.1:8095/api/v1/health', timeout=2) as r:
                assert r.status == 200
                if process.poll() is not None:
                    raise RuntimeError('Health response did not come from a running owned app')
                print('App healthy:', r.read().decode()); break
        except OSError:
            time.sleep(1)
    else:
        raise RuntimeError('App failed readiness; inspect .runtime/app.log')
else:
    start('studio', ['node', 'node_modules/@remotion/cli/remotion-cli.js', 'studio', '--port', '3095'], VIDEO, env)
