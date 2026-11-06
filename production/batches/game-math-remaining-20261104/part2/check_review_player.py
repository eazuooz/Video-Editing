"""Exercise each published local player in a separate, temporary Chrome session."""
import json
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen
import websocket
from edition import BATCH
from status import store

HUB = "http://127.0.0.1:9347/output/game-math-remaining-20261104/index.html"
PLAY = """
async () => {
  const video = document.querySelector('video');
  if (!video) throw Error('Missing player');
  video.muted = true;
  if (video.readyState < 1) {
    await new Promise((resolve, reject) => {
      video.addEventListener('loadedmetadata', resolve, {once: true});
      video.addEventListener('error', reject, {once: true});
    });
  }
  video.currentTime = Math.floor(video.duration * 0.52);
  await video.play();
  const start = video.currentTime;
  const frames = video.getVideoPlaybackQuality().totalVideoFrames;
  await new Promise(resolve => setTimeout(resolve, 1150));
  video.pause();
  return {seconds: video.duration, advanced: video.currentTime - start,
          decoded: video.getVideoPlaybackQuality().totalVideoFrames - frames,
          size: [video.videoWidth, video.videoHeight],
          visibleWidth: video.getBoundingClientRect().width};
}
"""

def check():
    browser = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    results = []
    with tempfile.TemporaryDirectory(prefix="game-math-review-") as temp:
        proc = subprocess.Popen([str(browser), "--headless=new", "--no-first-run",
            "--disable-extensions", "--disable-sync", "--mute-audio", "--remote-debugging-port=0",
            "--user-data-dir="+temp, "about:blank"], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        portfile = Path(temp)/"DevToolsActivePort"
        try:
            for _ in range(100):
                if portfile.exists() and portfile.read_text().strip(): break
                time.sleep(.15)
            port = portfile.read_text().splitlines()[0]
            with urlopen(f"http://127.0.0.1:{port}/json/list",timeout=5) as response:
                page = next(i for i in json.load(response) if i["type"]=="page")
            socket = websocket.create_connection(page["webSocketDebuggerUrl"],timeout=25,suppress_origin=True)
            counter=0
            def send(method, params):
                nonlocal counter
                counter+=1
                socket.send(json.dumps(dict(id=counter,method=method,params=params)))
                while True:
                    event=json.loads(socket.recv())
                    if event.get("id")==counter:
                        if "error" in event: raise RuntimeError(event["error"])
                        return event["result"]
            def evaluate(expression):
                result=send("Runtime.evaluate",dict(expression=expression,awaitPromise=True,returnByValue=True))
                if "exceptionDetails" in result: raise RuntimeError(result["exceptionDetails"])
                return result["result"].get("value")
            def navigate(url):
                send("Page.navigate",{"url":url})
                for _ in range(100):
                    if evaluate("document.readyState !== 'loading' && location.href === "+json.dumps(url)): return
                    time.sleep(.1)
                raise RuntimeError("Page load timed out: "+url)
            send("Emulation.setDeviceMetricsOverride",dict(width=375,height=812,deviceScaleFactor=1,mobile=True))
            navigate(HUB)
            rows=evaluate("[...document.querySelectorAll('tbody tr')].map(tr => ({episode:tr.cells[0].textContent, url:tr.querySelector('a')?.href}))")
            assert len(rows)==13 and all(r["url"] for r in rows),rows
            for row in rows:
                navigate(row["url"])
                result=evaluate("("+PLAY+")()")
                assert result["decoded"]>0 and result["advanced"]>.3 and result["size"]==[1920,1080], (row,result)
                assert 150<result["visibleWidth"]<=375,(row,result)
                results.append({**row,**result})
            send("Browser.close",{})
            socket.close()
        finally:
            if proc.poll() is None:
                try: proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    proc.wait(timeout=8)
    store(BATCH/"local/part2-20261106/browser-review.json",results)
    return results

if __name__=="__main__":
    print(json.dumps(check(),ensure_ascii=False,indent=2))
