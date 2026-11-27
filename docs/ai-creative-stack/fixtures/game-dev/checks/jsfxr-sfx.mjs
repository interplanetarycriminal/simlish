// jsfxr: render a jump and a coin preset to WAV, then verify with ffprobe and a decoded RMS.
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { sfxr } from 'jsfxr';
import { ROOT, version } from './versions.mjs';

// jsfxr presets draw from Math.random. Swap in a seeded generator so the WAVs are the same on every run.
function seeded(seed) {
  let s = seed >>> 0;
  return () => { s = (s + 0x6d2b79f5) >>> 0; let x = s; x = Math.imul(x ^ (x >>> 15), x | 1); x ^= x + Math.imul(x ^ (x >>> 7), x | 61); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
}
function render(preset, seed) {
  const original = Math.random;
  Math.random = seeded(seed);
  try {
    const params = sfxr.generate(preset, { sample_rate: 44100, sample_size: 16 });
    return Buffer.from(sfxr.toWave(params).wav);
  } finally { Math.random = original; }
}
function probe(file) {
  const info = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', file], { encoding: 'utf8' }));
  const s = info.streams[0];
  const pcm = execFileSync('ffmpeg', ['-v', 'error', '-i', file, '-f', 's16le', '-ac', '1', '-'], { maxBuffer: 64 << 20 });
  let sum = 0; let peak = 0; let clipped = 0;
  const n = pcm.length / 2;
  for (let i = 0; i < n; i++) { const v = pcm.readInt16LE(i * 2) / 32768; sum += v * v; peak = Math.max(peak, Math.abs(v)); if (Math.abs(v) >= 0.999) clipped++; }
  return { format: info.format.format_name, codec: s.codec_name, sampleRate: Number(s.sample_rate), channels: s.channels, duration: Number(info.format.duration), samples: n, rmsDbfs: 20 * Math.log10(Math.sqrt(sum / n) || 1e-12), peak, clippedSamples: clipped };
}

export default async function run() {
  const sounds = {};
  for (const [name, preset, seed] of [['jump', 'jump', 7], ['coin', 'pickupCoin', 11]]) {
    const file = join(ROOT, 'out', `${name}.wav`);
    writeFileSync(file, render(preset, seed));
    const again = render(preset, seed);
    const p = probe(file);
    p.ok = p.format === 'wav' && p.codec === 'pcm_s16le' && p.sampleRate === 44100 && p.channels === 1 && p.duration > 0.05 && p.duration < 5 && p.rmsDbfs > -40 && p.peak > 0.05;
    p.reproducible = again.equals(readFileSync(file));
    sounds[name] = { preset, seed, file: `out/${name}.wav`, ...p };
  }
  const distinct = Math.abs(sounds.jump.duration - sounds.coin.duration) > 1e-6 || Math.abs(sounds.jump.rmsDbfs - sounds.coin.rmsDbfs) > 0.01;
  return { pass: sounds.jump.ok && sounds.coin.ok && sounds.jump.reproducible && sounds.coin.reproducible && distinct, details: { jsfxr: version('jsfxr'), sounds, distinct } };
}
