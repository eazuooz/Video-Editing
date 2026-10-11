"""Narration/caption-bearing current scene excerpts for direct moving review.

These use the current clip and final mix, and do not approve a full master.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,html
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/quaternion-four-game-v3/narrated-scene-review'
O.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--only');args=parser.parse_args()
ledger=O/'index.json';rows=read(ledger) if ledger.exists() else {}
for episode in ['foundations','calculations']:
    slug=f'game-math-quaternion-{episode}-v3';P=ROOT/'projects'/slug;m=read(P/'project.json');t=read(P/'production/timeline.json')
    audio=ROOT/m['paths']['audioMix'];ass=P/'script/final.ko.ass';assert audio.exists() and ass.exists()
    audio_digest=sha(audio);ass_digest=sha(ass)
    for slot in t['scenes']:
        if slot['preservedOriginal'] or (args.only and slot['id'] not in args.only.split(',')):continue
        ident=slot['id'];clip=ROOT/f'shared/output/{slug}/clips/{ident}.mp4';target=O/(ident+'.mp4')
        signature=dict(clipSha256=sha(clip),audioMixSha256=audio_digest,captionsAssSha256=ass_digest,start=slot['start'],frames=slot['frames'],seconds=slot['seconds'])
        if target.exists() and all(rows.get(ident,{}).get(k)==v for k,v in signature.items()) and rows[ident]['sha256']==sha(target):continue
        vf=f'setpts=PTS+{slot["start"]:.9f}/TB,ass={ass.relative_to(ROOT).as_posix()},setpts=PTS-STARTPTS'
        log=O/(ident+'-render.log')
        with log.open('w',encoding='utf8') as f:
            subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-threads','2','-i',str(clip),'-ss',str(slot['start']),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-vf',vf,'-t',str(slot['seconds']),'-frames:v',str(slot['frames']),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-threads','3','-c:a','aac','-b:a','192k','-movflags','+faststart',str(target)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        rows[ident]={**signature,'slug':slug,'sha256':sha(target),'file':target.name,'movingReviewApproved':False,'meaning':'Current scene pixels/actual measured narration/fixed KO captions; full-master decode/pixel check remains separate.'}
        ledger.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print('Prepared current narrated/captioned scene',ident,flush=True)
buttons=''.join(f'<button data-scene="{html.escape(k)}">{html.escape(k)} · {v["seconds"]:.2f}초</button>' for k,v in rows.items())
page='''<!doctype html><meta charset="utf-8"><title>쿼터니언 추가 장면 · 실제 내레이션과 고정 자막 검수</title><style>body{background:#222;color:white;font:16px sans-serif}button{padding:9px;margin:4px}video{display:block;width:min(100%,1120px)}pre{white-space:pre-wrap}</style><h1>추가 장면의 실제 음성·자막·움직이는 표시</h1><p>원래 속도1x, 현재 파일 해시 기록. 전체 완성본 검수는 별도입니다.</p>'''+buttons+'''<video controls id="v"></video><p id="now"></p><pre id="proof"></pre><script>const rows='''+json.dumps(rows,ensure_ascii=False)+''';const v=document.querySelector('#v');let active;const proofs=[];for(const b of document.querySelectorAll('button'))b.onclick=()=>{active=b.dataset.scene;v.src=rows[active].file+'?sha='+rows[active].sha256;v.playbackRate=1;v.play()};v.ontimeupdate=()=>document.querySelector('#now').textContent=(active||'')+' '+v.currentTime.toFixed(3)+' / '+v.duration.toFixed(3);v.onended=()=>{proofs.push({scene:active,sha256:rows[active].sha256,seconds:v.duration,rate:v.playbackRate,ended:v.ended});document.querySelector('#proof').textContent=JSON.stringify(proofs,null,2)};</script>'''
(O/'index.html').write_text(page,encoding='utf8')
