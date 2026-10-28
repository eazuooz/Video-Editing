"""Verify deletion and preserved files, and write a human-readable audit."""
from pathlib import Path
import json,hashlib,collections,datetime,shutil
R=Path('D:/Github/VideoEditing');B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
p=read(B/'plan.json');result=read(B/'result.json');inventory=read(B/'inventory.json')
rows=[json.loads(s) for s in (B/'deletions.jsonl').read_text(encoding='utf8').splitlines()]
assert len(rows)==len(p['files'])
errors=[]
for row in rows:
    exists=(R/row['path']).exists()
    if row['status']=='deleted' and exists:errors.append({'path':row['path'],'error':'reported deleted but still exists'})
    if row['status']!='deleted' and not exists:errors.append({'path':row['path'],'error':'reported retained but missing'})
original={x['path']:x for x in inventory['files']}
preserved=0
for item in p['preserved']:
    f=R/item['path']
    if not f.exists():errors.append({'path':item['path'],'error':'protected file missing'});continue
    s=f.stat();old=original[item['path']]
    if s.st_size!=old['bytes'] or s.st_mtime_ns!=old['mtimeNs']:errors.append({'path':item['path'],'error':'protected file changed; external activity must be checked'})
    else:preserved+=1
masters=[]
for e in read(R/'production/batches/private-math-publishing-20261026/checkpoint.json')['entries']:
    f=Path(e['file']);actual=f.resolve(strict=True)
    assert actual.drive.upper()=='C:',str(actual)
    with actual.open('rb') as s:h=hashlib.file_digest(s,'sha256').hexdigest()
    ok=h==e['sha256'];masters.append({'id':e['id'],'path':str(f),'physicalPath':str(actual),'sha256':h,'matchesUploadedMaster':ok})
    if not ok:errors.append({'path':str(actual),'error':'retained C master differs from upload receipt'})
by=collections.defaultdict(lambda:{'files':0,'bytes':0,'videoId':None})
ext=collections.defaultdict(lambda:{'files':0,'bytes':0})
for row in rows:
    if row['status']!='deleted':continue
    s=by[row['owner']];s['files']+=1;s['bytes']+=row['bytes'];s['videoId']=row['videoId']
    e=ext[Path(row['path']).suffix];e['files']+=1;e['bytes']+=row['bytes']
result.update(verifiedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),errors=errors,protectedFilesVerified=preserved,retainedMathMasters=masters,byProject=dict(by),byExtension=dict(ext),driveFreeVerified=shutil.disk_usage('D:/').free)
(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
gb=lambda x:f'{x/1e9:,.2f}'
lines=['# 공개·예약 영상의 D드라이브 미디어 정리','',f"확인일: {result['verifiedAt']}",'','사용자가 2026-10-28 요청한 공개·예약 영상의 로컬 비디오/WAV 삭제만 실행했다. Studio 페이지에서 실제 공개·예약 상태와 영상 ID를 확인한 후, 프로젝트와 연결되는 생성 결과만 대상으로 삼았다. YouTube/Drive 변경은 0건이다.','',f"- 삭제: {result['deletedFiles']:,}개 파일, 합계 {gb(result['deletedBytes'])}GB",f"- 정리 직전 D 여유 공간: {gb(result['driveFreeBefore'])}GB",f"- 삭제 직후 D 여유 공간: {gb(result['driveFreeAfter'])}GB",f"- 최종 확인 D 여유 공간: {gb(result['driveFreeVerified'])}GB",f"- 보존 오류/잠금으로 건너뛴 파일: {result['preservedErrors']}개",f"- 보호 대상 확인: {preserved:,}개",f"- C드라이브에 실제 저장된 최신 수학 예약본: 18편 유지, 업로드 SHA256 모두 비교",f"- 검증 오류: {len(errors)}개",'', '파일 합계와 실제 여유 공간 증가량은 하드링크 및 동시에 진행 중인 다른 디스크 쓰기 때문에 다를 수 있다.','', '## 보존 범위','', '원본 게임 녹화·다운로드·소스/에셋, 공유 음성/브랜딩, 아직 공개·예약되지 않은 프로젝트 및 별도 V7/V8 강의, 미완성 프로젝트에서 참조하는 파일, C드라이브 연결 폴더를 보존했다. 코드·대본·자막·이미지·프로젝트 파일은 삭제 확장자에 포함하지 않았다. 이번 삭제로 기록에 나열된 과거 로컬 영상/PCM 링크는 더 이상 재생되지 않으며, 이는 렌더 실패가 아니라 사용자가 요청한 저장공간 정리다.','', '## 정리한 프로젝트','', '| 프로젝트 | YouTube 상태 | 삭제 파일 | 합계 GB |','|---|---|---:|---:|']
for slug,s in sorted(by.items(),key=lambda kv:-kv[1]['bytes']):
    o=p['owners'][slug];lines.append(f"| {slug} | [{o['visibility']}](https://www.youtube.com/watch?v={s['videoId']}) | {s['files']:,} | {gb(s['bytes'])} |")
lines+=['','## 증거','', '- `studio-rows-page1.json`, `studio-rows-page2.json`: 이번 확인의 실제 Studio 표시','- `inventory.json`, `plan.json`: 전체 파일 현황·소유 프로젝트·보존 사유·구체적인 절대 경로','- `hashes.jsonl`, `hash-verification.json`: 삭제 직전 SHA256 및 크기/수정시각 검증','- `deletions.jsonl`: 파일별 삭제 결과·SHA256·YouTube ID','- `verification.json`: 삭제 후 존재 여부, 보존 대상 및 C드라이브 최종본 검증','','이 기록은 이번 일회성 로컬 삭제에만 적용되며 향후 자동 삭제나 플랫폼 삭제를 승인하지 않는다.','']
(B/'README.md').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps({'deletedFiles':result['deletedFiles'],'deletedGB':gb(result['deletedBytes']),'freeGB':gb(result['driveFreeVerified']),'preserved':preserved,'errors':errors,'CmastersVerified':sum(m['matchesUploadedMaster'] for m in masters)},ensure_ascii=False),flush=True)
assert not errors
