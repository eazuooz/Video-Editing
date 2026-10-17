"""Native-frame teaching crops; raw originals remain preserved with provenance."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[4];L=R/'projects/making-game-sequels/production/local/reference-preserving-v2';a=L/'assets'
rows=[]
for name,sec in [('oatchi-before-focus',333.5),('oatchi-work-focus',336.5),('oatchi-result-focus',348)]:
 out=a/(name+'.png')
 if not out.exists():subprocess.run(['ffmpeg','-v','error','-ss',str(sec),'-i',str(L/'media/pikmin4-day2.mp4'),'-vf','crop=1000:800:600:50','-frames:v','1',str(out)],check=True)
 rows.append(dict(name=name,source='pikmin4-day2',sourceTime=sec,crop=[600,50,1000,800],purpose='enlarge pots, companion and resulting items for mobile explanation; original aspect of crop retained',role='explanation, not actual-footage seconds'))
(a/'focus-provenance.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Three targeted screenshots prepared without stretching or altering scene contents.')
