from pathlib import Path
H=Path(__file__).resolve().parent
def write(p,s):assert not p.exists(),p;p.write_text(s,'utf8')
s=(H/'run-ready-local-pilots-v38.py').read_text(encoding='utf8').replace('finite-ready-pilots-v38','finite-ready-pilots-v54');s=s.replace("helper=H/'run-lesson-film-v37-cooperative-v19.py';hp=pin(helper);", "helpers={v:pin(H/('run-lesson-film-'+v+'-cooperative-v19.py'))for v in['v37','v53']};")
s=s.replace("bp=P/('production/film-inputs-v37.json'if", "bp=P/('production/film-inputs-v53.json'if(P/'production/film-inputs-v53.json').exists()else'production/film-inputs-v37.json'if")
s=s.replace("assert pin(helper)==hp;log=", "version='v53'if chosen in['shorts-control-destruction-pipeline','shorts-doom-push-forward-healing']else'v37';helper=H/('run-lesson-film-'+version+'-cooperative-v19.py');assert pin(helper)==helpers[version];log=");write(H/'run-ready-local-pilots-v54.py',s)
s=(H/'run-reviewed-local-finals-v42.py').read_text(encoding='utf8').replace('finite-reviewed-finals-v42','finite-reviewed-finals-v54');s=s.replace("'finalize-local-bundle-v37.py']", "'finalize-local-bundle-v37.py','run-lesson-film-v53-cooperative-v19.py','finalize-local-bundle-v53.py']")
s=s.replace("run('run-lesson-film-v37-cooperative-v19.py',chosen,", "run('run-lesson-film-v53-cooperative-v19.py'if chosen in['shorts-control-destruction-pipeline','shorts-doom-push-forward-healing']else'run-lesson-film-v37-cooperative-v19.py',chosen,")
s=s.replace("run('finalize-local-bundle-v37.py',chosen,", "run('finalize-local-bundle-v53.py'if chosen in['shorts-control-destruction-pipeline','shorts-doom-push-forward-healing']else'finalize-local-bundle-v37.py',chosen,");write(H/'run-reviewed-local-finals-v54.py',s)
print('Prepared project-specific immutable renderer routes; completed pilots will be skipped')
