import timing from '../../../../../../projects/shorts-batman-origins-snow-below-camera/production/visual-timing.json';
import config from '../../../../../../projects/shorts-batman-origins-snow-below-camera/production/visual-config.json';
import {createTechScene} from '../../scene-factory';
import type {Timing, Config} from '../../model';
export default createTechScene(timing as Timing, config as unknown as Config);
