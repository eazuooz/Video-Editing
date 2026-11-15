"""Add explicit cooperative launchers; preserve all original source versions."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def main():
 names=['run-inside-voice-repair-v9.py','run-inside-voice-repair-asr-v9.py','run-clear-sentence-voice-repair-v15.py','run-clear-sentence-voice-repair-asr-v15.py','run-additional-master-voice-repair-asr-v14.py','run-lesson-mixed-voice-repair-asr-v10.py','run-inside-mixed-voice-repair-asr-v13.py','prepare-lesson-mix-v10.py','prepare-inside-paired-mix-v13.py','run-lesson-film-v10.py']
 rows=[]
 for name in names:
  p=HERE/name;t=p.read_text('utf-8-sig');target=HERE/(p.stem+'-cooperative-v19.py');assert not target.exists(),target
  # The new filename is part of every new model/mix/film identity. Existing
  # generated sources, output proofs and old helper hashes remain unchanged.
  at=t.index('\ndef ',t.index("run-camera-native-v1.py"))
  inject="\n_policy_spec=importlib.util.spec_from_file_location('exact12_cooperative_policy',HERE/'cooperative-resource-policy-v19.py');_policy=importlib.util.module_from_spec(_policy_spec);_policy_spec.loader.exec_module(_policy);_policy.install(native)\n"
  t=t[:at]+inject+t[at:];t=t.replace('use>=15','use>=35').replace('utilization below15%','utilization below35%')
  # Keep wait-minutes15 (bounded startup and exact bootstrap argv) unchanged.
  if "paths=["in t:
   t=t.replace('paths=[',"paths=[HERE/'resource-policy-v19.json',HERE/'cooperative-resource-policy-v19.py',",1)
  # Record the applied execution policy beside the immutable content identity.
  if 'identity=dict('in t:t=t.replace('identity=dict(',"identity=dict(executionResourcePolicy=native.cooperative_policy_proof,",1)
  ast.parse(t);target.write_text(t,'utf8');rows.append(dict(original=pin(p),cooperative=pin(target),baselineMeaningAndPcmPolicyUnchanged=True))
 out=HERE/'cooperative-execution-source-review-v19.json';assert not out.exists();out.write_text(json.dumps(dict(policy=pin(HERE/'resource-policy-v19.json'),adapter=pin(HERE/'cooperative-resource-policy-v19.py'),newHelpers=rows,utilizationChangeOnly=True,allExistingInputsPreserved=True,newModelsStarted=False),indent=2)+'\n','utf8');print(out)
if __name__=='__main__':main()
