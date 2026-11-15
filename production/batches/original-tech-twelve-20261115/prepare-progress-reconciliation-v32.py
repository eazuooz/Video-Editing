from pathlib import Path
H=Path(__file__).resolve().parent;R=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z')
def write(p,s):assert not p.exists();p.write_text(s,'utf8')
s=(H/'finalize-production-progress-v23.py').read_text(encoding='utf8').replace('v23','v32').replace('schemaVersion=23','schemaVersion=32')
s=s.replace("selection=ROOT/'projects'/slug/'production/accepted-voice-selection-v10.json'","selection=ROOT/'projects'/slug/('production/accepted-voice-selection-v27.json'if(ROOT/'projects'/slug/'production/accepted-voice-selection-v27.json').exists()else'production/accepted-voice-selection-v10.json')")
needle="review=native and nv.exists()and read(nv).get('allowedForFilm');bundle="
assert needle in s
s=s.replace(needle,"review=native and nv.exists()and read(nv).get('allowedForFilm');bindings=[ROOT/'projects'/slug/('production/film-inputs-'+v+'.json')for v in['v27','v25','v10']];binding=next((x for x in bindings if x.exists()),None)\n  if binding:\n   bound=read(binding);np=Path(bound['nativeFullProofPath']);nv=Path(bound['nativeVisualReviewPath']);native=np.exists();review=native and nv.exists()and read(nv).get('allowedForFilm')\n  bundle=")
s=s.replace("currentState='exact12-local-production-active-two-bundles-verified-eight-voices-accepted'","currentState='exact12-local-production-active-actual-output-reconciled'")
s=s.replace('Existing full guard continues to preserve foreign media work. Exact12 finite CPU controllers wait; no process termination, threshold change, lease reclaim or new automation.','User-authorized below35% start gate is active for this exact12. Original8/9GiB, foreign game/editor/render/model/app checks and exclusive lease remain. Own jobs advance without intermediate approval; original111 and other automations are unchanged.')
s=s.replace("'actual-full-source-verified'if row['nativeFullVisualReviewed']else'explicit-selected-source-full-capture-pending'","'actual-full-source-verified'if row['nativeFullVisualReviewed']else'explicit-selected-source-full-capture-pending'")
write(H/'finalize-production-progress-v32.py',s)
s=(R/'publish-production-resume-v23.py').read_text(encoding='utf8').replace('v23','v32').replace('c939f7b63a2400bf7d35050979fe926229c51c6d','961315852ea74b4211839e8d30883c2212010062').replace('Include exact native recovery shader source with its preserved MIT license and current scoped production state','Advance cooperative production with verified final bundles and scoped caption and native pose repairs')
write(R/'publish-production-resume-v32.py',s)
print('Prepared source-only reconciliation and private-index publisher32')
