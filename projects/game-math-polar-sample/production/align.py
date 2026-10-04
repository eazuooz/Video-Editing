"""Keep the repository's 93% matching gate; normalize observed spoken math.

Whisper writes 4/3/5/37 and cos/sin/R where the Korean script speaks the
corresponding words. Do not change recognized words, audio hashes or times.
"""
from pathlib import Path
import sys,json,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'qwen3-tts'))
import align_project_subtitles as alignment
original=alignment.normalized
def math_normalized(value):
    s=original(value)
    for a,b in [('코사인','cos'),('사인','sin'),('삼십칠','37'),('다섯','5'),('네칸','4칸'),('세칸','3칸'),('길이는네','길이는4'),('길이는셋','길이는3'),('거리를알','거리를r')]:
        s=s.replace(a,b)
    return s
alignment.normalized=math_normalized
if __name__=='__main__':
    sys.argv=[sys.argv[0],'--project','game-math-polar-sample']
    alignment.main()
    m=json.loads((ROOT/'projects/game-math-polar-sample/project.json').read_text(encoding='utf8'))
    for lang in ['ko','en']:
        shutil.copy2(ROOT/m['paths']['captions'+lang.title()],ROOT/f'projects/game-math-polar-sample/script/voice-aligned.{lang}.srt')
