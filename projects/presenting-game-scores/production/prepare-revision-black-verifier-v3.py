from pathlib import Path
P=Path(__file__).parent;dst=P/'verify-revision-black-render-v3.py';assert not dst.exists()
t=(P/'verify-measured-black-render-v8.py').read_text('utf-8')
t=t.replace("BASE/'measured-black", "BASE/'revision-balatro60-v2/measured-black")
t=t.replace('-v8','-v3').replace('7333','7707').replace('7334','7708')
dst.write_text(t,'utf-8');print('Prepared new-render verifier only.')
