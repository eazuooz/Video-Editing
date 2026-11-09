"""Prepare exactly four root-approved clarity edits; never starts TTS."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,os

H=Path(__file__).resolve().parent;R=H.parents[3];L=H/'local'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    value=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if p.exists()and p.read_text('utf8')==value:return
    t=p.with_suffix(p.suffix+'.pending');t.write_text(value,'utf8');os.replace(t,p)
def rel(p):return Path(p).relative_to(R).as_posix()

def main():
    source=H/'narration/source-verified-revisions.json';before=read(source);after=deepcopy(before)
    ids={('A05','029'),('A08','018'),('A09','041'),('A11','024')}
    replacements={
        ('A05','029'):('차이의 기타도 무기가 나아가는 방향과 맞은 상대의 반응을 함께 보면 타격이 더 분명해집니다.',None),
        ('A08','018'):('마엘이 검을 잡은 자세를 보세요. 상대를 향한 얼굴과 검을 잡은 팔의 방향이 서로 구별됩니다.',None),
        ('A09','041'):('컵헤드의 고피도 바닥에 눌릴 때 몸의 윤곽선과 얼굴의 모양이 함께 달라집니다. 둥근 그림 전체를 한 방향으로 줄인 것만으로는 같은 인상이 나오지 않을 수 있죠.',None),
        ('A11','024'):('길티기어 엑사드 사인의 개발 발표에서도 키 프레임 사이를 자동으로 이어 주는 인터폴레이션, 즉 보간 계산을 쓰지 않고 자세를 하나씩 직접 만들었다고 설명합니다. 중간을 매끈하게 채우는 대신 중요한 모양을 선택해 보여 주는 방식이죠. 우리 시연의 두 버전에서도 그 모양이 화면에 얼마나 남는지 보세요.',
            'The Guilty Gear Xrd -SIGN- development presentation explains that the team skipped automatically linking keyframes through interpolation and instead posed each frame by hand. Instead of smoothly filling every gap, they selected the important shapes to show. In our two demonstration versions, watch how long those shapes remain visible.'),
    }
    reviews=read(L/'asr-changed/text-review.json')['entries'];contexts=[];scenes=[];changes=[]
    archived=L/'clarity-retakes/source-before.json'
    if not archived.exists():save(archived,before)
    original_source=read(archived)
    for ep in after['episodes']:
        old_ep=next(x for x in before['episodes']if x['id']==ep['id'])
        for c in ep['changes']:
            key=(ep['id'],c['id']);old=next(x for x in old_ep['changes']if x['id']==c['id'])
            if key not in ids:assert c==old;continue
            original_ep=next(x for x in original_source['episodes']if x['id']==ep['id'])
            original=next(x for x in original_ep['changes']if x['id']==c['id'])
            ko,en=replacements[key]
            assert old['ko']in(original['ko'],ko),'Refuse to overwrite a later independent revision'
            c['ko']=ko
            if en is not None:c['en']=en
            c.pop('spokenKo',None);c.pop('pronunciationCorrection',None)
            review=next((x for x in reviews if(x['episode'],x['sentenceId'])==key),None)
            correction={
                'reason':'Root-approved minimum clarity rephrase after repeated independent ASR uncertainty. Original meaning, neighboring teaching logic and example retained; this is not proof that the prior speech was objectively wrong.',
                'sourceReadback':{k:review[k]for k in ('audioSha256','asrPath','asrSha256','recognized')}if review else None,
                'canonicalTermPreserved':True,'humanListening':False,
            }
            if not c.get('clarityCorrection'):c['clarityCorrection']=correction
            c['readThroughScope']='Replacement in KO/EN plus preceding/following current passage reread as connected text. No claim change or reordered point; text review, not audio listening.'
            voicekey=ep['id']+'S'+c['id']+'X'+hashlib.sha256(ko.encode()).hexdigest()[:10]
            scenes.append({'id':voicekey,'title':ep['id']+' '+c['id']+' approved clarity rephrase','lines':[ko]})
            changes.append({'episode':ep['id'],'sentenceId':c['id'],'key':voicekey,'ko':ko,'en':c['en'],'previousKo':original['ko'],'previousEn':original['en']})
            context={}
            for lang in ('ko','en'):
                file=R/'projects'/ep['slug']/'production/contrast-v5'/('final.'+lang+'.json')
                rows=read(file)['scenes'];i=next(i for i,x in enumerate(rows)if x['id']==c['id'])
                context[lang]=[{'id':x['id'],'text':c[lang]if x['id']==c['id']else' '.join(x['lines'])}for x in rows[max(0,i-1):i+2]]
            contexts.append({'episode':ep['id'],'sentenceId':c['id'],'context':context,'meaningAndTransitionPreserved':True})
    assert len(scenes)==4 and before['existingApprovedChanges']==after['existingApprovedChanges']
    save(source,after)
    script=L/'clarity-retakes.ko.json';manifest=L/'clarity-retakes-manifest.json'
    save(script,{'scenes':scenes})
    m=read(L/'phonetic-a05-029-manifest.json');m['paths']['script']=rel(script);m['tts']['filenameStem']='clarity-retakes'
    save(manifest,m)
    command=[str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8',str(R/'qwen3-tts/render_narration.py'),
        '--project','animation-contrast-v5','--manifest',rel(manifest),'--device','cuda:0','--batch-size','1','--force-scenes',','.join(x['id']for x in scenes)]
    report={'sourceRevisionsSha256':sha(source),'scope':'Only four of the same88 changed paragraphs; other84 entries and913 unchanged baseline sentences preserved',
        'changes':changes,'connectedTextReview':contexts,'reviewScope':'Model text review only, not listening',
        'script':rel(script),'manifest':rel(manifest),'command':command,'appendLog':rel(L/'tts-reviewed-final-gpu.log'),
        'ttsStartedByThisPreparation':False,'humanListening':False}
    save(L/'clarity-retakes-job.json',report)
    print(json.dumps({'sourceSha256':sha(source),'keys':[x['id']for x in scenes],'job':rel(L/'clarity-retakes-job.json')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
