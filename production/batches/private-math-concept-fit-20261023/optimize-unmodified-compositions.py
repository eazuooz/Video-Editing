from common import *
for episode in ['m05','m06','m07']:
 path=B/f'compose-{episode}.py';s=path.read_text(encoding='utf8')
 if 'passthrough_ok=' in s:continue
 slug={'m05':'game-math-quaternion-foundations-v3','m06':'game-math-quaternion-calculations-v3','m07':'game-math-interpolation-paths-v2'}[episode]
 assert not (R/'projects'/slug/'production/concept-fit-v2/composition.json').exists(),'Do not alter a started composition'
 line="  ff(args+['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-frames:v',n,'-an',*ENC,dst],f'composite-{sid}.log')"
 condition="sid not in SHOTS and not enlarge" if episode=='m05' else 'sid not in SHOTS'
 replacement="  original_video=next(x for x in probe(model)['streams'] if x['codec_type']=='video')\n  passthrough_ok="+condition+" and int(original_video['nb_frames'])==n and original_video['r_frame_rate']=='60/1' and original_video['width']==1920 and original_video['height']==1080 and float(original_video.get('start_time',0))==0\n  if passthrough_ok:\n   shutil.copy2(model,dst)\n   assert sha(dst)==sha(model)\n  else:\n"+' '+line
 assert line in s;s=s.replace(line,replacement).replace("visualReview='pending encoded captioned review'","visualReview='pending encoded captioned review',bytePreservedScene=passthrough_ok")
 compile(s,str(path),'exec');path.write_text(s,encoding='utf8')
save(B/'composition-reuse-decision.json',dict(at=now(),reason='Do not re-encode exact-frame1920x1080p60 clips without new overlays or geometry changes. Final clean/captioned encodes still run with preserved math overlay repairs and actual-file QA.',changesTiming=False,changesSourcePixels=False,finalQualityChecksSkipped=False))
