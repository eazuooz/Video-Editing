"""Capture the newly located installed guard animation after the current CPU queue."""
import time
from prepare import WORK,read,save
from run_selected_queue import run


def main():
    deadline=time.monotonic()+1800
    flag=WORK/'selected-input-status.json'
    while time.monotonic()<deadline:
        if flag.exists() and read(flag).get('stage')=='native-hands-and-sentence-readback-ready':break
        time.sleep(3)
    else:raise TimeoutError('Wait for this selected input queue; do not overlap costly jobs.')
    run('prepare_native.py','--only','A_Guard_idle')
    run('capture_native.py','A_Guard_idle')
    save(WORK/'guard-input-status.json',{'stage':'native-guard-captured-audition-pending','humanReviewed':False})
    print('Installed guard animation and matching native prop captured for inspection.',flush=True)


if __name__=='__main__':main()
