"""Record real missing requirements before allocation; never fake inferred frames."""
from pathlib import Path
import json,datetime
H=Path(__file__).resolve().parent
B=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/Sprite-Sheet-Diffusion/ModelTraining')
source=(B/'inference.py').read_text('utf8')
model=B/'pretrained_model'
required=['denoising_unet.pth','reference_unet.pth','motion_module.pth','pose_guider.pth','image_encoder/pytorch_model.bin']
state={f:(model/f).exists() for f in required}
rec={'checkedAt':datetime.datetime.now().isoformat(),'result':'blocked-before-inference','officialCodeRequiresPoseGuider': 'pose_guider' in source,'files':state,'officialIssue':'https://github.com/chenganhsieh/Sprite-Sheet-Diffusion/issues/3','companionDownloads':json.loads((model/'companion-download-record.json').read_text('utf8')),'actualInferenceExecuted':False,'randomWeightsUsed':False,'generatedFrames':0,'substitution':'Moore PoseGuider downloaded for investigated compatibility path; not passed off as original SSD trained guider'}
(H/'ssd-execution-attempt.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(rec,ensure_ascii=False,indent=2))
raise SystemExit(2 if not all(state.values()) else 0)
