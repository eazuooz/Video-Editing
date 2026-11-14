"""Finish only newly identified wording corrections after the current body boundary."""
import argparse,ctypes,time
from run_selected_queue import run
from prepare import WORK,save

def main(wait_pid=None):
    kernel=ctypes.windll.kernel32
    kernel.OpenProcess.restype=ctypes.c_void_p
    handle=kernel.OpenProcess(0x100000,False,wait_pid) if wait_pid else None
    if handle:
        try:
            while kernel.WaitForSingleObject(ctypes.c_void_p(handle),0)==258:time.sleep(3)
        finally:kernel.CloseHandle(ctypes.c_void_p(handle))
    run('render_recaps.py','--manifest','patches-manifest.json','--only-missing')
    run('check_narration_patches.py')
    save(WORK/'wording-alignment-status.json',{'stage':'all-additional-wording-readbacks-passed','humanReviewed':False})
    print('All additional wording aligned and checked.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wait-pid',type=int)
    main(p.parse_args().wait_pid)
