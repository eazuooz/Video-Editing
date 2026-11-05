"""Verify the actual local review UI in a separate, clean browser profile."""
import json,os,subprocess,tempfile,time,urllib.request
from pathlib import Path
import websocket
from delivery import DEST,SL,W,write
def run():
 exe=next((Path.home()/'.cache/puppeteer/chrome').glob('*/chrome-win64/chrome.exe'),None) or Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
 url='http://127.0.0.1:9347/output/'+DEST.name+'/index.html#t=76.783'
 req=urllib.request.Request(url.split('/index')[0]+'/'+SL+'.captioned.mp4',headers={'Range':'bytes=0-31'})
 with urllib.request.urlopen(req,timeout=4) as resp:assert resp.status==206 and len(resp.read())==32
 with tempfile.TemporaryDirectory(dir=W,ignore_cleanup_errors=True) as prof:
  proc=subprocess.Popen([str(exe),'--headless=new','--disable-gpu','--no-first-run','--disable-background-networking','--remote-debugging-port=0','--autoplay-policy=no-user-gesture-required','--mute-audio','--user-data-dir='+prof,url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   portfile=Path(prof)/'DevToolsActivePort'
   for _ in range(160):
    if portfile.exists() and portfile.stat().st_size:break
    if proc.poll() is not None:raise RuntimeError('Test browser did not start')
    time.sleep(.1)
   port=portfile.read_text().splitlines()[0]
   tabs=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/json/list'))
   tab=next(q for q in tabs if q['type']=='page')
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
     if evaluate("document.readyState==='complete'&&location.hash==='#t=76.783'&&document.querySelector('video')?.readyState>=2"):break
    except RuntimeError:pass
    time.sleep(.12)
   evidence=evaluate("""(async()=>{const wait=ms=>new Promise(r=>setTimeout(r,ms));let v;
   for(let i=0;i<150;i++){v=document.querySelector('video');if(v?.readyState>=2&&v.currentTime>76)break;await wait(100)}
   const requested=v.currentTime, measures=[];
   for(const index of [-1,2,3,5]){const link=index<0?null:document.querySelectorAll('[data-t]')[index];
   const target=link?Number(link.dataset.t):76.783;if(link)link.click();else await v.play();
   for(let i=0;i<100;i++){if(!v.seeking && v.currentTime>=target && v.currentTime<target+3 && !v.paused)break;await wait(90)}
   const a=v.currentTime,frames=v.getVideoPlaybackQuality().totalVideoFrames;
   await wait(950);measures.push({target,from:a,to:v.currentTime,frames:v.getVideoPlaybackQuality().totalVideoFrames-frames,
   width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null});v.pause()}
   return {fragment:requested,duration:v.duration,measures}})()""")
   assert 76.6<=evidence['fragment']<78 and 1929<evidence['duration']<1930
   for m in evidence['measures']:assert m['width']==1920 and m['height']==1080 and m['frames']>0 and m['to']-m['from']>.1 and abs(m['from']-m['target'])<2 and not m['error'],m
   write(W/'final-qa/browser-playback.json',dict(url=url,httpRange=206,isolatedBrowser=exe.name,**evidence));ws.close()
  finally:
   proc.terminate();proc.wait(timeout=15)
if __name__=='__main__':run()
