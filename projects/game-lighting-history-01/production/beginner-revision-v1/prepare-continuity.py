"""Prepare additive narration inputs for paired chapter transitions."""
import datetime, hashlib, json, pathlib, runpy
R=pathlib.Path(__file__).resolve().parents[4]
P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
runpy.run_path(str(H/'production-authority.py'))['require_selected_production']()
d=read(H/'current-policy-changes.json');assert d['review']['koEnDirectRead']
rows=[r for pair in d['pairs'] for r in pair['rows']]
assert len(rows)==14 and len({r['key'] for r in rows})==14
for lang in ['ko','en']:
 path=P/f'script/continuity-v2.{lang}.json'
 write(path,dict(scenes=[dict(id=f'c{i:02}',title=r['key'],lines=[r[lang]]) for i,r in enumerate(rows,1)]))
manifest=read(H/'tts.project.json')
manifest['tts'].update(outputDir='shared/output/narration/game-lighting-history-01/continuity-v2',filenameStem='continuity-v2',maxRenderAttempts=1)
manifest['paths'].update(script='projects/game-lighting-history-01/script/continuity-v2.ko.json',scriptEn='projects/game-lighting-history-01/script/continuity-v2.en.json')
manifest['status']='14-paired-transition-replacements-script-reviewed'
manifest['voiceRepair']['scope']='Only14 paired chapter-transition paragraphs. All baseline files remain immutable.'
write(H/'continuity-tts.project.json',manifest)
d['ttsRows']=[dict(id=f'c{i:02}',key=r['key']) for i,r in enumerate(rows,1)]
d['scriptHashes']={lang:hashlib.sha256((P/f'script/continuity-v2.{lang}.json').read_bytes()).hexdigest() for lang in ['ko','en']}
write(H/'current-policy-changes.json',d)
ck=read(P/'production/checkpoint.json');ck['currentSelection']['mediaRestoreStatus']='all274-hashes-verified';ck['currentSelection']['recoveryReceipt']='production/beginner-revision-v1/drive-recovery-receipt.json'
ck['beginnerRevision'].update(status='current-policy-transition-voice-prepared',recoveredMediaFiles=274,newUpload=False)
ck.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage='paired-transition-voice-prepared',nextAction='Generate14 changed paragraphs, measure real timing, preserve all unaffected voice and media; complete final review to Drive.')
write(P/'production/checkpoint.json',ck)
print(json.dumps(dict(recoveredFiles=274,preparedParagraphs=14,scriptHashes=d['scriptHashes'])))
