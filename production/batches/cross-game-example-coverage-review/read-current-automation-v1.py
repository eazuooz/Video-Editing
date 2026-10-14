import json
from pathlib import Path

text=Path('C:/Users/eazuo/.codex/automations/24/automation.toml').read_text(encoding='utf-8-sig')
data={}
for line in text.splitlines():
    if ' = ' in line:
        key,value=line.split(' = ',1)
        try:
            data[key]=json.loads(value)
        except json.JSONDecodeError:
            pass
print(json.dumps(data,ensure_ascii=False))
