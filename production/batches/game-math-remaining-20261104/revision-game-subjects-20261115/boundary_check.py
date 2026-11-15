"""Inspect exact encoded cut frames using both random and integer-prefix decode."""
from subject_revision import *
def main():
    e=EPISODES['M26'];movie=read(work(e)/'encoded.json')['files']['captioned']['path'];out=HERE/'local/boundary-check';out.mkdir(exist_ok=True)
    for name,start,filter0 in [('random',150.4,None),('integer-prefix',148,'select=eq(n\\,144)'),('following',148,'select=eq(n\\,145)')]:
        target=out/(name+'.png')
        if target.exists():continue
        command=[str(FF),'-v','error','-nostdin','-n','-threads','1','-ss',str(start),'-i',movie]
        if filter0:command+=['-vf',filter0]
        subprocess.run(command+['-frames:v','1','-threads','1',str(target)],check=True,creationflags=prior.CREATE)
if __name__=='__main__':main()
