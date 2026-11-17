"""Finish local-only verification once this exact tutorial render is available."""
from pathlib import Path
import json,time,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];L=H/'local/full-video-v4'
receipt=H/'full-video-delivery.json'
while True:
    d=json.loads(receipt.read_text('utf-8'))
    if d.get('stage')=='rendered-internal-QA-pending' and '/full-video-v4/' in d['outputs'][1]['path'].replace('\\','/'):
        break
    time.sleep(8)
while (R/'shared/output/GPU_HANDOFF.json').exists():time.sleep(8)
for name in ['verify-film.py','prepare-wiki-frames.py']:
    subprocess.run(['python','-X','utf8','-u',str(H/name)],cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
from PIL import Image,ImageDraw
frames=json.loads((H/'companion-frames.json').read_text('utf-8'));im=Image.new('RGB',(1440,1000),'#101812')
for i,f in enumerate(frames):
    a=Image.open(f['imagePath']);a.thumbnail((480,250));x=(i%3)*480;y=(i//3)*250;im.paste(a,(x,y));ImageDraw.Draw(im).text((x+5,y+5),f['name'],fill='white')
im.save(L/'wiki-contact.jpg')
print('Tutorial v3 technical QA and final-master wiki frames prepared.',flush=True)
