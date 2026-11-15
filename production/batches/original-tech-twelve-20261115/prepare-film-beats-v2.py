"""Source-order visual beats; speech times remain actual reviewed word edges."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    with Path(p).open('rb')as f:d=hashlib.file_digest(f,'sha256').hexdigest()
    return dict(path=str(Path(p).resolve()),sha256=d)
def game(slug,name,start,label):return dict(kind='game',source=pin(M/slug/'sources'/name),sourceStartSeconds=start,label=label,sourceSpeed=1,sourceAudio='paired-original'if slug=='shorts-inside-temporal-antialiasing'else'none')
def native(mode,view='player',start=0):return dict(kind='native',mode=mode,view=view,startFrame=start,sourceSpeed=1,capturePurpose='full',actualFullAndVisualReviewRequired=True)
def diagram(key):return dict(kind='diagram',key=key,localModelStartSeconds=0,originalGameData=False)
def main():
    slugs=[x['slug']for x in read(HERE/'batch.json')['projects']];oot,camera,sand,horizon,inside,spider,control,ret,ratchet,doom,botw,kart=slugs
    ootgame=lambda s:game(oot,'archive64-W0q5eFkZhBI-f299.mp4',s,'게임 장면 · 시간의 오카리나 3D')
    camgame=lambda s:game(camera,'gfa-Wrk3Ez_yZZg-f299.mp4',s,'게임 장면 · 닌텐도64 녹화')
    assets={
      oot:[ [ootgame(205),native('target-relative','observer')], [native('free-movement'),camgame(73.2)], [native('target-relative','observer')], [native('simultaneous-intents','observer'),native('turn-taking-intents','player',60)], [ootgame(214)], [native('target-relative','observer'),ootgame(795)], [native('target-relative'),native('turn-taking-intents','observer')] ],
      camera:[[camgame(199),native('follow')],[native('follow'),native('follow','observer')],[native('look-around'),native('look-around','observer')],[native('look-around'),native('look-around','observer')],[native('orbit'),native('orbit-limit')],[native('pull-back'),camgame(1139)]],
      sand:[[game(sand,'journey-free-PcL6zmz4GM8-candidate-copy-v2.mp4',18,'게임 장면 · PS5 녹화'),native('smooth-surface','dune')],[native('averaged-grain-mips','detail'),native('preserved-grain-mips','detail')],[native('half-vector-glints','dune'),native('half-vector-glints','detail')],[native('view-related-glints','dune'),native('view-related-glints','detail')],[native('masked-view-glints','dune'),native('masked-view-glints','detail')],[native('masked-glints-broad-light','dune'),game(sand,'journey-free-PcL6zmz4GM8-candidate-copy-v2.mp4',60,'게임 장면 · PS5 녹화')]],
      horizon:[[game(horizon,'JxqdU3IKHoo-candidate-120-180-copy-v1.mp4',5,'게임 장면 · 호라이즌 제로 던'),native('all-candidates','forest')],[native('all-candidates','map'),native('density-map','map')],[native('density-map','map'),native('road-water-exclusion','map')],[native('all-candidates','map'),native('road-water-exclusion','forest')],[native('terrain-aligned','forest',180),native('terrain-aligned','map',180)],[native('two-placement-layers','forest',180),native('two-placement-layers','map',180)],[native('two-placement-layers','forest',180),game(horizon,'JxqdU3IKHoo-candidate-120-180-copy-v1.mp4',40,'게임 장면 · 호라이즌 제로 던')]],
      inside:[[game(inside,'pressstartplay-9rwA7qvYnds-full-f299-v3.mp4',145,'게임 장면 · INSIDE'),native('no-aa','detail')],[native('jitter-only','detail'),native('temporal-clipping','detail')],[diagram('temporal-reproject'),native('temporal-clipping','full')],[diagram('temporal-clip'),native('naive-history-overlay','detail')],[diagram('temporal-history-blur'),native('temporal-clipping','detail')],[native('no-aa','detail'),native('temporal-clipping','detail')]],
      spider:[[game(spider,'pressstartplay-5Q4AfoUX1eU-swing-120-190-v4.mp4',10,'게임 장면 · PC 리마스터'),native('a','detail')],[diagram('spider-rays'),diagram('spider-rays')],[diagram('spider-volume'),diagram('spider-volume')],[diagram('spider-volume'),diagram('spider-criteria')],[diagram('spider-criteria'),diagram('spider-volume')],[native('a','overview'),native('b','overview')]],
      control:[[game(control,'control-free-TVfahIR7lYQ-candidate-copy-v2.mp4',10,'게임 장면 · Xbox Series S'),native('b','detail')],[diagram('control-hierarchy'),native('b','overview')],[diagram('control-hierarchy'),diagram('control-hierarchy')],[native('a','detail'),native('b','detail')],[native('b','overview'),native('b','detail')],[diagram('control-surface-hole'),diagram('control-hierarchy')]],
      ret:[[game(ret,'nohud-8-OJj2JoPfQ-candidate-45-105-copy-v2.mp4',8,'게임 장면 · PC 녹화'),native('b','detail')],[native('a','overview'),native('b','overview')],[diagram('returnal-delay'),diagram('returnal-delay')],[diagram('returnal-surface'),diagram('returnal-surface')],[diagram('returnal-surface'),diagram('returnal-surface')],[native('b','detail'),game(ret,'nohud-8-OJj2JoPfQ-candidate-45-105-copy-v2.mp4',38,'게임 장면 · PC 녹화')]],
      ratchet:[[game(ratchet,'ratchet-chase-world-transitions-640-703-v4.mp4',29,'게임 장면 · PS5 녹화'),diagram('ratchet-read-decompress')],[diagram('ratchet-read-decompress'),diagram('ratchet-read-decompress')],[diagram('ratchet-read-decompress'),native('a','detail')],[native('a','overview'),native('b','overview')],[diagram('ratchet-read-decompress'),game(ratchet,'ratchet-chase-world-transitions-640-703-v4.mp4',44,'게임 장면 · PS5 녹화')]],
      doom:[[game(doom,'genericbomb-2tXXuiAU1Xs-full-f299-v3.mp4',244,'게임 장면 · DOOM 2016'),native('b','detail')],[game(doom,'genericbomb-2tXXuiAU1Xs-full-f299-v3.mp4',305,'게임 장면 · DOOM 2016'),native('b','overview')],[game(doom,'genericbomb-2tXXuiAU1Xs-full-f299-v3.mp4',247.5,'게임 장면 · DOOM 2016'),native('b','detail')],[native('a','detail'),native('b','detail')],[native('b','detail',360),native('b','overview',360)],[native('b','overview'),game(doom,'genericbomb-2tXXuiAU1Xs-full-f299-v3.mp4',309.5,'게임 장면 · DOOM 2016')]],
      botw:[[game(botw,'botw-part2-rain-candidate-3060-3130-v3.mp4',49,'게임 장면 · 에뮬레이터 녹화'),diagram('botw-rules')],[diagram('botw-rules'),diagram('botw-rules')],[game(botw,'botw-part2-rain-candidate-3060-3130-v3.mp4',50.5,'게임 장면 · 에뮬레이터 녹화'),native('a','detail')],[diagram('botw-rules'),diagram('botw-rules')],[diagram('botw-rules'),diagram('botw-rules')],[native('b','overview',180),native('b','detail',180)],[native('b','overview'),diagram('botw-rules')]],
      kart:[[game(kart,'royaltyfree-npz4T7sznog-full-f299-v3.mp4',224,'게임 장면 · Mario Kart 8'),native('b','detail')],[native('a','detail'),native('b','detail')],[game(kart,'royaltyfree-npz4T7sznog-full-f299-v3.mp4',225.5,'게임 장면 · Mario Kart 8'),native('b','overview')],[game(kart,'royaltyfree-npz4T7sznog-full-f299-v3.mp4',226.5,'게임 장면 · Mario Kart 8'),native('b','detail')],[native('a','overview'),native('b','overview')]]
    }
    results=[]
    for slug in slugs:
        project=ROOT/'projects'/slug;version='edited-v3'if slug==oot else'sentence-v2';clauses_path=project/'planning'/('caption-clauses-'+version+'.json');clauses=read(clauses_path);paragraphs=[]
        assert len(assets[slug])==len(clauses['paragraphs'])
        for para,sources in zip(clauses['paragraphs'],assets[slug]):
            count=len(para['clauses']);beats=[]
            for n,source in enumerate(sources):
                start=0 if n==0 else count//2
                beats.append(dict(firstClauseIndex=start,**source))
            paragraphs.append(dict(id=para['id'],beats=beats))
        output=project/'planning/film-beats-v2.json';assert not output.exists();output.write_text(json.dumps(dict(schemaVersion=1,slug=slug,semanticClauses=pin(clauses_path),paragraphs=paragraphs,beatTimeRule='The actual reviewed onset of firstClauseIndex; no duration allocation by text length.',sourceRepetitionPolicy="No automatic loops; any deliberately repeated game action must be visibly labelled as replay in the pilot.",speed=1,originalGameAndTeachingModelsLabelled=True,nativeFullVisualQaRequired=True,sourceActionRangesNeedContinuousFinalPilotReview=True,timestampsAssigned=False,finalFilmComplete=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');results.append(pin(output))
    print(json.dumps(dict(plans=len(results),timestampsAssigned=False)))
if __name__=='__main__':main()
