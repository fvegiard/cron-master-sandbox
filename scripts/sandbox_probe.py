"""Verify Linux container boundaries before running synthetic tests."""
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
status=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
mounts=[line.split() for line in Path('/proc/mounts').read_text().splitlines()]
root_ro=any(p[1]=='/' and 'ro' in p[3].split(',') for p in mounts)
checks={'non_root':os.getuid()!=0,'root_filesystem_read_only':root_ro,'capabilities_dropped':int(status['CapEff'].strip(),16)==0,'no_new_privileges':status['NoNewPrivs'].strip()=='1','no_docker_socket':not Path('/var/run/docker.sock').exists(),'no_user_home_mount':not Path('/host').exists(),'no_injected_credentials':not any(os.environ.get(k) for k in ('GITHUB_TOKEN','GH_TOKEN','OPENAI_API_KEY','AWS_SECRET_ACCESS_KEY'))}
try:
    with socket.create_connection(('1.1.1.1',443),timeout=1): checks['outbound_connection_denied']=False
except OSError: checks['outbound_connection_denied']=True
scratch=Path('/tmp/cron-master-write-probe'); scratch.write_text('synthetic'); checks['tmp_writable']=scratch.read_text()=='synthetic'; scratch.unlink()
try:
    Path('/app/write-probe').write_text('should not write'); checks['app_writes_denied']=False
except OSError: checks['app_writes_denied']=True
print(json.dumps({'scope':'linux-container-boundary-probe','checks':checks,'passed':all(checks.values())}),flush=True)
if not all(checks.values()): raise SystemExit(1)
proc=subprocess.run([sys.executable,'scripts/run_ci.py'],timeout=180)
raise SystemExit(proc.returncode)
