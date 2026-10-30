"""Measured continuous-voice timing; no speculative video cuts or media changes."""
import json, math
from pathlib import Path
H=Path(__file__).resolve().parent
V=H.parent/'local/grid-v1/voice'

def main():
 timing=json.loads((V/'source-scene-timings.json').read_text('utf8'))
 scenes=timing['scenes']
 samples=sum(s['samples'] for s in scenes)
 body=math.ceil(samples/48000*60)
 plan={'slug':'animation-assigning','revision':'grid-v1','fps':60,'width':1920,'height':1080,
       'introFrames':120,'outroFrames':600,'bodyFrames':body,'totalFrames':body+720,
       'captionAliases':{},'continuousSourceSeconds':samples/48000,
       'scope':'Caption timing only; final EDL assembled separately from reviewed actual shots.',
       'scenes':[{'id':s['id'],'voiceStart':2+s['sourceOrigin'],
                  'startFrame':120+round(s['sourceOrigin']*60),
                  'endFrame':120+(round((s['sourceOrigin']+s['duration'])*60) if i<len(scenes)-1 else body)}
                 for i,s in enumerate(scenes)]}
 (H/'caption-timing-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Measured body frames:',body,'total:',body+720)

if __name__=='__main__':main()
