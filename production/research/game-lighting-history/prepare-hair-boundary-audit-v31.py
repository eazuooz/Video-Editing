from pathlib import Path
p=Path(__file__).with_name('audit-hair-boundary-v30.py')
s=p.read_text('utf-8').replace("'-fps_mode','vfr'","'-fps_mode','passthrough'").replace("'-threads','2','-i'","'-threads','2','-reinit_filter','0','-i'").replace('hair-clean-captioned-boundary-audit-v30','hair-clean-captioned-boundary-audit-v32')
q=p.with_name('audit-hair-boundary-v32.py');assert not q.exists();q.write_text(s,'utf-8')
