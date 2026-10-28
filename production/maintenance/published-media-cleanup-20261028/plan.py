"""Plan only: published/scheduled generated media on D, never source assets."""
from pathlib import Path
import json,re,subprocess,collections,datetime
R=Path('D:/Github/VideoEditing'); B=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
inventory=read(B/'inventory.json')
studio={}
for page in [1,2]:
    for row in read(B/f'studio-rows-page{page}.json'):
        vid=row['href'].split('/')[2]
        studio[vid]={'videoId':vid,'visibility':row['cells'][3], 'date':row['cells'][4], 'title':row['cells'][1].split('\n')[1], 'evidence':f'studio-rows-page{page}.json'}
eligible={v:s for v,s in studio.items() if s['visibility'] in ['공개','예약됨']}
owners={}
worklist=read(R/'shared/publishing/video-worklist.json')
for row in worklist['rows']:
    if row.get('videoId') in eligible:
        owners[row['slug']]={**eligible[row['videoId']], 'mappingEvidence':'shared/publishing/video-worklist.json'}
for row in read(R/'production/batches/private-math-publishing-20261026/checkpoint.json')['entries']:
    if row['videoId'] in eligible:
        owners[row['slug']]={**eligible[row['videoId']], 'mappingEvidence':'production/batches/private-math-publishing-20261026/checkpoint.json','uploadedSha256':row['sha256']}
prior=read(R/'shared/publishing/local-uploaded-master-cleanup-20261025.json')
for row in prior['files']:
    receipt=row.get('sourceReceipt','').replace('\\','/')
    m=re.search(r'/projects/([^/]+)/',receipt)
    if m and row.get('videoId') in eligible and m[1] not in owners:
        owners[m[1]]={**eligible[row['videoId']], 'mappingEvidence':receipt}
# Exact title/receipt association, also checked against current Studio visibility.
for slug,vid in {'renderformer-explained':'_Zz5JF5WGj4'}.items():
    if vid in eligible: owners[slug]={**eligible[vid], 'mappingEvidence':'project name and exact RenderFormer title in Studio page 2'}
known=sorted(owners,key=len,reverse=True)
source_parts={'source','sources','source-assets','downloads','download','raw','raw-footage','originals','recordings','recording','reference','references','research-reference-only','assets','thirdparty','third-party','library','voice-reference','gameplay','media','media-cache','selected-footage','capture','captures','footage','music','sfx'}
def classify(p):
    parts=p.split('/'); owner=None
    if p.startswith('projects/') and len(parts)>3 and parts[1] in owners:
        if parts[2] not in {'production','audio','renders','rendered','output'}: return None,'outside-generated-location'
        owner=parts[1]
    elif p.startswith('output/') or p.startswith('shared/output/'):
        rest=p[len('output/'):] if p.startswith('output/') else p[len('shared/output/'):]
        for prefix in ['narration/','motion-canvas/']:
            if rest.startswith(prefix):rest=rest[len(prefix):]
        first=rest.split('/')[0]
        for slug in known:
            if first==slug or first.startswith(slug+'-') or first.startswith(slug+'.'):
                owner=slug;break
    if not owner:return None,'no-confirmed-published-owner'
    low=p.lower(); ps=set(low.split('/'))
    if ps&source_parts or any('research' in s or 'source' in s or 'footage' in s or 'download' in s or 'capture' in s for s in low.split('/')[:-1]):return None,'source-or-asset-location'
    if 'revision-v8-orientation-matrix' in low or 'revision-v7-part1' in low:return None,'separate-unpublished-article-lesson'
    if re.search(r'(voice[-_]?ref|reference[-_]?audio|speaker|prompt[-_]?audio|branding|membership|coaching|intro[-_]?2s)',low):return None,'shared-or-reusable-media'
    if Path(p).suffix.lower()!='.wav' and not p.startswith('output/') and not p.startswith('shared/output/motion-canvas/'):
        generated_parts={'edit','delivery','delivery-history','pair','pair-exact-v2','assembly','assembly-staging','patches','manim','videos','partial_movie_files','clips','rendered','renders','unity','qa','qa-history','ui-clearance','segments','scenes'}
        generated_name=re.search(r'(captioned|clean|visual|final|render|review|scene|segment|preflight|euler|part1|compiled|corrected|mix|narration|subtitled)',Path(p).name.lower())
        if not(ps&generated_parts or generated_name):return None,'ambiguous-video-preserved'
    return owner,'generated-video-or-wav-for-verified-published-project'
