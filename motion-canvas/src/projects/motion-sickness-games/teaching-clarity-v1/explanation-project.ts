import {makeProject} from '@motion-canvas/core';
import opening from './opening-explanation?scene';
import goalCues from './goal-cues-explanation?scene';
// Two independently editable additions; original12 scenes and membership render are untouched.
export default makeProject({scenes: [opening, goalCues]});
