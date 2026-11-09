"""One root-approved A11 literal canonical-term take. Never launches TTS."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,os
H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);v=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if p.exists()and p.read_text('utf8')==v:return
    t=p.with_suffix(p.suffix+'.pending');t.write_text(v,'utf8');os.replace(t,p)
def rel(p):return Path(p).relative_to(R).as_posix()
def main():
    source=H/'narration/source-verified-revisions.json';before=read(source);after=deepcopy(before)
    c=next(c for e in after['episodes']if e['id']=='A11'for c in e['changes']if c['id']=='024')
    old=deepcopy(c);archive=L/'a11-canonical-term/source-before.json'
    if not archive.exists():save(archive,before)
    c['ko']=c['ko'].replace('인터폴레이션, 즉 보간 계산','인터폴레이션 계산');c.pop('spokenKo',None)
    c['canonicalTermDelivery']={'speech':'인터폴레이션 + 키 프레임 사이를 자동으로 이어 주는 plain definition',
        'prominentOnscreenHeading':'Interpolation (보간)','reason':'Omit only the redundant Korean equivalent in this sentence after repeated ASR ambiguity; retain the canonical English term, full mechanism, hand-posed technique and conclusion. Never equate 보관 with 보간.',
        'humanListening':False,'englishUnchanged':True}
    assert c['en']==old['en']
    for e in before['episodes']:
        ne=next(x for x in after['episodes']if x['id']==e['id'])
        for x in e['changes']:
            if(e['id'],x['id'])!=('A11','024'):assert x==next(y for y in ne['changes']if y['id']==x['id'])
    save(source,after);key='A11S024X'+hashlib.sha256(c['ko'].encode()).hexdigest()[:10]
    script=L/'a11-canonical-term.ko.json';manifest=L/'a11-canonical-term-manifest.json'
    save(script,{'scenes':[{'id':key,'title':'A11 024 canonical English term with full plain definition','lines':[c['ko']]}]})
    m=read(L/'last-clarity-pair-manifest.json');m['paths']['script']=rel(script);m['tts']['filenameStem']='a11-canonical-term';save(manifest,m)
    command=[str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(R/'qwen3-tts/render_narration.py'),'--project','animation-contrast-v5',
        '--manifest',rel(manifest),'--device','cuda:0','--batch-size','1','--force-scenes',key]
    save(L/'a11-canonical-term-job.json',{'sourceRevisionsSha256':sha(source),'key':key,'script':rel(script),'manifest':rel(manifest),'command':command,
        'appendLog':rel(L/'tts-reviewed-final-gpu.log'),'newKo':c['ko'],'en':c['en'],'other87PassagesExact':True,'ttsStartedByThisPreparation':False,'humanListening':False})
    print(json.dumps({'sourceSha256':sha(source),'key':key},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
