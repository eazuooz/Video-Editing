"""Generate complete revised scene contexts without rebuilding an incomplete master."""
from pathlib import Path
import argparse,json,sys,hashlib
from dataclasses import replace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qwen3-tts'))
import render_narration as renderer
p=argparse.ArgumentParser();p.add_argument('--scenes',required=True);a=p.parse_args()
ids=set(a.scenes.split(','));renderer.configure_project('ai-game-development-human-craft')
renderer.load_tts_dependencies()
pronunciations={'Unity Spark':'유니티 스파크','UE6':'언 리얼 엔진 식스','MCP':'엠씨피','UV':'유브이','UDK':'유디케이','NFT':'엔에프티','Verse':'벌스','AI':'에이아이','언리얼':'언 리얼','100골드':'백 골드','70골드':'칠십 골드','30골드':'삼십 골드','20골드':'이십 골드'}
items=[]
for item in renderer.build_render_items(renderer.load_jobs()):
 if item.key.split('-')[0] not in ids:continue
 text=item.text
 for x,y in pronunciations.items():text=text.replace(x,y)
 items.append(replace(item,text=text))
# Tail diagnostics identify candidates; content review, including the first
# syllables, decides whether a targeted second take is necessary.
renderer.MAX_RENDER_ATTEMPTS=1
renderer.torch.manual_seed(20261015)
renderer.render_chunks(items,1)
