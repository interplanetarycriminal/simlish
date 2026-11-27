# jsfxr

Use for generating retro 8-bit game sound effects from presets or saved parameters, in the browser, in Node, or as WAV files from the command line.

> #54 · Game development · Source E (games) · smoke test: **passed**

## Evidence and maintenance

- [Canonical reference](https://github.com/chr15m/jsfxr)
- Verified 2026-11-27 against default branch `master` at [`b7b6aa27d62f`](https://github.com/chr15m/jsfxr/commit/b7b6aa27d62f8f356db267276bf54b451555c49d).
- GitHub reports archive state **false** and a repository push at `2026-05-05T09:58:09Z`. Push activity is a maintenance signal, not a quality rating.
- Attribution: Listed in the game-development post (source E, transcript supplied by the user on 2026-11-27).

- [README.md](https://github.com/chr15m/jsfxr/blob/b7b6aa27d62f8f356db267276bf54b451555c49d/README.md)
- [package.json](https://github.com/chr15m/jsfxr/blob/b7b6aa27d62f8f356db267276bf54b451555c49d/package.json)
- [sfxr-to-wav](https://github.com/chr15m/jsfxr/blob/b7b6aa27d62f8f356db267276bf54b451555c49d/sfxr-to-wav)
- [sfxr.js](https://github.com/chr15m/jsfxr/blob/b7b6aa27d62f8f356db267276bf54b451555c49d/sfxr.js)

## Runtime, hardware and setup

- **Type** library. Primary language JavaScript.
- **Platforms** Unverified.
- **Runtime** JavaScript in the browser or Node (CommonJS and ES module builds). No runtime dependencies. Package version 1.4.0.
- **Execution** local.
- **Agent paths** Generic coding agent via project files. Client claims describe documentation and remain untested here unless the smoke test says otherwise.
- **Configuration** Pick a preset (pickupCoin, laserShoot, explosion, powerUp, hitHurt, jump, blipSelect, synth, tone, click, random) or pass a serialized JSON or base58 sound definition from sfxr.me; defaults are 44100 Hz, 8-bit, volume 0.25.
- **Credentials and services** None. Jsfxr Pro at pro.sfxr.me is a separate hosted product.

Review the source and pin the version before running the upstream-documented command. It was read in the pinned documentation; execution is recorded only under Smoke test.

```sh
npm i jsfxr
```

## Contracts and selection

| Boundary | Contract |
| --- | --- |
| Input | preset name, sfxr JSON parameter object, base58 short-URL sound definition from sfxr.me |
| Output | Web Audio playback (sfxr.play, toAudio, toWebAudio), sample buffer array (toBuffer), WAV as a data URI (toWave(...).dataURI), WAV file via the sfxr-to-wav CLI |
| Primary | Game audio |
| Supporting | Prototyping |

Skip when you need music, voice or realistic recorded effects; jsfxr only synthesizes simple retro sfxr-style sounds. Consider the existing project toolchain. Complementary tools include [howler](howler.md), [phaser](phaser.md), [pixelfx](pixelfx.md), [godot](godot.md), [pixelorama](pixelorama.md).

## Craft notes

- One call makes a sound: sfxr.generate('pickupCoin') then sfxr.play(sound), and the same definition can be shared as a compact base58 string.
- In Node, sfxr.toWave(sound).dataURI gives a WAV data URI, and the bundled sfxr-to-wav CLI writes a .wav from a base58 definition or JSON piped on stdin.
- The CLI reads stdin from /dev/stdin and uses the deprecated new Buffer(), so piping JSON may not work on Windows; passing the base58 string as an argument avoids stdin.

## Examples

1. **Independent** Generate 20 random laserShoot variations in Node and save each as a WAV file with sfxr-to-wav.
2. **Combined** Proposed handoff: render jsfxr hit and coin sounds to WAV and play them with howler in a Phaser game.

For both, save the inputs and output evidence with the selected version. Use a small authorized fixture first and review the actual render or inspection result before expanding scope.

## Smoke test

**passed**. fixtures/game-dev jsfxr-sfx: jsfxr 1.4.1 renders jump and coin presets to 44.1 kHz mono 16-bit WAV (0.312 s and 0.274 s, checked with ffprobe), byte-identical from a fixed seed.

## Security, privacy and licensing

- The browser snippet loads scripts from sfxr.me; bundle the npm package instead to avoid a third-party script.
- Runs locally; no network calls in the library.

**Software license** Unlicense (public domain dedication).

**Commercial use** Unlicense: public-domain dedication, so commercial use is allowed with no conditions. Generated sounds carry no license terms in the pinned files.

## Evidence quotes

| Field | Upstream wording and file |
| --- | --- |
| hardware | No hardware section; pure JavaScript library (package.json has no dependencies). |
| installation | 'Install it: `npm i jsfxr`' (README.md) |
| license | Repository licence file UNLICENSE; GitHub SPDX 'Unlicense' (meta.tsv, package.json files list) |
| model_license | Not a model tool. |
| inputs | 'Click the "serialize" button and copy the JSON code for the sound you want.' (README.md) |
| outputs | 'Additionally you can get a dataURI for a wav file of the sound' (README.md) |
| cli | 'Usage: ./sfxr-to-wav SYNTH-DEFINITION [FILENAME.wav]' (sfxr-to-wav) |
