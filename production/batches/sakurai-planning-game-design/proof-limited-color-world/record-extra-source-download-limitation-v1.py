from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parent
artifact=Path('C:/Users/eazuo/Downloads/chill.mp4');raw=artifact.read_bytes()
digest=hashlib.sha256(raw).hexdigest()
assert len(raw)==248137 and digest=='f431174be1427b854669517b1485d1135ac61ec0f8c07413b45f75c1e0cc8b15'
assert b'<!doctype html' in raw[:200].lower() or b'<!DOCTYPE html' in raw[:200]
assert b'ftyp' not in raw[:100]
dest=P/'official-extra-source-download-limitation-v1.json';assert not dest.exists()
proof=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),
 officialChicoryPressKitChillUrl='https://www.dropbox.com/scl/fo/96x40dg743j9lc43vmzar/ANb12glZQKs0Ye2nh-YPgfE/Video/chill.mp4?rlkey=bweconxebq1n9oz24ljhpgc7l&dl=0',
 observedFileSizeLabel='70.2MB',observedPreview=dict(seconds=56.790067,width=854,height=480,pausedAt=0,actualPixelsAndPlaybackApproved=False),
 attemptedDownload='One CUA matched downloadMedia attempt timed out; preserved artifact is HTML, not a completed media download.',
 artifact=dict(path=artifact.as_posix(),bytes=len(raw),sha256=digest,doctypeHtml=True,ftyp=False),
 actualArtifactInspectionTool='54b923',mediaDecodeAttempted=False,footageAdopted=False,
 previewHlsAssetObserved=True,previewHlsDownloaded=False,rapidRepeatedDownloads=0,remoteInternalApiOrShellUiAccess=0,
 nextAction='Use the reviewed original B1/B2 unique action bank for measured allocation. If more action footage is needed after new voice measurement, inspect a normal official download path through CUA; preserve this failed artifact and avoid guessing internal URLs.',
 gitImagesOrMediaAdded=0)
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(path=dest.as_posix(),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),mediaAdoption=False)))
