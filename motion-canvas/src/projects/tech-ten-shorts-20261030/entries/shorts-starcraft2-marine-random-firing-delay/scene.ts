import timing from '../../../../../../projects/shorts-starcraft2-marine-random-firing-delay/production/visual-timing.json';
import config from '../../../../../../projects/shorts-starcraft2-marine-random-firing-delay/production/visual-config.json';
import {createTechScene} from '../../scene-factory';
import type {Timing, Config} from '../../model';
export default createTechScene(timing as Timing, config as unknown as Config);
