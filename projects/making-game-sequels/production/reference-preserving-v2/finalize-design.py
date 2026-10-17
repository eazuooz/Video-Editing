from pathlib import Path
import json,subprocess,hashlib,datetime
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';L=P/'production/local/reference-preserving-v2';S=P/'script/reference-preserving-v2'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
ko=read(S/'narration.ko.json');en=read(S/'narration.en.json')
ko['scenes'][6]['lines'][3]='피크민 4에서는 대원들에게 일을 맡기는 활동에, 우주견 와치라는 동료가 더해집니다.'
ko['scenes'][6]['lines'][4]='와치가 몸으로 들이받는 돌진을 쓰면, 항아리가 깨지고 안에 있던 물건이 드러납니다. 대원들에게 일을 맡기는 것과 함께, 동료의 능력도 활용하는 거죠.'
en['scenes'][6]['lines'][4]='Oatchi can Rush forward to smash the pots, revealing the items inside. Alongside assigning jobs to Pikmin, the player can use the companion’s abilities.'
ko['scenes'][4]['lines'][4]='Wii U와 닌텐도 3DS용 작품에서 얼티밋으로 이어질 때는 같은 개발팀과 가까운 제작 환경을 이어 갈 수 있었습니다.'
ko['scenes'][4]['lines'][5]='두 작품 모두 반다이남코 스튜디오가 개발에 참여했습니다. 같은 시리즈 안에서도, 기반을 다시 세우는 경우와 이어 가는 경우가 달랐던 겁니다.'
en['scenes'][4]['lines'][5]='Bandai Namco Studios worked on both games. Even within one series, rebuilding a foundation and carrying it forward have been different situations.'
for d in [ko,en]:d['status']='independent-wording-and-source-action-matched'
write(S/'narration.ko.json',ko);write(S/'narration.en.json',en)
tts=json.loads(json.dumps(ko));aliases={'Wii U':'위 유','닌텐도 3DS':'닌텐도 쓰리디에스','피크민 4':'피크민 사'}
for s in tts['scenes']:
 for a,b in aliases.items():s['lines']=[x.replace(a,b) for x in s['lines']]
write(S/'narration.tts.ko.json',tts)
(S/'narration.ko.txt').write_text('\n\n'.join('\n'.join(s['lines']) for s in ko['scenes'])+'\n',encoding='utf8')
manifest=read(R/'projects/avoid-game-comparisons/production/reference-preserving-v2/tts-manifest.json')
manifest=json.loads(json.dumps(manifest).replace('avoid-game-comparisons','making-game-sequels').replace('avoid-comparisons','game-sequels'))
write(V/'tts-manifest.json',manifest)
sources=[]
rows=[('pikmin4-day2','P35tlRGBEBY',0,'Royalty Free Gameplay Footage','Uploader expressly dedicates its recording to public domain and requests no credit; underlying Nintendo game rights remain separate.','https://www.nintendo.co.jp/networkservice_guideline/en/index.html'),('gt7-sunday','1py4hV9act0',0,'The Geek Joint [Free to Use]','Video description explicitly allows use, editing and monetization; do not reupload to another free-footage channel.','https://eu.gran-turismo.com/gb/gt7/news/00_5186203.html'),('smash-wiiu','wn5EsQn5NLA',123,'LongplayArchive / Spazbo4','Existing channel reuse permission for transformed snippets with credit.','https://www.nintendo.co.jp/networkservice_guideline/en/index.html'),('smash-ultimate','663UvTXbzbM',726,'LongplayArchive / Spazbo4','Existing channel reuse permission for transformed snippets with credit.','https://www.nintendo.co.jp/networkservice_guideline/en/index.html')]
for name,id,offset,recorder,permission,policy in rows:
 f=L/'media'/(name+'.mp4');info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));video=next(s for s in info['streams'] if s['codec_type']=='video');assert video['width']>=1920 and video['height']>=1080
 sources.append(dict(id=name,url='https://www.youtube.com/watch?v='+id,recorder=recorder,classification='independent-gameplay',file=f.relative_to(R).as_posix(),requestedOriginalStart=offset,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),width=video['width'],height=video['height'],fps=video['r_frame_rate'],duration=float(info['format']['duration']),recorderPermission=permission,publisherPolicy=policy,publisherPolicyScope='Nintendo individual commentary/creative gameplay policy' if 'nintendo' in policy else 'Gran Turismo official guidance explicitly anticipates gameplay broadcasting; this is not a blanket license for third-party BGM.',sourceAudio='Use quiet useful game ambience/effects; GT7 original audio excluded because broadcast-mode/music rights were not established.',referenceMediaExcluded=True))
