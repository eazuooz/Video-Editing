"""Bind a selected episode's reviewed subtitle pairs to the finite, local-only batch."""
from pathlib import Path
import json,sys,hashlib
HERE=Path(__file__).resolve().parent;R=HERE.parents[2]
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def save(f,v):f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(f):return f.relative_to(R).as_posix()
def prepare(ep):
 batch=read(HERE/'batch.json');row=next(r for r in batch['episodes'] if r['id']==ep)
 assert batch['productionAuthorized'] and batch['ttsAuthorized'] and not batch['youtubeAuthorized']
 work=next(v for v in read(R/'shared/publishing/video-worklist.json')['rows'] if v['id']==ep)
 p=R/'projects'/work['slug'];h=p/'production/series-v1';l=p/'production/local/series-v1';l.mkdir(parents=True,exist_ok=True)
 selection=read(h/'source-selection.json');assert selection['episode']==ep
 data=read(HERE/'scripts'/ep/'narration.ko.json');pairs=(h/'narration-pairs.txt').read_text('utf-8-sig').strip().split('\n\n')
 assert len(pairs)==len(data['scenes'])
 groups=[];scenesKo=[];scenesEn=[]
 for source,block in zip(data['scenes'],pairs):
  g=[tuple(x.strip() for x in line.split(' | ')) for line in block.splitlines()]
  assert all(len(z)==2 and all(z) for z in g)
  groups.append(g)
  scenesKo.append(dict(id=source['id'],title=source['title'],lines=[' '.join(x for x,y in g)]))
  scenesEn.append(dict(id=source['id'],title=source['title'],lines=[' '.join(y for x,y in g)]))
 save(h/'narration.ko.json',{'scenes':scenesKo});save(h/'narration.en.json',{'scenes':scenesEn})
 m=read(R/'projects/animation-breaking-down-attack-animations/production/grid-v1/tts-manifest.json')
 m.update(slug=work['slug'],title=row['titleKo'],titles={'ko':row['titleKo']},revision='series-v1',seriesOrder=ep,sourceReference=row['sourceUrl'],authorization=rel(HERE/'batch.json'),sources=[row['sourceUrl']],status='in-production',publishReady=False)
 m['paths']={'script':rel(h/'narration.ko.json'),'scriptKo':rel(h/'narration.ko.json'),'scriptEn':rel(h/'narration.en.json')};m['tts']['outputDir']=rel(l/'voice');m['delivery']={'localStorageRoot':rel(l/'delivery')};m['editing']={'targetGameplayShare':.6,'sourceMinimum':[1920,1080],'output':[1920,1080,60],'sourceSelection':rel(h/'source-selection.json')}
 save(h/'tts-manifest.json',m)
 if not (p/'project.json').exists():save(p/'project.json',m)
 save(h/'production-binding.json',{'episode':ep,'referencePlan':data.get('sourceMap'), 'selectedScope':'source-bound original teaching order; local complete review with A04–A18','scriptHash':hashlib.sha256((h/'narration.ko.json').read_bytes()).hexdigest(),'captionGroups':len(groups),'platformAllowed':False})
 print(work['slug'])
if __name__=='__main__':prepare(sys.argv[1])
