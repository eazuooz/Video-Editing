import timing from '../../../../../projects/shorts-gears-inertialization/production/visual-timing.json';
import native from '../../../../../projects/shorts-gears-inertialization/production/local/capture-full-v1/readback.json';
import {composite} from '../composite';
export default composite('gears','shorts-gears-inertialization',timing,native);
