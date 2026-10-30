"""Create the local review page from verified, immutable four-file outputs."""
from pathlib import Path
import json, hashlib, html
from datetime import datetime, timezone
from audio_revision import P, REVISION

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def encode(value): return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf8')

def main():
    project=json.loads((P/'project.json').read_text(encoding='utf8'))
    out=P/project['currentFinalDirectory']
    integrity=json.loads((out/'integrity.json').read_text(encoding='utf8'))
    assert integrity['status']=='pass'
    metadata=json.loads((P/'publishing/metadata.json').read_text(encoding='utf8'))
    captions=json.loads((P/'script/captions.json').read_text(encoding='utf8'))
    files=[{'name':n,'path':str((out/n).resolve()),'sha256':sha(out/n),'bytes':(out/n).stat().st_size} for n in ['clean.mp4','captioned.mp4','captions.ko.srt','captions.en.srt']]
    assert next(x['sha256'] for x in files if x['name']=='captioned.mp4')==next(x['sha256'] for x in integrity['outputs'] if x['name']=='captioned')
    manifest={'revision':REVISION,'generatedAt':datetime.now(timezone.utc).isoformat(),'width':1080,'height':1920,'fps':60,'frames':captions['frames'],'durationSeconds':captions['durationSeconds'],'title':metadata['title'],'description':metadata['description'],'files':files,'localFinalReview':'awaiting-human-review','actualCompleteHumanListening':False,'youtubeUploaded':False,'driveUploaded':False}
    (out/'delivery.json').write_bytes(encode(manifest))
    (out/'metadata.json').write_bytes(encode(metadata))
    (out/'SHA256SUMS.txt').write_bytes(('\n'.join(x['sha256']+'  '+x['name'] for x in files)+'\n').encode())
    links=' · '.join('<a href="'+x['name']+'">'+html.escape(x['name'])+'</a>' for x in files)
    script=''.join('<p>'+html.escape(line)+'</p>' for line in (P/'script/narration.ko.txt').read_text(encoding='utf8').strip().split('\n\n'))
    page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>팩토리오 쇼츠 검수 · 얌얌코딩</title><style>body{margin:0;background:#080b0a;color:#f5f5f2;font:16px/1.7 "Malgun Gothic",sans-serif}main{max-width:920px;margin:auto;padding:24px}h1{font-size:26px;color:#ffdc62;line-height:1.4}video{display:block;width:min(100%,420px);margin:24px auto;background:#000}a{color:#83d8bc}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}details{border-top:1px solid #36413b;margin-top:24px;padding-top:16px}.muted{color:#b4bdb7}code{overflow-wrap:anywhere}</style><main><h1>'''+html.escape(metadata['title'])+'''</h1><p>1080 × 1920 · 60fps · '''+f"{captions['durationSeconds']:.2f}"+'''초 · '''+REVISION+'''</p><video controls playsinline preload="metadata" src="captioned.mp4"></video><p>'''+links+'''</p><p><a href="metadata.json">제목·설명</a> · <a href="SHA256SUMS.txt">파일 해시</a> · <a href="delivery.json">납품 기록</a></p><p class="muted">완성 파일의 기술 무결성·음량·음성 인식 대조와 표본 화면 검수는 별도 기록으로 확인합니다. 실제 전체 청취·사용자 최종검수는 아직 완료된 것으로 간주하지 않습니다.</p><details><summary>전체 대본</summary>'''+script+'''</details><details><summary>YouTube 설명 초안</summary><pre>'''+html.escape(metadata['description'])+'''</pre></details></main></html>'''
    (out/'index.html').write_bytes(page.encode('utf8'))
    print(json.dumps({'reviewPage':str((out/'index.html').resolve()),'files':files},ensure_ascii=False))

if __name__=='__main__': main()
