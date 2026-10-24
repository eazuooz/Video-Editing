"""Package actual finished masters, captions and publishing drafts; never upload."""
from pathlib import Path
import json,hashlib,shutil,html,datetime,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def copy(src,dst):
 if dst.exists():assert sha(src)==sha(dst),str(dst)
 else:shutil.copy2(src,dst)
slugs=read(B/'batch.json')['authorization']['slugs'];topics=['titanfall','superliminal','ghost','gears','portal']
gameTags=[['타이탄폴 2','Titanfall 2','시간여행','맵 디자인'],['슈퍼리미널','Superliminal','강제 원근','Forced Perspective'],['고스트 오브 쓰시마','Ghost of Tsushima','Wind Emitter','게임 VFX'],['기어스 오브 워 4','Gears of War 4','관성화','Inertialization','게임 애니메이션'],['포털','Portal','스텐실 버퍼','Stencil Buffer','재귀 렌더링']]
titles=['타이탄폴 2의 시간여행, 사실 위아래 이동이었다? #게임개발 #shorts','작은 물건이 진짜 커지는 게임의 비밀｜슈퍼리미널 강제 원근 #게임개발','불에 안 타는 낙엽을 바람으로 고쳤다?｜고스트 오브 쓰시마 #게임개발','동작을 뚝 바꿔도 자연스러운 이유｜게임 애니메이션 관성화 #게임개발','포털 속 포털, 컴퓨터는 무한히 그릴까?｜재귀 렌더링 #게임개발']
intros=['시간여행 버튼을 누르면 무슨 일이 일어날까요? 타이탄폴 2의 「인과관계」 임무가 두 시대의 맵과 순간이동을 연결한 방법을 실제 게임 장면과 Unity 시연으로 설명합니다. 시연의 10m는 설명용 수치입니다.','멀리 놓은 물건이 정말 커지는 슈퍼리미널. 거리와 크기를 함께 바꾸는 강제 원근(Forced Perspective)을 플레이어 시점과 옆 시점으로 비교합니다. 2m→6m는 우리 시연의 수치입니다.','고스트 오브 쓰시마 개발 중 모닥불에 떨어진 낙엽이 타지 않는 문제가 있었습니다. 개발팀은 위로 부는 바람을 만드는 Wind Emitter로 대부분의 낙엽이 불 안에 들어가지 않도록 했습니다. 실제 게임의 낙엽 장면과, 같은 초기 조건에서 바람만 바꾼 Unity 재현을 함께 봅니다.','기어스 오브 워 4 개발팀의 관성화(Inertialization). 새 동작으로 바꾼 뒤 이전 자세와의 차이를 부드럽게 없애는 방법입니다. 같은 목표 자세로 전환하는 두 캐릭터를 비교하며 자세 차이와 속도가 왜 필요한지 설명합니다. 각도와 시간은 우리 구현의 예시입니다.','포털 안에서 또 다른 포털이 보이면 어떻게 그릴까요? 스텐실 버퍼(Stencil Buffer)로 그릴 영역을 정하고, 재귀 렌더링(Recursive Rendering)으로 안쪽 시점을 다시 그리는 구조를 설명합니다. Unity 시연은 렌더 텍스처와 스텐실을 이용한 자체 재현이며 Valve 엔진의 실제 처리 수치를 측정한 화면이 아닙니다.']
style='''<style>body{margin:0;background:#080b0c;color:#fff;font:16px system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px}h1,h2{color:#ffd25a}a{color:#83ded3}video{width:100%;max-height:80vh;background:#000}section{border:1px solid #394444;padding:20px;margin:24px 0}p{line-height:1.65}.links{display:flex;gap:18px;flex-wrap:wrap}pre{white-space:pre-wrap;word-break:break-word;color:#b8c3bc;font:14px monospace}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px}.grid section{margin:0}</style>'''
now=datetime.datetime.now(datetime.timezone.utc).isoformat();cards=[]
for i,slug in enumerate(slugs):
 if len(sys.argv)>1 and slug not in sys.argv[1:]:continue
 p=R/'projects'/slug;project=read(p/'project.json');L=p/project.get('currentFinalDirectory','production/local/final-reviewed')
 if not (L/'integrity.json').exists():continue
 integrity=read(L/'integrity.json');assert integrity['status']=='pass';timing=read(p/'production/visual-timing.json');plan=read(p/'planning/production-plan.json');source=read(p/'sources/selected-footage.json');A=p/('production/local/audio-v2' if (p/'production/local/audio-v2/voice/narration.wav').exists() else 'production/local/audio-v1')
 out=R/'output'/slug;out.mkdir(parents=True,exist_ok=True)
 files={}
 suffix=project.get('deliveryFilenameSuffix','')
 masterVersion='distinctive-v1 / final-'+(suffix.lstrip('.') if suffix else 'v1')
 for role,src,name in [('clean',L/'clean.mp4',slug+suffix+'.clean.mp4'),('captioned',L/'captioned.mp4',slug+suffix+'.captioned.mp4'),('ko',A/'captions.ko.srt',slug+suffix+'.ko.srt'),('en',A/'captions.en.srt',slug+suffix+'.en.srt')]:
  dst=out/name;copy(src,dst);files[role]={'path':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size}
 sources='\n'.join(x['url'] for x in plan['research']['primarySources'])
 desc=intros[i]+'\n\n#게임개발 #게임기술 #shorts\n\n자료\n'+sources+'\n\n게임 플레이 녹화\n'+source['title']+' — '+source['recorder']+'\n'+source['url']+'\nYouTube Creative Commons Attribution(CC BY) 표시를 확인했습니다. 교육용 구간 발췌, 세로 화면 배치, 주석·자막·내레이션 추가, 녹화 음성 제거.\nhttps://support.google.com/youtube/answer/2797468\nhttps://creativecommons.org/licenses/by/4.0/\n게임 저작권은 각 권리자에게 있습니다.\n'
 if i==0:desc+='\nThis video is not endorsed by or affiliated with EA or its licensors.\nKayKit Adventurers / Kay Lousberg — CC0; Unity 시연 기사 캐릭터.\nhttps://kaylousberg.itch.io/kaykit-adventurers\n'
 desc+='\n음악\nPixel Peeker Polka - faster Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttps://creativecommons.org/licenses/by/4.0/\nhttps://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100833\n음악은 편집·페이드·음량 조정했습니다.\n'
 (out/'title.txt').write_text(titles[i]+'\n',encoding='utf8');(out/'description.txt').write_text(desc,encoding='utf8')
 metadata={'title':titles[i],'description':desc,'language':'ko','categoryId':'27','tags':['게임개발','게임기술','얌얌코딩',*gameTags[i]],'publicState':'not-uploaded','humanReview':'pending','revision':'distinctive-v1'};save(p/'publishing/metadata.json',metadata)
 mediaSeconds=sum(s['end']-s['start'] for s in timing['sections'] if s['kind']=='game')
 delivery={'slug':slug,'revision':'distinctive-v1','packagedAt':now,'durationSeconds':timing['durationSeconds'],'width':1080,'height':1920,'fps':60,'files':files,'title':titles[i],'descriptionPath':str(out/'description.txt'),'reviewPage':str(out/'index.html'),'humanReview':'pending','humanListening':'pending','youtube':'not-uploaded','drive':'not-requested','actualGameSeconds':mediaSeconds,'actualGameShare':mediaSeconds/timing['durationSeconds'],'technicalChecks':{'fullDecode':True,'regular60fpsPTS':True,'identicalFinalAudioAcrossMasters':True,'completeKoEnCaptions':True},'remainingReview':['Human full playback and final pronunciation/voice-mix assessment','Final user content approval of this captioned SHA256']}
 delivery['masterVersion']=masterVersion
 save(p/'production/delivery.json',delivery);save(out/'delivery.json',delivery)
 captionname=Path(files['captioned']['path']).name
 links=' '.join(f'<a href="{html.escape(Path(v["path"]).name)}">{label}</a>' for (role,v),label in zip(files.items(),['자막 없는 영상','전체 자막 영상','한국어 자막','영어 자막']))
 page=f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(titles[i])}</title>{style}<main><p>얌얌코딩 · 최종 검수 대기</p><h1>{html.escape(titles[i])}</h1><p>1080×1920 · 60fps · {timing["durationSeconds"]:.1f}초</p><video controls playsinline preload="metadata" src="{captionname}"></video><p>화면·파일 검사는 기록된 범위에서 완료했습니다. 최종 청취와 사람의 전체 내용 검수는 남아 있습니다.</p><div class="links">{links}<a href="description.txt">게시 설명</a></div><pre>버전 distinctive-v1\nSHA256 {files["captioned"]["sha256"]}</pre></main></html>'
 page=page.replace('버전 distinctive-v1', '버전 '+masterVersion)
 (out/'index.html').write_text(page,encoding='utf8')
 ledger=read(p/'production/review-ledger.json');ledger.update(delivery=delivery,updatedAt=now,humanFinalReview='pending');save(p/'production/review-ledger.json',ledger)
 print('PACKAGED',slug,files['captioned']['sha256'],flush=True)
for i,slug in enumerate(slugs):
 p=R/'projects'/slug/'production/delivery.json'
 if p.exists():
  d=read(p);name=Path(d['files']['captioned']['path']).name;cards.append(f'<section><h2>{i+1}. {html.escape(titles[i])}</h2><video controls playsinline preload="metadata" src="../{slug}/{name}"></video><p>{d["durationSeconds"]:.1f}초 · 1080p60 · 최종검수 대기</p><a href="../{slug}/index.html">영상·한영 자막·게시 설명</a></section>')
out=R/'output/distinctive-shorts-20261024';out.mkdir(exist_ok=True)
(out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 · 게임 기술 쇼츠 5편</title>'+style+'<main><p>얌얌코딩</p><h1>게임 기술 쇼츠 5편</h1><p>전체 자막 검수본입니다. 각 영상에서 소리를 켜고 재생해 주세요.</p><div class="grid">'+''.join(cards)+'</div></main></html>',encoding='utf8')
