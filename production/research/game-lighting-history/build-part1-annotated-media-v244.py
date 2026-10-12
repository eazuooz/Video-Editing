"""One CPU visual build, retaining the sealed mix and every input frame count."""
from pathlib import Path
import sys
source=Path(__file__).with_name('build-part1-final-media-v242.py').read_text('utf8')
assert '--phase' in sys.argv and sys.argv[sys.argv.index('--phase')+1]=='visual'
source=source.replace("local/part1-final-v242'","local/part1-final-v244'")
source=source.replace("f'part1-final-{a.phase}-execution-v242.json'","f'part1-final-{a.phase}-execution-v244.json'")
source=source.replace("P/'part1-final-visual-build-v242.json'","P/'part1-final-visual-build-v244.json'")
source=source.replace("SP=P/f'part1-final-", "layerPath=P/'part1-visual-layers-v244.json';layers=read(layerPath);assert layers['inputPlan']['sha256']==sha(PP)\nSP=P/f'part1-final-")
source=source.replace('rect=None,matte=0):','rect=None,matte=0,tracking=None,offset=0):')
source=source.replace("if matte:vf += [f'crop=1920:{1080-matte}:0:{matte}',f'pad=1920:1080:0:0:black']", "if matte:vf += [f\"crop=1920:{1080-matte}:0:{0 if tracking and tracking.get('matteFrom')=='bottom' else matte}\",f'pad=1920:1080:0:0:black']")
needle=" if annotation:\n"
insert=''' if tracking:
  if tracking.get('label'):vf.append(source_label(tracking['label'],label+'-target',x=tracking.get('labelX',600),y=tracking.get('labelY',110),size=28))
  for b in tracking['boxes']:
   start=max(0,b['from']-offset);end=min(frames/60,b['to']-offset)
   if end<=start:continue
   duration=b['to']-b['from'];x=f"{b['x0']}+({b['x1']-b['x0']})*(t+{offset}-{b['from']})/{duration}";y=f"{b['y0']}+({b['y1']-b['y0']})*(t+{offset}-{b['from']})/{duration}"
   vf.append(f"drawbox=x='{x}':y='{y}':w={b['width']}:h={b['height']}:color={b['color']}:t=4:enable='gte(t,{start})*lt(t,{end})'")
'''
assert needle in source;source=source.replace(needle,insert+needle)
needle="    for k,cut in enumerate(c['proposedCuts']):"
source=source.replace(needle,"    offset=0\n"+needle)
needle="labels=[c['identityLabel'],c.get('onScreenConditionLabel')]);pieces.append(segment)"
replacement="labels=[c['identityLabel'],c.get('onScreenConditionLabel')],tracking=layers['layers'].get(c['id']),offset=offset);pieces.append(segment);offset+=(cut['outFrame']-cut['inFrame'])/60"
assert needle in source;source=source.replace(needle,replacement)
source=source.replace("'sourceModelsRerendered':0,'newGitImages':0}","'sourceModelsRerendered':0,'newGitImages':0,'editableVisualLayers':{'path':rel(layerPath),'sha256':sha(layerPath)}}")
exec(compile(source,str(Path(__file__)),'exec'))
