"""Small bounded HTTP probe, not a production capacity benchmark.

BARAKAH_LOAD_URL=http://127.0.0.1:8000/api/v1/health python3 tests/load_smoke.py
Optionally set BARAKAH_ACCESS_TOKEN to probe an authenticated read endpoint.
"""
import concurrent.futures
import json
import os
import statistics
import time
import urllib.error
import urllib.request


def main():
    url = os.environ.get("BARAKAH_LOAD_URL", "http://127.0.0.1:8000/api/v1/health")
    token = os.environ.get("BARAKAH_ACCESS_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    def request(_):
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10) as response:
                response.read()
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        except (urllib.error.URLError, TimeoutError):
            status = 0
        return status, (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(request, range(50)))
    elapsed = time.perf_counter() - start
    durations = sorted(duration for _, duration in results)
    failed = sum(status != 200 for status, _ in results)
    print(json.dumps({
        "requests": 50, "concurrency": 4, "passed": 50 - failed, "failed": failed,
        "elapsed_seconds": round(elapsed, 3),
        "median_ms": round(statistics.median(durations), 3),
        "p95_ms": round(durations[47], 3), "max_ms": round(max(durations), 3),
        "scope": "Local bounded read probe only; no production capacity claim",
    }, indent=2))
    return bool(failed)


if __name__ == "__main__":
    raise SystemExit(main())
