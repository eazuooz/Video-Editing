"""Four targeted clarity repairs after whole-take and paired-context ASR."""
import json,pathlib,hashlib
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=rd(H/'current-policy-changes.json');assert not d.get('pronunciationRepairs')
updates={
 '04-p1':('퀘이크는 그 정보를','게임 퀘이크는 그 정보를'),
 '04f-p7':('품질을 높이면 읽고 섞는 비용도 늘 수 있죠.','품질을 높이면 여러 표본을 읽고 섞어야 해서 비용도 늘 수 있죠.'),
 '08-p10':('정적 간접광은 저장해 읽고 직접광은 동적으로 계산할 수 있죠.','정적 간접 조명은 저장된 값을 읽고, 직접 조명은 그때그때 계산할 수 있죠.'),
 '09b-p1':('그 자리의 빛 계산까지 마쳐 색을 내는 방식입니다.','그 자리의 빛 계산을 끝내고 색을 내는 방식입니다.')}
rows=[r for pair in d['pairs'] for r in pair['rows']];by={r['key']:r for r in rows}
for key,(before,after) in updates.items():assert before in by[key]['ko'];by[key]['ko']=by[key]['ko'].replace(before,after)
by['04-p1']['en']=by['04-p1']['en'].replace('Quake stores','The game Quake stores')
by['04f-p7']['en']=by['04f-p7']['en'].replace('Higher quality may require more reads and blending.','Higher quality may require reading and blending more samples.')
repair_ids=[x for x in d['ttsRows'] if x['key'] in updates]
for lang in ['ko','en']:
 wr(P/f'script/continuity-repairs-v2.{lang}.json',dict(scenes=[dict(id=x['id'],title=x['key'],lines=[by[x['key']][lang]]) for x in repair_ids]))
 wr(P/f'script/continuity-v2.{lang}.json',dict(scenes=[dict(id=x['id'],title=x['key'],lines=[by[x['key']][lang]]) for x in d['ttsRows']]))
repair_dir='shared/output/narration/game-lighting-history-01/continuity-v2-repairs'
for x in repair_ids:x['overrideDirectory']=repair_dir
manifest=rd(H/'continuity-tts.project.json');manifest['tts'].update(outputDir=repair_dir,filenameStem='continuity-v2-repairs')
manifest['paths'].update(script='projects/game-lighting-history-01/script/continuity-repairs-v2.ko.json',scriptEn='projects/game-lighting-history-01/script/continuity-repairs-v2.en.json')
manifest['status']='four-context-confirmed-pronunciation-repairs';wr(H/'continuity-repair-tts.project.json',manifest)
d['pronunciationRepairs']=dict(ids=[x['id'] for x in repair_ids],reason='Repeated ambiguity in complete contexts: Quake, blending cost, calculate, finish. Rewrite complete paragraphs for clarity; no syllable-level patch or speed change.',previousSourceCommit='131c0d240c246ad58d3745edc6e9bd9c9995ec1b',priorWavPreserved=True,contextDirectory='production/local/continuity-v2/context-asr',asrHallucination='Pair01 appends nonexistent subtitle credits after actual final speech. Original whole c02 text has no such words; review actual sample duration and final mix instead of treating this recognition tail as narration.')
d['scriptHashes']={lang:hashlib.sha256((P/f'script/continuity-v2.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']}
wr(H/'current-policy-changes.json',d)
print(json.dumps(dict(repairIds=d['pronunciationRepairs']['ids'])))
