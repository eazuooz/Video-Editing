from pathlib import Path
import argparse,json
R=Path(__file__).resolve().parents[4];D=R/'projects/game-reward-planning/production/reference-preserving-v2'
p=argparse.ArgumentParser();p.add_argument('--check',choices=['asr','integrity'],required=True);args=p.parse_args();f=D/('review-final-audio.py' if args.check=='asr' else 'verify-output.py');s=f.read_text(encoding='utf8')
s=s.replace("'production/local/reference-preserving-v2/edit'","'production/local/reference-preserving-v2/edit/original-deletion-v4'").replace("'projects/game-reward-planning/production/local/reference-preserving-v2/edit'","'projects/game-reward-planning/production/local/reference-preserving-v2/edit/original-deletion-v4'").replace('production/reference-preserving-v2/edit-plan.json','production/reference-preserving-v2/original-deletion-v4-plan.json').replace('script/reference-preserving-v2/narration.tts.ko.json','script/original-deletion-v4/narration.tts.ko.json')
exec(compile(s,str(f),'exec'),{'__file__':str(f)})
