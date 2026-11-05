"""Verify the actual local review UI in a separate, clean browser profile."""
import json,os,subprocess,tempfile,time,urllib.request
from pathlib import Path
import websocket
from delivery import DEST,SL,W,write
def run():
 return run_review(DEST,W,SL,76.783,1929.933333)
def run_review(dest,work,slug,initial,expected_duration):
 exe=next((Path.home()/'.cache/puppeteer/chrome').glob('*/chrome-win64/chrome.exe'),None) or Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
 fragment=f'#t={initial:.3f}'
 url='http://127.0.0.1:9347/output/'+dest.name+'/index.html'+fragment
 req=urllib.request.Request(url.split('/index')[0]+'/'+slug+'.captioned.mp4',headers={'Range':'bytes=0-31'})
 with urllib.request.urlopen(req,timeout=4) as resp:assert resp.status==206 and len(resp.read())==32
 with tempfile.TemporaryDirectory(dir=work,ignore_cleanup_errors=True) as prof:
  proc=subprocess.Popen([str(exe),'--headless=new','--disable-gpu','--no-first-run','--disable-background-networking','--remote-debugging-port=0','--autoplay-policy=no-user-gesture-required','--mute-audio','--user-data-dir='+prof,url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   portfile=Path(prof)/'DevToolsActivePort'
   for _ in range(160):
    if portfile.exists() and portfile.stat().st_size:break
    if proc.poll() is not None:raise RuntimeError('Test browser did not start')
    time.sleep(.1)
   port=portfile.read_text().splitlines()[0]
   for _ in range(100):
    tabs=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/json/list',timeout=3))
    tab=next((q for q in tabs if q['type']=='page' and q.get('webSocketDebuggerUrl')),None)
    if tab:break
    time.sleep(.1)
   else:raise RuntimeError('The isolated test browser did not expose a page target')
   ws=websocket.create_connection(tab['webSocketDebuggerUrl'],suppress_origin=True,timeout=45);idx=0
   def evaluate(expression):
    nonlocal idx
    idx+=1;ws.send(json.dumps(dict(id=idx,method='Runtime.evaluate',params=dict(expression=expression,returnByValue=True,awaitPromise=True))))
    while True:
     reply=json.loads(ws.recv())
     if reply.get('id')==idx:break
    if 'error' in reply:raise RuntimeError(str(reply['error']))
    assert 'exceptionDetails' not in reply['result'],reply
    return reply['result']['result'].get('value')
   for _ in range(100):
    try:
     if evaluate(f"document.readyState==='complete'&&location.hash==={json.dumps(fragment)}&&document.querySelector('video')?.readyState>=2"):break
    except RuntimeError:pass
    time.sleep(.12)
   evidence=evaluate("""(async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));let v;
   const entry=Number(location.hash.slice(3));
   for(let i=0;i<150;i++){v=document.querySelector('video');if(v?.readyState>=2&&Math.abs(v.currentTime-entry)<.1)break;await wait(100)}
   const requested=v.currentTime, measures=[];
   for(const index of [-1,2,3,5]){const link=index<0?null:document.querySelectorAll('[data-t]')[index];
   const target=link?Number(link.dataset.t):entry;if(link)link.click();else await v.play();
   for(let i=0;i<100;i++){if(!v.seeking && v.currentTime>=target && v.currentTime<target+3 && !v.paused)break;await wait(90)}
   const a=v.currentTime,frames=v.getVideoPlaybackQuality().totalVideoFrames;
   await wait(950);measures.push({target,from:a,to:v.currentTime,frames:v.getVideoPlaybackQuality().totalVideoFrames-frames,
   width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null});v.pause()}
   return {fragment:requested,duration:v.duration,measures}})()""")
   assert abs(evidence['fragment']-initial)<.1 and abs(evidence['duration']-expected_duration)<.05
   for m in evidence['measures']:assert m['width']==1920 and m['height']==1080 and m['frames']>0 and m['to']-m['from']>.1 and abs(m['from']-m['target'])<2 and not m['error'],m
   write(work/'final-qa/browser-playback.json',dict(url=url,httpRange=206,isolatedBrowser=exe.name,**evidence));ws.close()
  finally:
   proc.terminate();proc.wait(timeout=15)
if __name__=='__main__':run()
