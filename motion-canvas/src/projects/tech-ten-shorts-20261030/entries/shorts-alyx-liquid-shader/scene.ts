import timing from '../../../../../../projects/shorts-alyx-liquid-shader/production/visual-timing.json';
import config from '../../../../../../projects/shorts-alyx-liquid-shader/production/visual-config.json';
import {createTechScene} from '../../scene-factory';
import type {Timing, Config} from '../../model';
export default createTechScene(timing as Timing, config as unknown as Config);
