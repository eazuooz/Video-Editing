"""Version the previous analytic compositor; never edit accepted source in place."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'revision-game-subjects-20261115'
def main():
 s=(PREV/'subject_revision.py').read_text(encoding='utf8')
 def replace(a,b):
  nonlocal s
  assert a in s,a[:160];s=s.replace(a,b)
 replace("WORK=Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingWork/game-math-subjects-20261115-final'","WORK=HERE/'local/work'")
 replace("if eid=='M24' and s['scene'] in ('010','015'):asset='forza'","if eid=='M24' and s['scene'] in ('010','015'):asset='kart'\n   if asset in ('kart','forza') and l['motion']['parameters'].get('kind')==4:asset='forza'\n   elif eid=='M26':asset='kart'")
 replace("else:height=170 if asset in ('mario','kart') else 140","else:height=170 if asset=='mario' else 105 if asset in ('kart','beamng') else 180")
 replace("cmds=[];last=None;af=ASSETS[asset]", "cmds=[];facecmd=[];last=None;af=ASSETS[asset]")
 replace("width=round(iw*height/ih);width+=width%2;height+=height%2", "width=round(iw*height/ih);width+=width%2;height+=height%2\n  animated=(asset=='mario' and mode=='motion') or (asset=='forza' and mode=='motion')")
 replace("'Forza Horizon 5 · 코너링을 단순화한 모형'", "'Forza Horizon 5 · 위쪽 시점의 원운동 모형'")
 replace("sy=round(cy-height*.55)","sy=round(cy-height*.55)") if 'sy=round(cy-height*.55)' in s else None
 replace("sx=round(cx-width*.5);sy=round(cy-height*.55)","sx=round(cx-width*.5);sy=round(cy-height*.55)\n    if asset=='forza' and mode=='motion':sy=round(cy-height*.5)\n    if animated:\n     vv=motion.raw(q['model'],q['velocity'])\n     # Upright running characters use horizontal facing, including during descent.\n     if asset=='mario':\n      face=(1 if vv[0]<0 else 0) if abs(vv[0])>1e-8 else (lastface if 'lastface' in locals() else 0)\n      lastface=face\n      facecmd.append(f'{max(0,sec-.0001):.6f} hflip@face{j} enable {face};')\n     else:\n      # The high-angle source nose is up. Positive rotate angles turn clockwise.\n      angle=math.atan2(-vv[1],vv[0])+math.pi/2\n      facecmd.append(f'{max(0,sec-.0001):.6f} rotate@face{j} angle {angle:.9f};')")
 replace("extra.append(dict(asset=asset,mode=mode,file=af['file']", "(p/f'face-{j}.txt').write_text('\\n'.join(facecmd)+'\\n',encoding='utf8')\n  extra.append(dict(animated=animated,asset=asset,mode=mode,file=af['file']")
 replace("inputs+=['-i',item['file']];j=item['j']", "inputs+=(['-loop','1','-framerate','60'] if item.get('animated') else [])+['-i',item['file']];j=item['j']")
 replace("chain.append(f'[{n}:v]scale={item[\"width\"]}:{item[\"height\"]},format=rgba[sprite{j}]')", "face=''\n  if item.get('animated'):\n   operation=f'hflip@face{j}=enable=0' if item['asset']=='mario' else f'rotate@face{j}=angle=0:ow=iw:oh=ih:c=black@0'\n   face=f',setpts=PTS+{origin}/TB,sendcmd=f=face-{j}.txt,'+operation\n  chain.append(f'[{n}:v]scale={item[\"width\"]}:{item[\"height\"]},format=rgba{face}[sprite{j}]')")
 replace("postboard.text(565,330,'정점 · t=1 s'", "postboard.text(565,280,'정점 · t=1 s'")
 # Add a meaningful facing key to every motion annotation, not decorative UI.
 replace("board.write(p/'identity.ass')", "for t in ts:\n  a=max(origin,t['start']);z=min(end,t['end'])\n  if z<=a:continue\n  if t['asset']=='forza' and t['mode']=='motion':note='차량 앞쪽 = 접선 방향 · v / 중심 쪽 = a'\n  elif t['asset'] in ('kart','beamng') and t['mode'] in ('motion','mechanics'):\n   note=('차체 자세 유지 · 아래쪽 +y · 이동 방향은 v' if t['lesson']['motion'].get('positiveYIsDown') else '차체 앞쪽 → +x · 이동 방향은 v로 표시') if t['mode']=='motion' else '차체 방향 고정 · 이동·힘의 방향은 따로 표시'\n  elif t['asset']=='mario' and t['mode']=='motion':note='좌우 진행에 맞춘 시선 · 점프 중에도 몸은 세움'\n  else:continue\n  board.rectangle(1190,178,715,50,a,z)\n  board.text(1200,181,note,a,z,TEAL,29,width=690)\n board.write(p/'identity.ass')")
 (HERE/'base_renderer.py').write_text(s,encoding='utf8')
if __name__=='__main__':main()
