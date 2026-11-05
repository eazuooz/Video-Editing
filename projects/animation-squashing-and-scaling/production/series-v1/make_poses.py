"""Render each mathematical comparison from its editable Manim scene."""
from pathlib import Path
import subprocess,shutil,hashlib,json
H=Path(__file__).resolve().parent; P=H.parents[1]; R=P.parents[1]; L=P/'production/local/series-v1'
if __name__=='__main__':
    tool=R/'manim/.venv/Scripts/python.exe'
    source=hashlib.sha256((H/'shape_studies.py').read_bytes()).hexdigest()
    receipt=L/'manim-plates.json'
    existing=json.loads(receipt.read_text('utf-8')) if receipt.is_file() else {}
    for scene in ('Bounce','Volume','Morph','Fist'):
        dest=L/(scene.lower()+'.mp4')
        if existing.get(scene)==source and dest.is_file():continue
        subprocess.run([tool,'-m','manim','render','--disable_caching','-r','1920,1080','--fps','60',
                        '--media_dir',L/'manim-renders',H/'shape_studies.py',scene],cwd=R,check=True)
        matches=list((L/'manim-renders').rglob(scene+'.mp4'))
        assert len(matches)==1,matches
        shutil.copy2(matches[0],dest)
        existing[scene]=source
        receipt.write_text(json.dumps(existing),'utf-8')
