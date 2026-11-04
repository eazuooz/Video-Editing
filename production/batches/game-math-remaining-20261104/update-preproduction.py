"""Update only this authorized batch using reported, persisted evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess

ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
batch=load(BATCH/'batch.json')
work=load(ROOT/'shared/publishing/video-worklist.json')
rows={r['id']:r for r in work['rows']}
# Completion here means source audit and bilingual draft, never rendered media.
reported_complete={'M21','M22','M23','M24','M25','M26','M27','M28'}
currently_writing={'M29','M30','M31','M32','M33'}
for item in batch['items']:
    project=ROOT/'projects'/item['slug']
    row=rows[item['id']]
    if item['localReviewReady']:continue
    stage='원문 확보 · 순차 대본 준비'
    if item['id'] in currently_writing:stage='원문 검수 · 한영 대본 작성 중'
    if item['id'] in reported_complete:
        assert all((project/p).exists() for p in ('planning/source-audit.json','script/draft-narration.ko.json','script/draft-narration.en.json'))
        stage='원문 검수·한영 초안 완료 · 장면 제작 전'
        item['status']='source-audit-bilingual-draft-ready'
    if item['id']=='M21':stage='대본·실제 게임 장면 연결 · Unity 씬 제작 중'
    if item['id']=='M22':stage='한영 초안·FHD 게임 후보 준비 · 장면 제작 전'
    if item['id']=='M23':stage='원문 검수·한영 초안·FHD 게임 후보 준비'
    row['productionStatus']=stage
    row['productionComplete']=False
    row['reviewStatus']='완성 영상 대기 · 실제 음성/합성 검수 전'
    row['notes']='2026-11-04 승인된 M21–M33 로컬 제작 범위. '+stage+'. 업로드·예약 미승인.'
    item['evidence']={'sourceAudit':str(project/'planning/source-audit.json') if (project/'planning/source-audit.json').exists() else None,
                      'footageAudit':str(project/'planning/footage-audit.json') if (project/'planning/footage-audit.json').exists() else None}
batch['updatedAt']=datetime.now(timezone.utc).isoformat()
save(BATCH/'batch.json',batch);save(ROOT/'shared/publishing/video-worklist.json',work)
checkpoint=load(BATCH/'checkpoint.json')
checkpoint['updatedAt']=batch['updatedAt']
checkpoint['currentWork']=['Complete source audit and bilingual draft: '+', '.join(sorted(reported_complete)),
                         'M21 isolated Unity shader, geometry, material factorization and real-bake scene authoring; no GPU capture yet',
                         'M21–M23 independently inspected FHD candidates ready; narration/visual bindings and actual composite QA pending',
                         'Drafts in progress: '+', '.join(sorted(currently_writing))]
checkpoint['localReviewReady']=[];checkpoint['runningCostlyJobs']=[]
checkpoint['lastPlanningCommit']='01f08cc92f3ea5ba6e2234e4c99377edbf9021c6'
save(BATCH/'checkpoint.json',checkpoint)
subprocess.run(['python','-X','utf8',str(BATCH/'progress.py')],cwd=ROOT,check=True)