design=[
 ('01','피크민의 지시와 GT7의 운전에서 익숙한 행동을 본다.','익숙한 행동 → 만드는 쪽/하는 쪽의 질문','overview','pikmin4-day2:200–225;gt7-sunday:0–15','게임 화면 두 장을 연결하며 제작의 기반과 다시 할 이유를 대비한다.','고양이2초 뒤 연속 인사·질문; 같은 피크민 화면이02의 첫 행동 설명으로 이어진다.'),
 ('02','실제 피크민 이동/일감 배정과 GT7 조작, 반복 구매 보장 없음.','익숙한 행동 → 재사용 가능한 기반','layers','pikmin4-day2:85–115;gt7-sunday:15–30','작은 영화 프레임/촬영 순서 도식과 자동차 실제 스샷. 시스템·도구·콘텐츠를 순차 분리.','마지막의 입력/규칙 구조를03첫 문장에서 화면의 내용과 나눈다.'),
 ('03','GT7 코너에서 차가 반응하고, 화면 속 코스/차와 실행 기능을 구별.','실행 기능 → 제작 도구 → 콘텐츠 → 가상6+4와2+4','work','gt7-sunday:30–65','실제 차/도로 스샷 옆에 관계도, 아래 작업량 막대. 달 단위 설명용 수치이며 실제GT기간 아님.','일정상의 출발점 이점을04에서 재미 검증 경험으로 확장.'),
 ('04','피크민 지시→부수기/회수의 반응을 확인.','설명만 읽기 → 작은 실행본 → 실제 조작 → 확인','test','pikmin4-day2:225–261,300–327,440–465','벽이 남은 상태와 열린 상태 스샷을 나란히 놓고 프로토타입/플레이테스트 단계도. 실제게임 제작툴/테스트계측인 것처럼 표시하지 않는다.','검증된 기반이 항상 이어지는 것은 아니라는05첫 문장으로 연결.'),
 ('05','WiiU와Ultimate의 대미지/밀어내기 비교; 연속성과 재구축의 차이.','공통 규칙 → 다른 제작 출발점 → 이어지는 개발 환경','teams','smash-wiiu:30–90;smash-ultimate:0–35','두게임 실제 스샷과2014→2018연결; 개발사 사실만 표기, 비공개코드재사용률 주장 없음.','개발 결과를 판단하는 플레이어가06구매 경험 흐름을 이어받는다.'),
 ('06','대전의 공격/반응에서 첫 기대와 직접 한 뒤의 평가를 구분.','기대 → 플레이 → 기억 → 다음 선택','experience','smash-ultimate:175–205;smash-wiiu:180–212','대전 스샷에 연결된 네 단계, 만족/불일치 두 갈래. 실제 이용자 조사나 이탈률이 아닌 개념도.','만족의 기억이 새 구매 이유와 같지는 않다는07전환.'),
 ('07','피크민4에서 와치가 돌진해 항아리를 깨고 물건이 나타나는 행동.','항아리 선택 → 와치 돌진 → 파괴와 물건 등장','oatchi','pikmin4-day2:331.5–336.8,341.5–349.5,520–565','333.5전상태/336.5파괴/348결과 실제스샷. 이동카메라와가림구간에서는표식중단.','새행동/상황의 필요성을08의 제작효율과 플레이가치 구분으로 이어간다.'),
 ('08','피크민 일 배정과GT코너 진입의 구체적 판단으로 두 가치 연결.','이어 쓸 것 → 개선할 행동 → 새로 느낄 결과','value','pikmin4-day2:465–498;gt7-sunday:65–92','그림과스샷을양쪽에놓고 재사용→투자→새경험 화살표. 판매효과수치없음.','두문장의 연결을09에서 전체 제작/플레이 점검으로 마무리.'),
 ('09','기반·경험과 완성도·새도전의 정리.','제작의 출발점 + 다시 할 이유','conclusion','pikmin4-day2:145–158,397–406','이미본개념을새로운실제컷으로정리하고두질문+개발/플레이측스샷. 마지막자막뒤회원10초원본.','내부씬제목으로음악리셋하지않으며결론뒤원본회원엔딩으로연결.')]
