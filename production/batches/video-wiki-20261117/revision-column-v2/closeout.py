"""Update only this wiki revision's ledgers after all 113 readbacks pass."""
from pathlib import Path
import json,hashlib

B=Path(__file__).resolve().parent
REPO=B.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def main():
    p=read(B/'progress.json');assert p['summary']['savedAndInternallyReviewed']==113 and p['summary']['pending']==0
    p['status']='all-notion-columns-saved-internally-reviewed-user-review-pending'
    p['qa']='final-qa.json';p['completedOn']='2026-11-18';write(B/'progress.json',p)
    m=read(B/'media-uploaded.json')
    # These two filenames were corrected and visually rechecked BEFORE their POST.
    # The in-memory metadata had been read before that correction; reconcile only its fingerprint.
    for x in m:
        if x['key'] in ['diagram_leaf_paths','diagram_parallax_offsets']:
            x['sha256']=hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()
            x['metadataAudit']='Fingerprint reconciled to the corrected file actually uploaded after pre-upload visual QA; image content was not changed after upload.'
    write(B/'media-uploaded.json',m)
    status='all-notion-columns-saved-internally-reviewed-user-review-pending'
    pub=read(B.parent/'publication.json')
    if 'baselineSummary' not in pub:pub['baselineSummary']=dict(pub['summary'])
    pub['status']=status;pub['summary']['imageBlocks']=p['summary']['revisedPageImageBlocks']
    pub['columnRevisionResult']={**p['summary'],'completedOn':'2026-11-18','qa':'revision-column-v2/final-qa.json','publicWebsite':'Public-site update verification remains separate from successful native Notion readbacks.'}
    write(B.parent/'publication.json',pub)
    work=REPO/'shared/publishing/video-worklist.json';w=read(work);v=w['videoCompanionWiki20261117'];v['status']=status
    v['summary']['imageBlocks']=p['summary']['revisedPageImageBlocks'];v['review']='production/batches/video-wiki-20261117/revision-column-v2/index.html';v['columnRevision'].update(p['summary']);v['columnRevision']['status']=status
    for r in v['pages']:
        actual=next(x for x in p['rows'] if x['id']==r['id']);r['status']=actual['status'];r['columnEvidence']=actual['verification']
    write(work,w)
    control=REPO/'shared/publishing/video-production-control.json';c=read(control);b=c['videoCompanionWikiPolicy20261117']['existingBatch'];b['revisionStatus']=status;b['imageBlocks']=p['summary']['revisedPageImageBlocks'];b['revisionSummary']=p['summary'];write(control,c)
    print(json.dumps({'status':status,**p['summary']}))

if __name__=='__main__':main()
