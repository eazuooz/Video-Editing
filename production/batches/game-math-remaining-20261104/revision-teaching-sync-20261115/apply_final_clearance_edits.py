"""Apply only the encoded-review clearance fixes once the active job ends."""
import subprocess
import sys
from inventory import ROOT,HERE,read,save
from render_revision import guard


def main():
    assert read(HERE/'finite-worker.json')['status']=='finite-job-ended-review-pending'
    assert not guard().idle_reason(), 'Preserve active work'
    path=HERE/'game-additions.json';d=read(path)
    for g in d['additions']:
        if (g['episode'],g['scene']) in {('M29','018'),('M30','003')}:
            g['nativeClearBottom']=180
            g['nativeFooterReason']='Full encoded review: remove the entire clipped auxiliary footer, keep balls/normal or rigid-body points.'
    save(path,d)
    path=HERE/'game_plan.py';s=path.read_text(encoding='utf8')
    s=s.replace("additions[-1]['nativeClearBottom']=140", "additions[-1]['nativeClearBottom']=180")
    path.write_text(s,encoding='utf8')
    path=HERE/'motion_panels.py';s=path.read_text(encoding='utf8')
    s=s.replace('b.rectangle(56,178,886,738,a,z)', 'b.rectangle(56,160,940,756,a,z)')
    if 'def hermite_endpoint_labels' not in s:
        function="""def hermite_endpoint_labels(b,s):
    # The new math gutter covers the native outside labels. Keep identities
    # next to the exact unchanged endpoint and its downward tangent instead.
    a,z=s['start'],s['end']
    b.rectangle(930,790,65,70,a,z)
    b.text(933,795,"p₁",a,z,GOLD,44)
    b.text(920,490,"v₁",a,z,TEAL,44)


"""
        s=s.replace('def apply(board,episode,games):',function+'def apply(board,episode,games):')
        s=s.replace('    if episode["id"]=="M30":carriage_displacements(board,lookup["053"])', '    if episode["id"]=="M30":carriage_displacements(board,lookup["053"])\n    if episode["id"]=="M31":hermite_endpoint_labels(board,lookup["032"])')
    path.write_text(s,encoding='utf8')
    for name in ('validate.py','math_checks.py'):
        subprocess.run([sys.executable,'-X','utf8',str(HERE/name)],cwd=ROOT,check=True)
    print('Only the four recorded clearance corrections are prepared; final encoded inspection remains pending.')


if __name__=='__main__':main()
