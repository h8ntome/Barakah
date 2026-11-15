"""Record shared-host contention without reading process arguments or interrupting jobs."""
import argparse
import json
import subprocess
import time
from pathlib import Path
import psutil
from common import now


def sample():
    processes=[]
    for p in psutil.process_iter(['pid','name','memory_info','cpu_times']):
        try:
            info=p.info
            processes.append({'pid':info['pid'],'name':info['name'],'rss_bytes':info['memory_info'].rss,
                              'cpu_seconds':sum(info['cpu_times'][:2])})
        except (psutil.AccessDenied,psutil.NoSuchProcess):
            pass
    return {'timestamp':now(),'load_average':list(__import__('os').getloadavg()),
            'memory_available_bytes':psutil.virtual_memory().available,
            'gpu_busy_percent':{str(p):p.read_text().strip() for p in Path('/sys/class/drm').glob('card*/device/gpu_busy_percent')},
            'largest_processes':sorted(processes,key=lambda x:x['rss_bytes'],reverse=True)[:12]}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--units',nargs='+',required=True)
    a=p.parse_args()
    with a.output.open('x') as f:
        for _ in range(720):
            f.write(json.dumps(sample())+'\n');f.flush()
            if not any(subprocess.run(['systemctl','--user','is-active','--quiet',u]).returncode==0 for u in a.units):break
            time.sleep(10)
