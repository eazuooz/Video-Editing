import timing from '../../../../../../projects/shorts-uncharted3-fixed-plane-scrolling-desert/production/visual-timing.json';
import config from '../../../../../../projects/shorts-uncharted3-fixed-plane-scrolling-desert/production/visual-config.json';
import {createTechScene} from '../../scene-factory';
import type {Timing, Config} from '../../model';
export default createTechScene(timing as Timing, config as unknown as Config);