candidates=[]; preserved=[]
for f in inventory['files']:
    owner,reason=classify(f['path'])
    if owner:candidates.append({**f,'owner':owner,'videoId':owners[owner]['videoId'],'reason':reason})
    else:preserved.append({'path':f['path'],'bytes':f['bytes'],'reason':reason})
# Protect explicit references from projects that have no confirmed scheduled/public master.
lookup={f['path'].lower():f for f in candidates}; dependencies={}
cmd=['rg','--files','--hidden','projects','motion-canvas/src','-g','*.json','-g','*.py','-g','*.ts','-g','*.tsx','-g','*.md','-g','*.txt','-g','*.yaml','-g','*.yml','-g','!node_modules','-g','!Library','-g','!*.log']
paths=subprocess.run(cmd,cwd=R,capture_output=True,text=True,encoding='utf8',check=True).stdout.splitlines()
checked=0
for name in paths:
    n=name.replace('\\','/'); parts=n.split('/')
    own=parts[1] if parts[0]=='projects' else (parts[3] if len(parts)>4 and parts[2]=='projects' else None)
    if own in owners:continue
    p=R/name
    if not p.exists() or p.stat().st_size>8_000_000:continue
    try:txt=p.read_text(encoding='utf-8-sig').replace('\\\\','/').replace('\\','/').lower()
    except (UnicodeError,OSError):continue
    checked+=1
    for m in re.finditer(r'(?:d:/github/videoediting/)?((?:projects|shared/output|output)/[^\s\"\'<>]+?\.(?:mp4|mov|mkv|webm|m4v|avi|wav))',txt):
        target=m[1]
        if target in lookup:dependencies.setdefault(target,[]).append(n)
final=[]
for f in candidates:
    refs=dependencies.get(f['path'].lower())
    if refs:preserved.append({'path':f['path'],'bytes':f['bytes'],'reason':'referenced-by-unpublished-project','references':sorted(set(refs))})
    else:
        stat=Path(f['absolute']).stat()
        assert stat.st_size==f['bytes'] and stat.st_mtime_ns==f['mtimeNs'],f['path']
        f['inode']=stat.st_ino; f['links']=stat.st_nlink
        final.append(f)
by=collections.defaultdict(lambda:{'files':0,'bytes':0})
for f in final:by[f['owner']]['files']+=1;by[f['owner']]['bytes']+=f['bytes']
plan={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'userAuthorization':'2026-10-28: D드라이브 용량이 없는데 업로드서 예약된것들 또는 게시된것들 비디오파일이랑 wav 파일 삭제좀 해줘','scope':'Local D-drive generated videos/WAV for currently scheduled/public projects; no platform mutations. Preserve raw/source assets, shared brand/voice references, unuploaded projects/revisions, explicit unfinished-project dependencies and all C-drive junction targets.','root':str(R),'owners':owners,'files':final,'preserved':preserved,'dependencyFilesChecked':checked,'summary':{'files':len(final),'bytes':sum(f['bytes'] for f in final),'byProject':dict(by)}}
(B/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'owners':len(owners),'files':len(final),'GB':round(plan['summary']['bytes']/1e9,2),'dependentFilesPreserved':len(dependencies),'dependencyFilesChecked':checked,'byProject':{k:{'files':v['files'],'GB':round(v['bytes']/1e9,2)} for k,v in sorted(by.items(),key=lambda kv:-kv[1]['bytes'])}},ensure_ascii=False,indent=2))
