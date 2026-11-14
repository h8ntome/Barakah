"""Non-invasive hardware snapshot. No credentials or process command arguments."""
import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
import psutil
from common import ROOT, now, save, versions

def command(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=8)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None

def inspect():
    vm = psutil.virtual_memory()
    disk = shutil.disk_usage(ROOT)
    gpu = {"available": False, "reason": "PyTorch not installed"}
    try:
        import torch
        gpu = {"available": torch.cuda.is_available(), "cuda": torch.version.cuda,
               "hip": torch.version.hip, "mps": torch.backends.mps.is_available()}
        if torch.cuda.is_available():
            free, total = torch.cuda.mem_get_info()
            gpu.update(name=torch.cuda.get_device_name(0), free_bytes=free, total_bytes=total,
                       bf16_supported=torch.cuda.is_bf16_supported())
    except ImportError as e:
        gpu = {"available": False, "reason": f"PyTorch import unavailable: {e}"}
    sysfs = {}
    for p in Path("/sys/class/drm").glob("card*/device/*"):
        if p.name.startswith("mem_info_") or p.name == "gpu_busy_percent":
            try:
                sysfs[str(p)] = p.read_text().strip()
            except OSError:
                pass
    cpu = command(["sysctl", "-n", "machdep.cpu.brand_string"]) if sys.platform == "darwin" else command(["lscpu"])
    active = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            if p.info["memory_info"] and p.info["memory_info"].rss > 200 * 1024**2:
                active.append({"pid": p.pid, "name": p.info["name"], "rss_bytes": p.info["memory_info"].rss})
        except psutil.Error:
            pass
    cache = Path.home() / ".cache/huggingface/hub"
    return {"timestamp": now(), "hostname": platform.node(), "os": platform.platform(),
            "cpu": cpu or platform.processor(), "logical_cores": psutil.cpu_count(),
            "physical_cores": psutil.cpu_count(logical=False), "cpu_utilization_percent": psutil.cpu_percent(interval=1),
            "load_average": list(psutil.getloadavg()), "ram_total_bytes": vm.total, "ram_available_bytes": vm.available,
            "disk_free_bytes": disk.free, "disk_total_bytes": disk.total, "gpu": gpu, "sysfs_gpu": sysfs,
            "nvidia_smi": command(["nvidia-smi"]), "versions": versions(),
            "lfm_caches": [str(p) for p in cache.glob("models--LiquidAI--LFM3*")],
            "active_memory_workloads": sorted(active, key=lambda p:p["rss_bytes"], reverse=True)[:12]}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=str(ROOT / "results/hardware/local.json"))
    args = p.parse_args()
    result = inspect()
    save(args.output, result)
    print(__import__("json").dumps(result, indent=2))
