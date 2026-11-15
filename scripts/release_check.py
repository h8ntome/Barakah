"""Run a release check with a timestamped, hash-linked receipt; never records environment secrets."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time


def tree_hash(root):
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root).decode().split('\0')
    digest = hashlib.sha256()
    for name in sorted(set(paths) - {''}):
        path = root / name
        if path.is_file() and not path.is_symlink():
            digest.update(name.encode() + b'\0' + hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New receipt prefix (without extension)')
    parser.add_argument('--cwd', type=Path, default=Path.cwd())
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('command required after --')
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    log = output.with_suffix('.log')
    receipt = output.with_suffix('.json')
    if log.exists() or receipt.exists():
        parser.error('Refusing to overwrite an earlier check')
    cwd = args.cwd.resolve()
    root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd, text=True).strip())
    result = {'command': command, 'cwd': str(cwd), 'started_at': datetime.now(timezone.utc).isoformat(),
              'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              'source_tree_sha256_before': tree_hash(root), 'environment': platform.platform(),
              'python': platform.python_version(), 'log': log.name}
    start = time.monotonic()
    with log.open('x') as stream:
        try:
            proc = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT, timeout=args.timeout)
            result.update(exit_status=proc.returncode, outcome='PASS' if proc.returncode == 0 else 'FAIL')
        except subprocess.TimeoutExpired:
            result.update(exit_status=None, outcome='BLOCKED', reason='Check exceeded its time limit')
    result.update(ended_at=datetime.now(timezone.utc).isoformat(), seconds=round(time.monotonic()-start, 3),
                  source_tree_sha256_after=tree_hash(root), log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    print(log.read_text()[-4000:])
    return 0 if result['outcome'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
