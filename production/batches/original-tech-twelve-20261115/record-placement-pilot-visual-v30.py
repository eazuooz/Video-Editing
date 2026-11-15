from pathlib import Path
import hashlib,json
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/shorts-horizon-gpu-placement/film-v10')
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=M/'pilot-visual-review.json';assert not p.exists()
samples=sorted((M/'pilot-encoded-qa-v1').glob('cue-*-375.jpg'));assert len(samples)==35
report=dict(pilotProof=pin(M/'pilot-proof.json'),encodedQa=pin(M/'pilot-encoded-qa.json'),actualEncodedSamplesInspected=35,displayWidth=375,captionSamples=[pin(x)for x in samples],findings=['Actual independent PS5 Zero Dawn forest footage introduces the question and returns in the recap.','Authored candidate, density, exclusion, terrain-alignment and layered-placement examples follow the primary-source teaching order.','All35 caption samples were inspected at375px. Title, subject labels and caption margins are readable; no diagram is hidden by captions.','Contact preview temporarily obscures some title headers; individually decoded cue016 retains the full correct title.','The examples are labeled as authored teaching models, not original GPU buffers or measured performance.','Existing-source full capture25 passes7200 encoded-to-source frame checks; small cross-run raster differences are separately disclosed.'],allowedForFinalBundle=True,actualRealtimePlayback=False,actualFullListening=False,humanApproval=False)
p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(pin(p)))
