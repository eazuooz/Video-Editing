"""Record an explicit inspection of the current final encoded images."""
import argparse
from prepare import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('episode');ap.add_argument('notes');ap.add_argument('--full',action='store_true');ap.add_argument('--mobile',action='store_true');a=ap.parse_args()
 f=HERE/'visual-review.json';j=read(f);d=read(HERE/'deliveries'/(a.episode+'.json'))
 row=dict(id=a.episode,masterSha256=d['files']['captioned']['sha256'],review=a.notes,actualEncodedTemporalSamples=True,fullResolution=a.full,fullResolutionAndMobile=a.full and a.mobile,passed=True,humanReviewed=False)
 j['episodes']=[r for r in j['episodes'] if r['id']!=a.episode]+[row];j['episodes'].sort(key=lambda r:r['id']);j['allFinalEncodedSamplesReviewed']=len(j['episodes'])==13
 save(f,j);print('Recorded current encoded-image inspection:',a.episode)
if __name__=='__main__':main()
