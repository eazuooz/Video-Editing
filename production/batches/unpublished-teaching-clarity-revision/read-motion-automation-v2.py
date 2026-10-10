import json
from pathlib import Path
values={}
for line in Path('C:/Users/eazuo/.codex/automations/24/automation.toml').read_text('utf-8').splitlines():
    if '=' in line:
        key,value=line.split('=',1)
        values[key.strip()]=json.loads(value.strip())
print(json.dumps(values,ensure_ascii=False))
