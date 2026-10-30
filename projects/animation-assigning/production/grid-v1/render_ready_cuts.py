"""Composite only hash-bound, completed A01 sources. Reuses unchanged cut receipts."""
from pathlib import Path
import subprocess,sys,json
H=Path(__file__).resolve().parent
R=H.parents[3]
def main():
 subprocess.run([sys.executable,'-X','utf8',str(H/'assemble_edit_plan.py')],cwd=R,check=True)
 plan=json.loads((H/'edit-plan.json').read_text('utf8'))
 ids=[c['id'] for c in plan['cuts'] if c['kind']=='independent-gameplay' or c.get('renderedSourceSha256')]
 args=[sys.executable,'-X','utf8',str(H/'video_pipeline.py'),'cuts']
 for key in ids:args+=['--only-cut',key]
 print('READY CUTS',len(ids),'of',len(plan['cuts']),flush=True)
 subprocess.run(args,cwd=R,check=True)
if __name__=='__main__':main()
