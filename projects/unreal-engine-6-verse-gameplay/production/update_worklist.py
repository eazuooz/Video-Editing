"""Build exact per-video overlays only after both review deliveries exist."""
from pathlib import Path
import hashlib, json, html, re,sys
from datetime import datetime, timezone
sys.dont_write_bytecode=True
from commit_reviews import R,W,D,C,B,TABLE,HTML,CHECK,UE,A02,REV
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rel(p):return p.relative_to(R).as_posix()
def art(p):
    with p.open('rb') as f:return {'path':rel(p),'bytes':p.stat().st_size,'sha256':hashlib.file_digest(f,'sha256').hexdigest()}
def runtime(sec):m,s=divmod(round(sec),60);return f'{m}분 {s}초'
P=R/'projects'/UE
A=R/'projects'/A02
H=A/'production'/REV
UE_REV='engine-comparison-v2'
new=read(P/'production/delivery-output.json');first=read(P/'production/local'/UE_REV/'encoded-verification.json')
ac=read(H/'checkpoint.json');ad=A/'production/local'/REV/'delivery/output'/A02;am=read(ad/'delivery-manifest.json')
stamp=datetime.now(timezone.utc).isoformat()
hash1=first['masters']['captioned']['sha256'];hash2=am['captionedMasterSha256']
assert ac['captionedMasterSha256']==hash2 and am['verification']['structuralFinalPair']=='pass'
t1=runtime(first['seconds']);t2=runtime(ac['durationSeconds'])
stage=read(H/'unreal-stage/editable-stages.json')
assert len(read(H/'unreal-stage/encoded-motion-evidence.json'))==6
host='http://127.0.0.1:'+str(int(sys.argv[1]) if len(sys.argv)>1 else 9243)
ue_script=rel(P/'script/engine-comparison-v2/전체대본.md')
row1={'id':'S-UE6','slug':UE,'series':'S','seriesOrder':5,'title':read(P/'project.json')['titles']['ko'],'productionAuthorized':True,'productionComplete':True,'productionStatus':'두 영상과 발표 자료 반영 · '+t1+' · 1080p60','reviewStatus':'한국어 내레이션·한영 자막 로컬 검수본 전달 · 사용자 시청 대기','humanApproval':'현재 검수본 시청·청취 대기','platformStatus':'미업로드','executionStatus':'로컬 검수 대기','localMasterAvailable':True,'captionedMasterSha256':hash1,'evidence':[ue_script,rel(P/'production/delivery-output.json'),rel(P/'planning/sources.json')],'updatedAt':stamp}
row2={'id':'A02','productionComplete':True,'productionStatus':f'쿨라·리리 실제 FHD 및 언리얼 손목 30cm / 54cm · {t2} · 1080p60','reviewStatus':'새 수정본 시청·청취 대기','platformStatus':'미업로드 · 로컬 검수 대기','humanApproval':'현재 수정본 사용자 검수 대기','executionStatus':'A02 1.8배 비교 검수본 전달','localMasterAvailable':True,'deliveryLedger':rel(H/'local-delivery-ledger.json'),'evidence':[rel(H/'local-delivery-ledger.json'),rel(H/'sources/reviewed-footage.json'),rel(H/'unreal-stage/encoded-motion-evidence.json')],'updatedAt':stamp,'captionedMasterSha256':hash2}
link=host+'/a02/'
markdown_title=row1['title'].replace('|',r'\|')
table={'S-UE6':f"| S-UE6 | [{markdown_title}]({host}/ue6/) | ☑ 1080p60 · {t1} | ☐ 사용자 시청·청취 | 미업로드 |",'A02':f'| A02 | [동작의 과장](https://www.youtube.com/watch?v=zNBKzLzDKtM) | 동작의 과장 \\| 게임 캐릭터는 왜 현실보다 과장되게 움직일까? | [쿨라·리리 · 언리얼 1.0×/1.8× · {t2} 검수본]({link}) |'}
base=next(x for x in read(R/TABLE)['rows'] if x['episode']=='A02')
cues=sum(1 for line in (ad/(A02+'.ko.srt')).read_text(encoding='utf-8-sig').splitlines() if '-->' in line)
script=dict(base['script'],path=rel(A/'script'/REV/'narration.ko.json'),displayKo=f'기존 14문단 · 캐릭터 해설 3문단 교체 · 한글 {cues}큐')
voice={k:v for k,v in base['voice'].items() if k not in {'cpuAsr','evidence'}}
voice.update(displayKo='변경 3문단 로컬 Qwen · 전편 청취 검수 대기',evidence=art(H/'final-audio-asr-review.json'),humanListening=False)
video={'status':'local-four-output-review-delivery-ready','displayKo':row2['productionStatus'],'completedReviewMaster':True,'technicalQaComplete':True,'sampledEncodedPixelsReviewed':True,'humanFinalReviewRecorded':False,'finalAudioVisualQaComplete':False,'uploadAuthorizedByBatch':False}
delivery={'directory':rel(ad),'indexUrl':link+'index.html','captionedUrl':link+A02+'.captioned.mp4','manifestUrl':link+'delivery-manifest.json','captionedMasterSha256':hash2,'manifest':art(ad/'delivery-manifest.json'),'fourOutputs':am['files'],'userFinalReview':False,'uploadsPerformed':False}
next_action='쿨라·리리 실제 녹화와 언리얼 1.8배 비교 수정본 시청·청취'
snapshot={'checkedAt':stamp,'delivery':art(ad/'delivery-manifest.json'),'audioAsr':art(H/'final-audio-asr-review.json'),'motionEvidence':art(H/'unreal-stage/encoded-motion-evidence.json')}
animation_row=dict(script=script,voice=voice,video=video,nextActionKo=next_action,evidenceSnapshot=snapshot,delivery=delivery)
old_markup=re.search(r'<tr><td data-label="[^"]*">A02</td>.*?</tr>',(R/HTML).read_text(encoding='utf-8'),flags=re.S).group(0)
def cell(label,value):
    global old_markup
    old_markup,n=re.subn(r'(<td data-label="'+re.escape(label)+r'">).*?(</td>)',lambda m:m[1]+value+m[2],old_markup,flags=re.S);assert n==1,(label,old_markup)
