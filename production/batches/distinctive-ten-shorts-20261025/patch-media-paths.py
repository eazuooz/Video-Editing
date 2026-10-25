"""Accept only this batch's verified C: junction targets in copied mix tools."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]
batch=json.loads((Path(__file__).parent/'batch.json').read_text(encoding='utf8'))
for row in batch['projects']:
 p=R/'projects'/row['slug']/'production/finish-audio.py'
 text=p.read_text(encoding='utf8')
 text=text.replace("    return Path(path).resolve().relative_to(R).as_posix()", "    path=Path(path).absolute()\n    if path.is_relative_to(R):return path.relative_to(R).as_posix()\n    resolved=path.resolve()\n    owned=Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025').resolve()\n    if resolved.is_relative_to(owned):return resolved.as_posix()\n    raise ValueError('Unregistered external media path: '+str(path))")
 text=text.replace("if any(not p.resolve().is_relative_to(R.resolve()) for p,_ in SOURCES.values()):", "if any(not (p.resolve().is_relative_to(R.resolve()) or p.resolve().is_relative_to(Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025').resolve())) for p,_ in SOURCES.values()):")
 p.write_text(text,encoding='utf8')
print('Updated ten copied mixer path guards; no other projects changed.')