plan=read(P/'planning/chapter-plan.json');rev=plan['currentRevision'];rev.update(status='script-and-scene-design-complete-preflight-pending',sourceSelection=sources,scriptKo=(S/'narration.ko.json').relative_to(R).as_posix(),scriptEn=(S/'narration.en.json').relative_to(R).as_posix(),pronunciationAliases=aliases)
rev['scenes']=[dict(id=id,visibleAction=act,learningSteps=steps,visual=kind,candidateRanges=ranges,visualEvidence=visual,boundaryLink=boundary,renderer='Motion Canvas for explanation; native-speed independent gameplay for action',implementationKind='editorial teaching model; no private engine measurements',captionClearance='fixed960,970; actual gameplay aspect-preserved1600x900 within1920x1080; explanation belowy840clear',annotation='speech-linked hollow labeled shapes/paths; inspect target per selected cut; clear at cut/occlusion',editableScene=f'motion-canvas/src/projects/making-game-sequels/revision-v2/scene-{id}.tsx',sceneSaveStatus='pending') for id,act,steps,kind,ranges,visual,boundary in design]
rev['scriptInternalReview']={'all55KoEnParagraphsRead':True,'completeNarrationReadWithoutHeadings':True,'allEightAdjacentBoundaryPairsReviewed':True,'canonicalTermsExplainedBesideFirstUse':True,'hypotheticalCalculation':{'unit':'illustrative months of work, sequential simplification','first':[6,4,10],'reuse':[2,4,6],'notMeasuredGameProduction':True},'referenceCreatorFramingOmitted':True,'personalExperiencesNotRelabelled':True,'sourceActionSampleSheetsRead':['gt7-sheet.jpg','wiiu-sheet.jpg','pikmin-01..05.jpg','ultimate-01..02.jpg','oatchi-detail.jpg'],'continuousSourceMotionReview':'pending','earlyRenderedSample':'pending'}
write(P/'planning/chapter-plan.json',plan)
write(V/'source-selection.json',{'revision':'reference-preserving-v2','sources':sources,'reference':'research-reference-only; never an edit source','selectedGameCount':3,'extraGames':0})
metadata={'titleCandidates':[{'title':ko['title'],'support':'scenes06–07: satisfaction with first game does not guarantee a new reason to buy','selected':True},{'title':'게임 속편은 만들기 쉬운데 팔기는 어려울까?','support':'scenes03–08; avoid literal universal ease claim','selected':False},{'title':'같은 게임을 또 만들면, 왜 다시 사고 싶을까?','support':'scenes07–09 familiar actions/newvalue','selected':False}],'title':ko['title'],'titleEn':en['title'],'publication':'complete final review first; no new upload or scheduling yet','thumbnailConcept':'기반은 이어 쓰되 / 다시 할 이유는 새롭게; original cat and concrete familiar/new action illustration; yellowheader whiteground black/redtype','sourceCredits':sources}
write(P/'publishing/reference-preserving-v2/metadata.json',metadata)
print('55 paired paragraphs finalized against observed source actions; all nine scene designs recorded.')
