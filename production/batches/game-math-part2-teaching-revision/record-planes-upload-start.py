"""Record the real native Studio ID while transport/platform checks remain pending."""
from pathlib import Path
import datetime,json,sys
ROOT=Path(__file__).resolve().parents[3]
slug,video_id=sys.argv[1:3]
assert slug in ['game-math-plane-distances-v2','game-math-triangle-addresses-v2']
assert len(video_id)==11 and all(c.isalnum() or c in '-_' for c in video_id)
p=ROOT/'projects'/slug/'publishing/youtube-upload.json'
d=json.loads(p.read_text(encoding='utf8'))
assert d['videoId'] in [None,video_id]
d.update(videoId=video_id,url='https://youtu.be/'+video_id,status='actual-native-Studio-private-upload-started; transport and full platform verification pending',uploadStartedObservedAt=datetime.datetime.now().astimezone().isoformat(),scheduled=False,fullPublishingSettingsComplete=False)
d['platformObserved']={'nativeStudioVideoId':video_id,'privacySelectedAndSaveSubmitted':'private','transportComplete':False,'copyrightAndAdChecksComplete':False,'uploadedCaptionPixelsVerified':False}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Preserved actual in-flight ID:',video_id)
