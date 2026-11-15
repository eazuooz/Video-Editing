from pathlib import Path
H=Path(__file__).resolve().parent;R=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z')
def write(p,s):assert not p.exists();p.write_text(s,'utf8')
s=(H/'finalize-production-progress-v43.py').read_text(encoding='utf8').replace('v43','v49').replace('schemaVersion=43','schemaVersion=49')
needle="page=HERE/'production-progress-v49.html';progress=";assert needle in s
s=s.replace(needle,"""for row in rows:
  P=ROOT/'projects'/row['slug'];bindings=[P/('production/film-inputs-'+v+'.json')for v in['v37','v33','v27','v25','v10']];binding=next((x for x in bindings if x.exists()),None);review=Path(read(binding)['mixProofPath']).parent/'mixed-content-review.json'if binding else None
  row['mixedAudioContentAndLevelsReviewed']=bool(row['finalVideo']or(review and review.exists()and read(review).get('approvedForPilot')))
 page=HERE/'production-progress-v49.html';progress=""")
s=s.replace("nativeActualSmokeGroups=6,", "mixedAudioContentAndLevelsReviewed=sum(x['mixedAudioContentAndLevelsReviewed']for x in rows),nativeActualSmokeGroups=6,");write(H/'finalize-production-progress-v49.py',s)
s=(R/'publish-production-resume-v43.py').read_text(encoding='utf8').replace('v43','v49').replace('2f059ca32d46836eab75478b711bd89d3b625562','a6dd13a89e2c8901645af6b126c7224f6637248f').replace('Preserve exact first-pose evidence and bind remaining reviewed native films with finite local QA completion','Verify all12 mixed narrations and full temporal source capture; retain scoped native and final QA continuation');write(R/'publish-production-resume-v49.py',s);print('Prepared audio and actual native progress49')
