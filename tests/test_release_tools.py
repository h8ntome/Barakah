"""Small regressions for release helpers, independent of the running application."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('demo_cli', ROOT / 'scripts/demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class ReleaseToolsTests(unittest.TestCase):
    def test_demo_origin_supports_both_launchers(self):
        for extra, expected in [([], 'http://localhost:5173'), (['--origin', 'http://127.0.0.1:8080'], 'http://127.0.0.1:8080')]:
            requests = []
            def respond(request, timeout):
                requests.append(request)
                return contextlib.closing(io.BytesIO(json.dumps({'access_token': 'synthetic-test-token'}).encode()))
            args = ['demo.py', '--url', 'http://127.0.0.1:8080', '--email', 'synthetic@example.com', '--delete-test-account', *extra]
            with patch.object(sys, 'argv', args), patch.object(demo.getpass, 'getpass', return_value='synthetic test password'), patch.object(demo.urllib.request, 'urlopen', side_effect=respond), contextlib.redirect_stdout(io.StringIO()):
                demo.main()
            self.assertEqual(len(requests), 2)
            self.assertTrue(all(r.headers['Origin'] == expected for r in requests))

    def test_capture_refuses_occupied_port_before_build_or_database(self):
        with socket.socket() as listener:
            try:
                listener.bind(('127.0.0.1', 8095))
                listener.listen()
            except OSError:
                pass  # An existing listener supplies the same collision condition.
            proc = subprocess.run([sys.executable, str(ROOT/'demo-video/scripts/prepare-demo.py'), 'start'], capture_output=True, text=True, timeout=5)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('Port 8095 is occupied', proc.stderr)
            self.assertNotIn('vite', proc.stdout)

    def test_check_receipt_preserves_failure_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            prefix = str(Path(tmp)/'receipt')
            cmd = [sys.executable, str(ROOT/'scripts/release_check.py'), '--output', prefix, '--', sys.executable, '-c', 'raise SystemExit(7)']
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=20)
            data = json.loads(Path(prefix+'.json').read_text())
            self.assertEqual(proc.returncode, 1)
            self.assertEqual((data['exit_status'], data['outcome']), (7, 'FAIL'))
            self.assertEqual(len(data['source_tree_sha256_before']), 64)
            self.assertNotEqual(subprocess.run(cmd, capture_output=True, cwd=ROOT).returncode, 0)


if __name__ == '__main__':
    unittest.main()
