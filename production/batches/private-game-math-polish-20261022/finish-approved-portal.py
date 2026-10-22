"""Finite serialized completion of the five explicitly authorized restorations.

Produces masters and technical evidence only. Direct final visual review is
still required; this worker cannot mark a video ready or publish anything.
"""
import datetime, sys, traceback
from polish_common import *

ids = sys.argv[1:]
assert ids and len(ids) == len(set(ids))
assert set(ids) <= {'M09', 'M10', 'M11', 'M12', 'M17'}
state_path = B / 'approved-portal-finish-job.json'
state = {'pid': os.getpid(), 'ids': ids, 'status': 'running', 'results': {},
         'newTts': False, 'platformMutation': False, 'humanReview': 'pending'}

def checkpoint(episode, stage):
    state.update(episode=episode, stage=stage,
                 updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(state_path, state)
    print(episode, stage, flush=True)

for ident in ids:
    e = Episode(ident)
    try:
        for script in ['prepare-observed-composition.py',
                       'register-reviewed-geometry-inputs.py', 'assemble.py',
                       'technical-qa.py', 'review-final-pixels.py']:
            e.authorized()
            checkpoint(ident, script)
            e.run([sys.executable, B / script, ident],
                  'approved-portal-' + script.replace('.py', '') + '.log')
        state['results'][ident] = {'status': 'technical-complete-await-direct-final-review',
                                  'outputs': rel(e.H / 'outputs.json'),
                                  'technicalQa': rel(e.H / 'technical-qa.json'),
                                  'finalPixelSamples': rel(e.H / 'final-pixel-samples.json')}
    except Exception as error:
        state['results'][ident] = {'status': 'failed', 'error': str(error),
                                  'traceback': traceback.format_exc()}
    checkpoint(ident, state['results'][ident]['status'])
state['status'] = 'finished-with-failures' if any(x['status'] == 'failed' for x in state['results'].values()) else 'finished-await-direct-final-review'
checkpoint(None, state['status'])
