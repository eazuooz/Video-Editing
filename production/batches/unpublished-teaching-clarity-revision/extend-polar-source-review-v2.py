"""Inspect previously unseen later action frames, preserving first pilot outputs."""
exec((__import__('pathlib').Path(__file__).with_name('prepare-polar-source-review-v1.py')).read_text(encoding='utf-8').split('OUT.mkdir')[0])
LOCAL.mkdir(parents=True,exist_ok=True)
clip=ROOT/'shared/output/game-math-polar-3d/clips/02.mp4'
frames=[780,900,1020,1140,1260,1380,1500,1620,1740,1860,1980,2086,2087,2147,2267,2387,2507,2627,2747,2867,2987,3107,3227,3347,3402]
records=[]
for frame in frames:
 target=LOCAL/f'scene02-f{frame:04d}.png'; assert not target.exists()
 subprocess.run([str(FF),'-hide_banner','-nostdin','-loglevel','error','-threads','2','-filter_threads','1','-i',str(clip),'-vf',f'select=eq(n\\,{frame})','-frames:v','1','-fps_mode','passthrough',str(target)],check=True)
 records.append({'frame':frame,'seconds':frame/60,'path':rel(target),'sha256':sha(target)})
boards=[]
for n in range(0,len(records),6):
 group=records[n:n+6];board=Image.new('RGB',(1920,780),'#181818');d=ImageDraw.Draw(board)
 for j,r in enumerate(group):
  x=(j%3)*640;y=(j//3)*390
  with Image.open(ROOT/r['path']) as im:board.paste(im.resize((640,360)),(x,y+30))
  d.text((x+8,y+7),f"scene02 f{r['frame']} / {r['seconds']:.3f}s",fill='white')
 path=LOCAL/f'later-source-board-{n//6+1:02d}.png';assert not path.exists();board.save(path);boards.append({'path':rel(path),'sha256':sha(path)})
write(OUT/'source-pilot-extraction-v2.json',{'records':records,'boards':boards,'ffmpegExitCodes':[0]*len(records),'scope':'scene02 remaining action and exact cut-adjacent converted frames','newNativePtsApproval':False,'allContinuousPixelsReviewed':False,'annotationApproved':False,'localOnly':True})
print(json.dumps({'samples':len(records),'boards':len(boards)}),flush=True)
