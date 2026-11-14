"""Complete the final phrase/crop preflight after the selected guard capture."""
import time
from prepare import WORK,read,save
from run_selected_queue import run


def main():
    deadline=time.monotonic()+1800
    flag=WORK/'guard-input-status.json'
    while time.monotonic()<deadline:
        if flag.exists() and read(flag).get('stage')=='native-guard-captured-audition-pending':break
        time.sleep(3)
    else:raise TimeoutError('Guard capture pending. Preserve all other work.')
    run('render_recaps.py','--manifest','patches-manifest.json','--only-missing')
    run('check_narration_patches.py')
    run('preflight_visuals.py')
    save(WORK/'scene-input-status.json',{'stage':'all-native-inputs-preflight-prepared',
         'configurationReviewPending':True,'humanReviewed':False})
    print('All revised native comparisons and their actual-caption preflight are ready for inspection.',flush=True)


if __name__=='__main__':main()
