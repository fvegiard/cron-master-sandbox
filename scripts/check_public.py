"""Check tracked publication paths and obvious secret/private-path patterns."""
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'); names=[n for n in names if n]
blocked_paths=('.env','.agents/','.codex/','state/','node_modules/','.venv')
patterns=[re.compile(r'[A-Za-z]:\\Users\\(?!Public\\)[^\s"\']+'),re.compile(r'\b(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_-]{20,}'),re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')]
findings=[]
for name in names:
    p=ROOT/name
    if name.startswith(blocked_paths) or p.suffix in ('.sqlite','.db','.log') or '.bak' in name: findings.append({'file':name,'reason':'private/runtime path'})
    if p.is_symlink(): findings.append({'file':name,'reason':'symlink'})
    try: text=p.read_text(encoding='utf-8')
    except UnicodeDecodeError: findings.append({'file':name,'reason':'unexpected binary'}); continue
    if any(rx.search(text) for rx in patterns): findings.append({'file':name,'reason':'secret/private-path pattern'})
print(json.dumps({'tracked_files':len(names),'findings':findings,'scope':'pattern-and-path-screen; not absolute secret absence proof'}))
raise SystemExit(bool(findings))
