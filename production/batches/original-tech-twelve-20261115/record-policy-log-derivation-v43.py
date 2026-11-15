from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];p=H/'run-reviewed-pose-native-v35.py';source=p.read_text(encoding='utf8');block=""" save=m.save
 def observed_save(path,d):
  if Path(path).name in ['launch.json','accepted-full.json']:d=dict(d,utilizationBelow=35,executionResourcePolicy=m.native.cooperative_policy_proof,executionReviewAdapter=m.pin(__file__))
  return save(path,d)
 m.save=observed_save
""";assert source.count(block)==1;original=source.replace(block,'');proof=ROOT/'shared/output/original-tech-twelve-20261115/remaining-seven/native-reviewed-pose-v35/accepted-smoke.json';d=json.loads(proof.read_text(encoding='utf8'));expected=d['executionReviewAdapter'];assert hashlib.sha256(original.encode('utf8')).hexdigest()==expected['sha256'];snapshot=H/'native-pose-warmup-v30/review-adapter-before-policy-log-v35.py';assert not snapshot.exists();snapshot.write_text(original,'utf8')
pin=lambda x:dict(path=str(x.resolve()),sha256=hashlib.sha256(x.read_bytes()).hexdigest());out=H/'policy-log-derivation-v43.json';assert not out.exists();out.write_text(json.dumps(dict(historicalReviewAdapter=expected,exactHistoricalSourceSnapshot=pin(snapshot),currentExecutionAdapter=pin(p),onlyChange='Attach the already authorized35% policy and execution adapter identity to new launch/full-proof JSON records. Pixel verification, model states, startup correction, source bytes and full-to-smoke equality are unchanged.',historicalProofPreserved=pin(proof),narrationQualityThresholdsChanged=False),indent=2)+'\n','utf8');print(json.dumps(pin(out)))
