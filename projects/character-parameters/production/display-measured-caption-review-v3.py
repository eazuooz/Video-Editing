from pathlib import Path
import json,argparse
BASE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--first',type=int,required=True);ap.add_argument('--last',type=int,required=True);args=ap.parse_args()
j=json.loads((BASE/'caption-candidate-v3/captions.json').read_text('utf-8'))
for p in j['paragraphs']:
 if not args.first<=int(p['scene'][:2])<=args.last:continue
 print(f"\n{p['scene']} p{p['paragraph']} PCM {p['sourceStartSeconds']:.3f}..{p['sourceEndSeconds']:.3f} match={p['characterMatch']:.6f}")
 print('ExpectedKO: '+p['ko']);print('Recognized: '+p['recognizedCompleteParagraph']);print('ExpectedEN: '+p['en'])
 for r in j['ko']:
  if (r['scene'],r['paragraph'])==(p['scene'],p['paragraph']):print(f"KO{r['index']:03} {r['startSeconds']:.3f}..{r['endSeconds']:.3f} [{r['textWidthPx']:.1f}px] {r['ko']}")
 for r in j['en']:
  if (r['scene'],r['paragraph'])==(p['scene'],p['paragraph']):print(f"EN{r['index']:03} {r['startSeconds']:.3f}..{r['endSeconds']:.3f} {r['en']}")
