from pathlib import Path
import json
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
topics=['titanfall','superliminal','ghost','gears','portal']
for row,topic in zip(json.loads((B/'batch.json').read_text(encoding='utf8'))['projects'],topics):
 slug=row['slug'];folder=R/'motion-canvas/src/projects/distinctive-shorts-20261024'/topic;folder.mkdir(parents=True,exist_ok=True)
 (folder/'scene.tsx').write_text(f"import timing from '../../../../../projects/{slug}/production/visual-timing.json';\nimport native from '../../../../../projects/{slug}/production/local/capture-full-v1/readback.json';\nimport {{composite}} from '../composite';\nexport default composite('{topic}','{slug}',timing,native);\n",encoding='utf8')
 (folder/'project.ts').write_text(f"import {{makeProject}} from '@motion-canvas/core';\nimport scene from './scene?scene';\nexport default makeProject({{name:'{slug}',scenes:[scene]}});\n",encoding='utf8')
 p=R/'projects'/slug/'production';base=(R/'projects/shorts-interior-mapping-window/production/render-visual.cjs').read_text(encoding='utf8')
 a=base.index("if(control.selectedShortVideo");b=base.index('const timing=',a);base=base[:a]+f"if(!control.shortsBatchAuthorization?.slugs.includes('{slug}')||control.shortsBatchAuthorization.status!=='active')throw Error('Batch selection changed');\n"+base[b:]
 base=base.replace("control.shortsDirectSelection?.fullProductionAuthorized","control.shortsBatchAuthorization?.fullProductionAuthorized").replace('capture-full/','capture-full-v1/').replace('interior-mapping-v1-full','distinctive-v1-full').replace('9252','9265').replace('shorts-interior-mapping-window',slug).replace(f'/src/projects/{slug}/project.ts',f'/src/projects/distinctive-shorts-20261024/{topic}/project.ts')
 (p/'render-visual.cjs').write_text(base,encoding='utf8')
print('Five Motion Canvas project routes prepared')
