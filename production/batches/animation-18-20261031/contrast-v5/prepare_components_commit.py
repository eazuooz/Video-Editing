from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf8')
now=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
s=read(H/'integration-progress-commit-spec.json');c=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
c.update(updatedAt=now,latestCompletionRequest='응~ 17편 전부 마저 완성해서 통합 검수 링크 줘~ 한꺼번에 볼게',gpuBoundary=read(H/'gpu-authorization.json'))
cp=read(H/'checkpoint.json');cp.update(updatedAt=now,gpuBoundary=c['gpuBoundary'],activeCpuTts={'session':83389,'script':'run_reviewed_cpu_tts.py','manifest':'narration/released-tts-manifest.json','releasedPassagesInCurrentRun':83,'additionalReleasedPassagesPendingNextPass':3});save(H/'checkpoint.json',cp)
s['control']=c;s['worklist']=[{'id':x,'set':{'updatedAt':now}} for x in c['episodes']];s['markdownStatus']='설명 시연17편 완료 · 새 게임/음성/자막 통합 제작 중'
m=read(H/'renderer/owned-files.json');files=[v['path'] for v in m['files']]+[m['selfEntry']]
names=['align_baseline.py','baseline-sentence-timing.json','edit_core.py','prepare_narration.py','run_cpu_narration.py','prepare_reviewed_tts.py','run_reviewed_cpu_tts.py','render_shape_diagram.cjs','serve_review.cjs','gpu-authorization.json','scoped_components_commit.py','prepare_components_commit.py','checkpoint.json']
files += [(H/n).relative_to(R).as_posix() for n in names]
files += [p.relative_to(R).as_posix() for p in (H/'narration').iterdir() if p.is_file() and p.suffix in ['.json','.md','.py']]
files += ['projects/'+r['slug']+'/production/contrast-v5/final.'+lang+'.json' for r in read(H/'baseline-review-manifest.json')['records'] if r['id'] in c['episodes'] for lang in ['ko','en']]
s['ownedPaths']=sorted(set(files));save(H/'components-commit-spec.json',s)
print('Owned source files',len(s['ownedPaths']))
