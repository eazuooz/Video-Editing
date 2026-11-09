"""Prepare the approved final two clarity/pronunciation takes; no synthesis."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,os
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    value=json.dumps(d,ensure_ascii=False,indent=2)+'\n';p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists()and p.read_text('utf8')==value:return
    t=p.with_suffix(p.suffix+'.pending');t.write_text(value,'utf8');os.replace(t,p)
def rel(p):return Path(p).relative_to(R).as_posix()
def main():
    source=H/'narration/source-verified-revisions.json';before=read(source);after=deepcopy(before)
    archive=L/'last-clarity-pair/source-before.json'
    if not archive.exists():save(archive,before)
    original=read(archive);scenes=[];changes=[]
    for e in after['episodes']:
        for c in e['changes']:
            key=(e['id'],c['id'])
            if key not in {('A09','041'),('A11','024')}:continue
            old=next(c for ep in original['episodes']if ep['id']==e['id']for c in ep['changes']if c['id']==key[1])
            if key[0]=='A09':
                target=old['ko'].replace('몸의 윤곽선과','몸의 윤곽과');assert target!=old['ko']
                assert c['ko']in(old['ko'],target);c['ko']=target;c.pop('spokenKo',None)
            else:
                assert c['ko']==old['ko']and c['en']==old['en'];assert c['ko'].count('보간 계산')==1
                c['spokenKo']=c['ko'].replace('보간 계산','보 간 계산')
            c.setdefault('finalClarityCorrection',{'reason':'A09 removes the ambiguous 선+과 junction with the same contour meaning. A11 separates only spoken 보 간 while retaining canonical 보간 and the full interpolation definition in display. Independent ASR uncertainty is not asserted as objective incorrect speech.',
                'humanListening':False,'claimAndOrderPreserved':True})
            spoken=c.get('spokenKo',c['ko']);jobkey=e['id']+'S'+c['id']+'X'+hashlib.sha256(spoken.encode()).hexdigest()[:10]
            scenes.append({'id':jobkey,'title':e['id']+' '+c['id']+' final minimum clarity adjustment','lines':[spoken]})
            changes.append({'episode':e['id'],'sentenceId':c['id'],'key':jobkey,'ko':c['ko'],'en':c['en'],'spokenKo':spoken})
    for ep in before['episodes']:
        ne=next(x for x in after['episodes']if x['id']==ep['id'])
        for c in ep['changes']:
            if(ep['id'],c['id'])not in {('A09','041'),('A11','024')}:assert c==next(x for x in ne['changes']if x['id']==c['id'])
    save(source,after);script=L/'last-clarity-pair.ko.json';manifest=L/'last-clarity-pair-manifest.json';save(script,{'scenes':scenes})
    m=read(L/'clarity-retakes-manifest.json');m['paths']['script']=rel(script);m['tts']['filenameStem']='last-clarity-pair';save(manifest,m)
    command=[str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(R/'qwen3-tts/render_narration.py'),'--project','animation-contrast-v5',
        '--manifest',rel(manifest),'--device','cuda:0','--batch-size','1','--force-scenes',','.join(x['id']for x in scenes)]
    save(L/'last-clarity-pair-job.json',{'sourceRevisionsSha256':sha(source),'changes':changes,'script':rel(script),'manifest':rel(manifest),'command':command,
        'appendLog':rel(L/'tts-reviewed-final-gpu.log'),'ttsStartedByThisPreparation':False,'humanListening':False,'other86PassagesPreserved':True})
    print(json.dumps({'sourceSha256':sha(source),'keys':[x['id']for x in scenes]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
