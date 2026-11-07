"""Explicit A02 normal-speed rehearsal edit; immutable previous deliveries."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3]
def load(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
P=R/'projects/animation-exaggeration';L=P/'production/local/pacing-v3'
old=P/'production/local/fighters-v4-kula-lili/edit'
rec=next(x for x in load(H.parent/'real-clips-v2/review-manifest.json')['records'] if x['id']=='A02')
cuts={c['id']:c for c in load(P/'production/fighters-v4-kula-lili/edit-plan.json')['cuts']}
events=[]
def add(key,audio,picture,cut,start,end,reason,repeats=2):
    cid='A02-'+cut
    source=(P/'production/local/real-clips-v2/picture'/f'{cid}.mp4') if cut=='E011' else old/f'{cid}.mp4'
    events.append(dict(key=key,audioAt=audio,pictureAt=picture,source=source.relative_to(R).as_posix(),sourceSHA256=sha(source),sourceStartFrame=start,sourceEndFrame=end,repeatCount=repeats,frames=(end-start)*repeats,kind=cuts[cid]['kind'],reason=reason,speed=1,firstPassAlreadyInBaseline=repeats==2,sourceCut=cid))
add('kula-jump',3034.62,3069,'F11',234,332,'쿨라 상승 공격의 준비·상승·착지를 먼저 세 번 보고 기존 0.25배 분석으로 연결.')
add('lili-kicks',5304,5308,'F21',135,289,'리리의 연속 발차기 전체를 세 번 보고 같은 동작의 느린 분석으로 연결.')
add('screen-size',6411,6426,'E011',0,168,'동일 동작을 큰 화면/작은 화면에서 세 번 비교한 뒤 카메라 크기를 고정.')
add('amplitude',6786,6786,'E011',516,684,'관절 회전 진폭 1.0/1.8배의 전체 동작을 세 번 보고 동일 클립의 자세 분석으로 연결.')
add('shoulder-rotation',9420,9420,'E014',0,144,'고정된 어깨 중심의 회전 경로를 세 번 관찰한 뒤 회전과 이동 정의를 유지.')
add('shoulder-translation',10113,10113,'E014',681,825,'어깨 중심이 움직이는 비교를 세 번 관찰하고 리그의 제약 설명으로 연결.')
add('same-hand-target',10899,10899,'E015',130,310,'같은 손 목표에서 어깨·가슴 모양의 차이를 세 번 확인한 뒤 기존 설명을 유지.')
add('kula-spin',14694,14777,'F31N',0,150,'쿨라의 공중 회전부터 바닥 미끄러짐까지 세 번 확인하고 기존 0.25배 분석으로 연결.')
add('overshoot',16328,16328,'E021',514,688,'목표 도착·초과·정착을 세 번 관찰한 뒤 정식 용어와 기존 수치 설명을 유지.')
add('shape-expansion',18271,18271,'E024',162,366,'가시가 펴지고 자리 잡는 전체 동작을 먼저 세 번 본 뒤 기존 단계 분석으로 연결.',3)
add('kirby-needle',18585,18596,'E023',0,150,'실제 커비 바늘 동작을 재확인한 뒤 큰 그림과 바로 다음 작은 그림의 분석으로 연결.')
plan=dict(episode='A02',slug=rec['slug'],revision='pacing-v3',title=rec['title'],fps=60,baseline=rec,baselineFrames=20354,totalFrames=20354+sum(e['frames'] for e in events),events=events,
    scope='User-selected A02 pacing revision and replacement upload, then the other 17 animation episodes for combined review.',
    userEvidence=['설명 부분 영상이랑 실제 게임예시 영상이랑~ 텀이 너무 짧아서 이해하기전에 영상이 쑥쑥 지나가','앞에서 한번 기본 속도로 3번정도 반복해서 보여주고 느리게 설명하는 (지금) 프레임으로 보이게끔 붙여주면 좋을거같아','A02 수정하고 업로드 완료하고 나머지 전체 적용'],
    preservation='All baseline picture frames, all narration PCM samples, statement order, source rights and existing slow analysis retained. No voice speed change or new TTS. Music continues over the added observation time.',
    ratioException='Meaningful repeated animation observation explicitly requested by user; no unrelated padding to restore a quota.',
    audioStem=(old/'narration-stem.wav').relative_to(R).as_posix(),masterGain=load(old/'audio-build.json')['masterGain'],music='shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3',captionAss=(old/'captions.ko.ass').relative_to(R).as_posix(),
    outputDirectory=(L/'delivery/output/animation-exaggeration').relative_to(R).as_posix(),humanViewedThisRevision=False,platformMutation=False)
save(P/'production/pacing-v3/edit-plan.json',plan)
save(H/'checkpoint.json',dict(stage='a02-render-preparation',order=['A02 replacement and schedule transfer','other 17 local reviews'],authorizedEpisodes=[f'A{i:02d}' for i in range(1,19)],platformAuthorizedEpisodes=['A02'],autoNextOutsideList=False))
print(plan['totalFrames']/60,'seconds;',len(events),'observation blocks')