cell('대본',html.escape(script['displayKo']));cell('음성',html.escape(voice['displayKo']));cell('영상·최종 검수',html.escape(video['displayKo'])+f'<small><a href="{link}index.html">영상·자막 보기</a> · <a href="{link}{A02}.captioned.mp4">완성 자막 영상</a></small>')
# Use project-owned source paths only. Present data from a different revision never enters Git staging.
owned=set()
for base_dir in (P,H,A/'script'/REV):
    for f in base_dir.rglob('*'):
        if not f.is_file() or {'local','__pycache__','.godot'} & set(f.relative_to(base_dir).parts):continue
        if f.suffix.lower() in {'.py','.cjs','.js','.ts','.tsx','.txt','.json','.md','.html','.cs','.gd','.tscn','.godot','.uid'} or f.name=='.gitignore':owned.add(rel(f))
owned.update(x['path'] for x in stage['files']);owned.add(rel(A/'project.json'))
control=read(R/C)['scopedProductionAuthorizations']
spec={'scope':'ue6-and-a02-two-local-reviews','ownedPaths':sorted(owned),'rows':[row1,row2],'table':table,'grants':{key:control[key] for key in (UE,A02+'-'+REV)},'animationTableRow':animation_row,'animationHtmlRow':old_markup,'animationCheckpoint':{'currentWork':[f'A02 {REV}: four verified local outputs with Kula, Lili and six native Unreal 30/54 cm demonstrations.'],'nextAction':'Watch the exact local captioned master for A02.','updatedAt':stamp,'costlyJobSummary':dict(read(R/CHECK)['costlyJobSummary'],ttsGenerations=3,currentJob='A02 v4 local masters delivered',sourceAsr=rel(H/'final-audio-asr-review.json'))}}
path=P/'production/local/v1/git-scope.json';path.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(path,len(owned))
