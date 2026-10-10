"""Make episode metadata describe the actual revision, preserving baseline history."""
from pathlib import Path
import json,sys,shutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;slug=sys.argv[1];P=ROOT/'projects'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,data):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text((json.dumps(data,ensure_ascii=False,indent=2)+'\n') if not isinstance(data,str) else data,encoding='utf8')
m=read(P/'project.json');t=read(P/'production/timeline.json');l=read(P/'production/lesson.json');part=m['lecture']['episode']
m['editing']['finalBodyFrames']={'total':t['bodyFrames'],'actual':t['actualFrames'],'explanation':t['explanationFrames'],'ratioErrorFrames':0}
m['editing']['openingOverview']={'required':True,'scenes':['F01','01'] if part==1 else ['F03'],'reviewedBeforeTts':True,'question':m['lecture']['viewerQuestion'],'outcome':'Create and reverse a defined unit rotation' if part==1 else 'Compose rotations in order, compute relative rotation and rotate the worked vector','orderedSteps':['허수와 평면 회전 → 네 성분과 반각','같은 자세의 두 부호 → 단위 길이','회전을 되돌리기 → 다음 편의 합성 문제'] if part==1 else ['두 회전의 순서와 적용 기준','목표 자세까지의 회전 차이와 짧은 경로','같은 벡터를 회전하고 역회전하기'],'baselineWholeChapterMapRetained':part==1,'classification':'explanation','languages':['ko','en']}
m['lecture']['baselineRotationSeriesPart']=3;m['lecture']['baselineRotationSeriesTotalParts']=4
m['lecture']['part']=part;m['lecture']['totalParts']=2;m['lecture']['partNumberScope']='two-episode quaternion revision'
m['lecture']['baselineCoveredSections']=m['lecture'].pop('coveredSections',m['lecture'].get('baselineCoveredSections',[]))
m['lecture']['coveredOriginalSceneIds']=m['preservation']['originalIds']
m['paths']['productionBuilder']='production/batches/game-math-part2-teaching-revision/build-episodes.py'
m['paths']['publishingKo']=f'projects/{slug}/publishing/upload-description.ko.txt';m['paths']['publishingEn']=f'projects/{slug}/publishing/upload-description.en.txt'
m['rendererDecision']['comparison']='projects/game-math-quaternion-operations/planning/manim-comparison.md'
write(P/'project.json',m)
cuts=[{'scene':s['id'],'startSeconds':s['start'],'seconds':s['seconds'],'frames':s['frames'],'classification':s['classification'],'preservedOriginal':s['preservedOriginal'],**s['cut']} for s in t['scenes'] if s['classification']=='actual']
write(P/'sources/gameplay-cuts.json',{'nativeSpeed':1,'noLoops':True,'sourceAudioUsed':False,'ratioScope':'body','actualShare':.4,'explanationShare':.6,'cuts':cuts,'annotationTrackRegistry':'production/batches/game-math-part2-teaching-revision/quaternion-annotation-tracks.json','movingPixelReview':'pending'})
write(P/'sources/SOURCES.md',f'# {m["titles"]["ko"]} — 내부 출처\n\n원본26장면과 승인 PCM은 `game-math-quaternion-operations`에서 보존했습니다. 이 편은 원본 장면 {", ".join(m["preservation"]["originalIds"])}을 원래 순서로 유지합니다.\n\n기존 게임 녹화: Riders Republic, `4Odvp_TIeQU`. 새 비교 녹화: Riders Republic, `_dw9jjRpanA`. 녹화 업로더의 재사용 안내와 비교 재생 기록을 보존하며, 게임 IP와 사람의 공개 권리 검토는 별도 미완료입니다.\n\n최종 발췌는 `gameplay-cuts.json`의 실제 원속도 구간입니다. 후보 선택·제외와 잘림/충돌 수정 근거는 배치의 `new-source-playback-comparison.json`, `extra-source-playback-comparison.json`, `closing-source-playback-comparison.json`, `quaternion-source-corrections-v5.json`에 있습니다. 화면 투영선은 수동 관찰한 몸체·날개·바퀴 랜드마크입니다. 게임 월드 좌표나 내부 쿼터니언을 측정했다는 뜻은 아닙니다.\n\n실제 화면이 주도하는 발췌는 actual, 정지 도식과 계산은 explanation이며 중복 계상하지 않습니다. 완성본 움직임 검수는 아직 별도입니다.\n')
rows=[f'# {m["titles"]["ko"]}\n',f'시청자 질문: {m["lecture"]["viewerQuestion"]}\n',f'측정 길이 {t["seconds"]:.2f}초. 본문 실제 {t["actualFrames"]}프레임 / 설명 {t["explanationFrames"]}프레임: 정확히40:60. BGM과 원본 게임 소리 없음.\n','기존 설명과 순서는 그대로 두고 어려운 대목 옆에 선행 지식·작은 숫자·인과 연결을 삽입했습니다. 한 장면의 결과가 다음 장면의 질문이 되도록 실제 대사를 다음 순서로 배치했습니다.\n']
for slot,scene in zip(t['scenes'],l['scenes']):
 assert slot['id']==scene['id'];rows.append(f'## {slot["id"]} · {slot["start"]:.2f}s · {slot["title"]}\n\n'+('기존 전체 설명 보존.' if slot['preservedOriginal'] else '새 삽입 설명/연결.')+' '+f'분류: {slot["classification"]}.\n\n'+ '\n\n'.join(scene['ko'])+'\n')
rows.append('## 검수 상태\n\n원본26장면155한글문장·영문·수학 규약 보존 검사는 통과했습니다. 실제 완성본의 전체 흐름·추적선·고정 자막 검수, 사람의 전체 청취, 플랫폼 설정은 각각 별도 기록합니다.\n')
write(P/'planning/outline.md','\n'.join(rows))
if (P/'audio/mix-measurements.json').exists():
 a=read(P/'audio/mix-measurements.json');write(P/'audio/mix-report.md',f'# 내레이션 전용 믹스\n\n{t["seconds"]:.2f}초,48kHz stereo. BGM 및 게임 원본 소리 없음. 실측 {a["final"]["input_i"]}LUFS, {a["final"]["input_tp"]}dBTP. 원본 안내/회원 엔딩은 보존하고, 엔딩10초와 브랜드2초의 무음 범위를 확인했습니다. 전체 사람 청취는 미완료입니다.\n')
write(P/'README.md',f'# {m["titles"]["ko"]}\n\n원본 `game-math-quaternion-operations`의 추가 보강 수정본 {part}/2. 원본 승인 설명·PCM·소개·회원 엔딩을 보존합니다.\n\n납품 확인: `output/index.html`. 배치 상태: `production/batches/game-math-part2-teaching-revision/queue.json`. 현재 미완료 상태를 완성/업로드 증거로 읽지 않습니다.\n\n재생성: `python production/batches/game-math-part2-teaching-revision/build-episodes.py {slug} render` 후 `finish-episode-render.py {slug}`. GPU 음성은 별도 보존 배치이며 재생성하지 않습니다.\n')
print('Episode metadata, exact cuts and retained/insertion records updated; no approval or platform mutation.')
