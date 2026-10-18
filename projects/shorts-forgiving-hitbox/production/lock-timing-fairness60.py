"""Lock inspected quiet edits and voice-led visual sections without retiming speech."""
from pathlib import Path
import json,hashlib,math,soundfile as sf
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local/fairness-60s'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def q(t):return math.ceil((t-1e-8)*60)/60
def main():
 assert not (L/'narration-timeline.wav').exists(),'Do not change completed PCM timing'
 inspect=read(L/'additions-timing-inspection.json');approval=read(L/'inspected-cuts.json');assert approval['sourceSha256']==inspect['sourceSha256'] and approval['waveformReviewed']
 cuts=approval['cuts'];assert len(cuts)==3 and all(a<b for a,b in zip(cuts,cuts[1:]));end=approval.get('sourceEnd',inspect['seconds'])
 v1=R/'shared/output/narration/shorts-forgiving-hitbox/hitbox-v1/hitbox-v1.wav';v2=R/'shared/output/narration/shorts-forgiving-hitbox/hitbox-v2/hitbox-v2.wav';new=R/inspect['source'];numbers=R/'shared/output/narration/shorts-forgiving-hitbox/fairness60-code-numbers-v1/fairness60-code-numbers-v1.wav';ni=sf.info(numbers);parts=[]
 def part(id,src,a,b,d,lines):
  row=dict(id=id,source=src.relative_to(R).as_posix(),sourceSha256=sha(src),sourceRange=[a,b],dest=q(d),destinationEnd=q(d)+b-a,lineIndices=lines,rate=1,gain=1,speechFades=False);parts.append(row);return row
 A=part('approved-hook',v1,0,2.23,.2,[0]);X=part('new-viewpoints',new,0,cuts[0],3,[1,2,3]);B=part('approved-definitions',v2,2.95,9.21,X['destinationEnd']+.16,[4,5]);F=part('new-celeste-fact',new,cuts[0],cuts[1],B['destinationEnd']+.16,[6]);G=part('new-code-numbers',numbers,0,ni.frames/ni.samplerate,F['destinationEnd']+.16,[7]);game=q(F['dest']-.10);compare=q(G['destinationEnd']+.16);I=part('approved-comparison-intro',v2,9.21,11.16,compare,[8]);C=part('approved-comparison',v2,11.16,17.9,I['destinationEnd']+.50,[9,10]);Y=part('new-limit',new,cuts[1],cuts[2],C['destinationEnd']+.20,[11,12]);Z=part('new-small-margin',new,cuts[2],end,Y['destinationEnd']+.20,[13]);D=part('approved-resolution',v2,17.9,22.56,max(55,Z['destinationEnd']+.22),[14]);assert D['destinationEnd']<=59.85,('Content exceeds60s; revise complete wording or useful observation holds, never stretch speech',D['destinationEnd'])
 save(L/'pcm-edit.json',dict(seconds=60,parts=parts,reason='Reuse approved PCM with changed additions inserted at inspected quiet boundaries; no speech retiming, no fades into speech.',humanListening='pending',quietBoundaryEvidence='inspected-cuts.json'))
 xlines=inspect['lines'];survivor=q(X['dest']+xlines[0]['start']+(xlines[0]['end']-xlines[0]['start'])*.5);reveal=q(X['dest']+xlines[2]['start']);wide=q(C['dest']-.45);narrow=q(C['dest']+1.4);limit=q(Y['dest']-.1);code=G['dest'];gameSplit=93+code-game;returngame=q(D['dest']-(103.5-gameSplit))
 def s(id,kind,a,b,ss,se,rate=None):
  r=dict(id=id,kind=kind,start=a,end=b,sourceStart=ss,sourceEnd=se)
  if rate is not None:r['rate']=rate
  return r
 rows=[s('hook','unity',0,3,.05,1.85,.6),s('attacker','unity',3,survivor,.4,1.9,1.5/(survivor-3)),s('survivor','unity',survivor,reveal,.4,1.8,1.4/(reveal-survivor)),s('reveal','unity',reveal,B['dest'],4,4,0),s('terms','unity',B['dest'],game,5,10.9,1),s('celeste','game',game,code,93,gameSplit),s('code','game',code,compare,gameSplit,gameSplit),s('compare-intro','unity',compare,wide,12,12,0),s('wide','unity',wide,narrow,13.25,15.38,1),s('narrow','unity',narrow,limit,15.4,21.3,1),s('limit','unity',limit,returngame,4,4,0),s('return-game','game',returngame,D['dest'],gameSplit,103.5),s('resolution','unity',D['dest'],60,.4,1.9,1.5/(60-D['dest']))]
 assert all(s['end']>s['start'] for s in rows);assert all(abs(a['end']-b['start'])<1e-6 for a,b in zip(rows,rows[1:]));save(L/'visual-timing.json',dict(status='Locked from measured approved/additions PCM; no speech retiming',seconds=60,fps=60,revealStart=reveal,termsStart=B['dest'],sections=rows));print(json.dumps(dict(parts=parts,sections=rows),ensure_ascii=False))
if __name__=='__main__':main()
