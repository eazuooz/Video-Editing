"""Package checked local masters, with truthful remaining human review."""
from pathlib import Path
import json,hashlib,shutil,html,sys,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
style='<style>body{margin:0;background:#090b0d;color:#fff;font:18px system-ui}main{max-width:1000px;margin:auto;padding:28px}video{max-width:100%;width:375px;display:block;background:#000}a{color:#73d7cd;display:inline-block;margin:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}h1{color:#ffd25a}</style>'
slugs=read(B/'batch.json')['authorization']['slugs'];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for slug in sys.argv[1:]:
 p=R/'projects'/slug;project=read(p/'project.json');L=p/project['currentFinalDirectory'];a=p/'production/local/audio-v1';timing=read(p/'production/visual-timing.json');integrity=read(L/'integrity.json');assert integrity['status']=='pass';out=R/'output'/slug;out.mkdir(parents=True,exist_ok=True)
 files={}
 for role,source,suffix in [('clean',L/'clean.mp4','clean.mp4'),('captioned',L/'captioned.mp4','captioned.mp4'),('ko',a/'captions.ko.srt','ko.srt'),('en',a/'captions.en.srt','en.srt')]:
  target=out/(slug+('.'+project['finalVersion'] if project.get('finalVersion') else '')+'.'+suffix)
  if target.exists():assert sha(target)==sha(source)
  else:shutil.copy2(source,target)
  files[role]={'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size}
 title=project['title']+'｜게임 개발 기술 #포털 #shorts';momentum='momentum' in slug
 intro=('포털은 위치만 바꾸는 장치일까요? 입구에서 얻은 속력과 이동 방향을 출구에 연결하는 좌표 변환을 실제 Portal 장면과 Unity 구현으로 설명합니다. 6m/s는 우리 시연의 값이며 게임 내부 측정값이 아닙니다.' if momentum else '포털을 통과할 때 시야와 몸이 끊기지 않는 이유. 플레이어 화면과 관찰 시점을 동시에 보며 출구 카메라, 위치·방향의 좌표 변환, 몸의 보여주기용 복사와 클리핑을 Unity에서 구현합니다. 원리를 설명하는 자체 구현이며 Valve 내부 소스 코드를 재현했다는 주장이 아닙니다.')
 credits='기술 자료\nhttps://danielilett.com/2020-01-03-tut4-4-portal-momentum/\nhttps://github.com/SebLague/Portals\n\n게임 플레이 녹화\n[FREE TO USE] 23 Minutes of PORTAL Gameplay - no commentary — joel\nhttps://www.youtube.com/watch?v=AmJ4orxVpss\nYouTube Creative Commons Attribution(CC BY) 표시 확인. 교육용 구간 발췌, 세로 배치, 주석·자막·내레이션 추가, 원래 음성 제거. 게임 권리는 각 권리자에게 있습니다.\nhttps://creativecommons.org/licenses/by/4.0/\n\n음악\nPixel Peeker Polka - faster Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttps://creativecommons.org/licenses/by/4.0/\nhttps://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100833\n음악은 편집·페이드·음량 조정했습니다.\n'
 if not momentum:credits+='\n캐릭터\nKayKit Adventurers — Kay Lousberg, CC0\nhttps://kaylousberg.itch.io/kaykit-adventurers\n'
 credits+='\n제작 도구\nUnity — https://unity.com/\nMotion Canvas — https://motioncanvas.io/\n'
 footer=read(R/'projects/shorts-portal-recursion/publishing/youtube-upload.json')['metadata']['description'].split('🎮',1)[1].split('출처·자료 및 제작 도구',1)[0]
 (out/'description.txt').write_text(intro+'\n\n#게임개발 #포털 #게임프로그래밍 #shorts\n\n🎮'+footer+'출처 및 라이선스\n'+credits,encoding='utf8');(p/'publishing/title.ko.txt').write_text(title+'\n',encoding='utf8');(p/'publishing/description.ko.txt').write_text((out/'description.txt').read_text(encoding='utf8'),encoding='utf8')
 media=sum(s['end']-s['start'] for s in timing['sections'] if s['kind']=='game');d={'slug':slug,'title':title,'masterVersion':project['currentRevision']+' / final-'+project.get('finalVersion','v1'),'files':files,'outputDirectory':str(out),'reviewPage':str(out/'index.html'),'descriptionPath':str(out/'description.txt'),'durationSeconds':timing['durationSeconds'],'width':1080,'height':1920,'fps':60,'actualGameSeconds':media,'actualGameShare':media/timing['durationSeconds'],'humanReview':'pending','humanListening':'pending','youtube':'not-uploaded','drive':'not-requested','technicalChecks':integrity,'remainingReview':['Full human viewing and listening of this exact captioned master','Brief Korean ASR particle/adverb variants and source quiet-speech contexts; raw PCM retained']};save(p/'production/delivery.json',d);save(out/'delivery.json',d)
 page='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title>'+style+'<main><p>얌얌코딩 · 최종 검수 대기</p><h1>'+html.escape(title)+'</h1><p>1080×1920 · 60fps · '+str(round(d['durationSeconds'],1))+'초</p><video controls playsinline preload="metadata" src="'+Path(files['captioned']['path']).name+'"></video><p>소리를 켜고 전체 내용을 확인해 주세요. 최종 청취와 사용자 검수는 남아 있습니다.</p>'+''.join('<a href="'+Path(v['path']).name+'">'+k+'</a>' for k,v in files.items())+'<a href="description.txt">게시 설명</a><pre>SHA256 '+files['captioned']['sha256']+'</pre></main></html>'
 (out/'index.html').write_text(page,encoding='utf8');save(p/'production/checkpoint.json',{'slug':slug,'revision':project['currentRevision'],'status':'local-review-ready','delivery':str(p/'production/delivery.json'),'captionedSha256':files['captioned']['sha256'],'humanReview':'pending','wholeListening':False,'youtubeUpload':False,'updatedAt':now});project['status']='local-review-ready';save(p/'project.json',project)
 print('PACKAGED',slug,files['captioned']['sha256'])
cards=[]
for s in slugs:
 f=R/'projects'/s/'production/delivery.json'
 if not f.exists():continue
 d=read(f);cards.append('<section><h2>'+html.escape(d['title'])+'</h2><video controls playsinline preload="metadata" src="../'+s+'/'+Path(d['files']['captioned']['path']).name+'"></video><a href="../'+s+'/index.html">영상·한영 자막·설명</a></section>')
out=R/'output/portal-traversal-shorts-20261025';out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+style+'<main><h1>포털 원리 쇼츠 6·7편</h1>'+''.join(cards)+'</main></html>',encoding='utf8')
