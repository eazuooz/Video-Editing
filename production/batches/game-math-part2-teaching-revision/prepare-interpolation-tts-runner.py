"""Freeze the existing approved voice/reference and new script hashes."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-interpolation-teaching-additions-v2';P=ROOT/'projects'/slug
def read(p):return json.loads(p.read_text(encoding='utf8'))
m=read(P/'project.json');base=read(B/'baselines/game-math-rotation-interpolation/project.json')
assert m['tts']['renderMode']=='line'
for key in ['engine','language','reference','referenceText','model','tailRatioThreshold','tailDecayMsThreshold','maxRenderAttempts','maxNewTokens','edgeFadeSeconds']:
    assert m['tts'][key]==base['tts'][key],key
audit=read(B/'interpolation-pretts-audit.json')
audit['voiceSettingsExact']={k:m['tts'][k] for k in ['engine','language','reference','referenceText','model','tailRatioThreshold','tailDecayMsThreshold','maxRenderAttempts','maxNewTokens','edgeFadeSeconds']}
audit['voiceReferenceSha256']={k:hashlib.sha256((ROOT/m['tts'][k]).read_bytes()).hexdigest() for k in ['reference','referenceText']}
audit['projectManifestSha256']=hashlib.sha256((P/'project.json').read_bytes()).hexdigest()
(B/'interpolation-pretts-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
text=(B/'render-narration-v6.py').read_text(encoding='utf8').replace('game-math-quaternion-teaching-additions-v6',slug).replace('quaternion-v6-pretts-audit.json','interpolation-pretts-audit.json').replace("audit['original26ScenesAnd155KoLinesExact']","audit['allOriginalSceneDictionariesExact'] and audit['originalOrderAndContractExact'] and audit['gameplayComparedBeforeDependentNarration']").replace('quaternion-v6-line-provenance.json','interpolation-line-provenance.json')
text=text.replace("for lang,sha in audit['scriptSha256'].items():", "assert hashlib.sha256((ROOT/f'projects/{slug}/project.json').read_bytes()).hexdigest()==audit['projectManifestSha256']\nfor key,sha in audit['voiceReferenceSha256'].items():assert hashlib.sha256((ROOT/audit['voiceSettingsExact'][key]).read_bytes()).hexdigest()==sha\nassert all(c['passed'] for c in audit['checks'])\nfor lang,sha in audit['scriptSha256'].items():")
(B/'render-interpolation-narration.py').write_text(text,encoding='utf8')
print('New70 lines frozen with the unchanged approved voice/reference and gates; guarded runner prepared.')
