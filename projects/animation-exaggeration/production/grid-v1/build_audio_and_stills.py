"""Sequential A02 CPU mix and four source-frame plates; no Unity/UI/TTS."""
from pathlib import Path
import subprocess,sys
import audio_pipeline as ap
H=Path(__file__).resolve().parent
R=H.parents[3]
def run(*args):
    subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=R,check=True)
def main():
    proposal=ap.read(H/'measured-edit-plan.proposal.json')
    ap.save(H/'audio-plan.json',proposal)
    run(H/'audio_pipeline.py','mix','--plan',H/'audio-plan.json')
    for spec in sorted((H/'still-specs').glob('*.json')):
        run(H/'render_still.py','--spec',spec)
    print('A02 continuous mix and four exact inspected source-frame plates complete.',flush=True)
if __name__=='__main__':main()
