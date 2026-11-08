from pathlib import Path
import shutil,subprocess,sys,datetime
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';B=L/('before-scene15-repair-'+datetime.datetime.now().strftime('%H%M%S'));B.mkdir(exist_ok=True)
for f in [L/'narration/ai-2d-game-assets.wav',L/'narration/ai-2d-game-assets.timing.json',L/'narration/ai-2d-game-assets.srt',L/'timeline.json']:
 shutil.copy2(f,B/f.name)
for f in [P/'production/audio-qa.json',L/'narration-aligned.wav',L/'final-mix.wav',L/'final-mix.m4a',L/'qa/narration.txt',L/'qa/narration.timestamps.json',L/'qa/mix.txt',L/'qa/mix.timestamps.json']:
 assert f.resolve().is_relative_to(P.resolve())
 shutil.move(f,B/f.name)
print('Preserved prior current files; regenerate only paragraph15',flush=True)
result=subprocess.run([sys.executable,'-X','utf8','-u',str(P/'production/run_tts.py'),'--force-scenes','15'],cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
print(result.stdout,result.stderr,flush=True);result.check_returncode()
result=subprocess.run([str(R/'qwen3-tts/.venv/Scripts/python.exe'),'-X','utf8','-u',str(P/'production/run_final_qa.py')],cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
print(result.stdout,result.stderr,flush=True);result.check_returncode()
