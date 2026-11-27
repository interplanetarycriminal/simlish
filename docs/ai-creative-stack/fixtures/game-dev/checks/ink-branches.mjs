// inkjs: compile an original .ink story, walk every choice path, check endings, variables and save/restore.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { Compiler, Story } from 'inkjs/full';
import { ROOT, version } from './versions.mjs';

const EXPECTED_ENDINGS = ['beacon', 'home', 'map'];

function drain(story) {
  let text = '';
  while (story.canContinue) text += story.Continue();
  return text;
}

// Depth-first walk. Each branch restores the saved JSON state, so this also exercises save/load many times.
function walk(json) {
  const story = new Story(json);
  const paths = [];
  const visit = (saved, trail) => {
    story.state.LoadJson(saved);
    const text = drain(story);
    if (story.currentChoices.length === 0) {
      paths.push({ trail, ending: story.variablesState.ending, courage: story.variablesState.courage, coins: story.variablesState.coins, lastLine: text.trim().split('\n').pop() });
      return;
    }
    const here = story.state.ToJson();
    const labels = story.currentChoices.map((c) => c.text);
    labels.forEach((label, i) => {
      story.state.LoadJson(here);
      story.ChooseChoiceIndex(i);
      visit(story.state.ToJson(), [...trail, label]);
    });
  };
  visit(story.state.ToJson(), []);
  return paths;
}

export default async function run() {
  const source = readFileSync(join(ROOT, 'story', 'lantern.ink'), 'utf8');
  const compiler = new Compiler(source);
  const story0 = compiler.Compile();
  const errors = compiler.errors || [];
  const json = story0.ToJson();
  writeFileSync(join(ROOT, 'out', 'lantern.ink.json'), json);

  const paths = walk(json);
  const endings = [...new Set(paths.map((p) => p.ending))].sort();
  const allReachable = JSON.stringify(endings) === JSON.stringify(EXPECTED_ENDINGS);
  const everyPathEnds = paths.every((p) => p.ending !== '' && /THE END/.test(p.lastLine));

  // Variables: the beacon path climbs twice (courage 2); the coin path that buys the box ends with 2 coins.
  const beacon = paths.find((p) => p.ending === 'beacon');
  const mapEnd = paths.find((p) => p.ending === 'map');
  const variablesUpdate = beacon?.courage === 2 && mapEnd?.coins === 2 && /courage 2/.test(beacon.lastLine) && /2 coins/.test(mapEnd.lastLine);
  // The guarded choice must be hidden when coins < 3 (stairs -> back down -> pools has 0 coins).
  const guarded = paths.filter((p) => p.trail[0] === 'Climb the lighthouse stairs' && p.trail[1] === 'Go back down');
  const conditionalChoiceHidden = guarded.length === 1 && guarded[0].ending === 'home';

  // Save mid-story, finish one way, then restore into a new Story and finish the same way: identical output.
  const live = new Story(json);
  drain(live); live.ChooseChoiceIndex(1); drain(live); // took the rock pools; now at the crab
  const saved = live.state.ToJson();
  live.ChooseChoiceIndex(0); const tailA = drain(live);
  const resumed = new Story(json);
  resumed.state.LoadJson(saved);
  const choicesAfterLoad = resumed.currentChoices.map((c) => c.text);
  resumed.ChooseChoiceIndex(0); const tailB = drain(resumed);
  const saveRestore = tailA === tailB && resumed.variablesState.ending === 'map' && resumed.variablesState.coins === 2 && choicesAfterLoad[0] === 'Trade a coin for the box';

  return {
    pass: errors.length === 0 && allReachable && everyPathEnds && variablesUpdate && conditionalChoiceHidden && saveRestore,
    details: { inkjs: version('inkjs'), compileErrors: errors.length, paths: paths.map((p) => ({ trail: p.trail.join(' > '), ending: p.ending, courage: p.courage, coins: p.coins })), endings, allReachable, everyPathEnds, variablesUpdate, conditionalChoiceHidden, saveRestore, choicesAfterLoad },
  };
}
