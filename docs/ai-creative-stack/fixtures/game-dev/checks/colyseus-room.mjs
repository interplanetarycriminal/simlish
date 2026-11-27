// Colyseus server-authoritative room on loopback: two clients, input intents, a rejected teleport, a reconnect.
import { createServer } from 'node:net';
import { Room, Server } from '@colyseus/core';
import { WebSocketTransport } from '@colyseus/ws-transport';
import { MapSchema, schema, t } from '@colyseus/schema';
import { Client } from '@colyseus/sdk';
import { version } from './versions.mjs';

const SPEED = 2; // units per accepted step intent
const Player = schema({ x: t.number(), y: t.number(), rejected: t.uint16() }, 'Player');
const Arena = schema({ tick: t.uint32(), players: t.map(Player) }, 'Arena');

class ArenaRoom extends Room {
  maxClients = 2;
  onCreate() {
    this.setState(new Arena());
    this.state.players = new MapSchema();
    this.state.tick = 0;
    this.setPatchRate(20);
    // Clients only send intents. The server owns positions and validates every message.
    this.onMessage('input', (client, msg) => {
      const p = this.state.players.get(client.sessionId);
      if (!p) return;
      const dx = Math.sign(Number(msg?.dx) || 0);
      const dy = Math.sign(Number(msg?.dy) || 0);
      if (Object.keys(msg || {}).some((k) => k !== 'dx' && k !== 'dy')) { p.rejected++; client.send('rejected', { reason: 'unknown field' }); return; }
      p.x += dx * SPEED; p.y += dy * SPEED; this.state.tick++;
    });
  }
  onJoin(client, options) {
    const p = new Player();
    p.x = options?.spawn ?? 0; p.y = 0; p.rejected = 0;
    this.state.players.set(client.sessionId, p);
  }
  async onDrop(client) { await this.allowReconnection(client, 10); }
  onLeave(client) { this.state.players.delete(client.sessionId); }
}

function freePort() {
  return new Promise((ok, fail) => {
    const s = createServer();
    s.once('error', fail);
    s.listen(0, '127.0.0.1', () => { const { port } = s.address(); s.close(() => ok(port)); });
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, ms = 3000) {
  const end = Date.now() + ms;
  while (Date.now() < end) { if (fn()) return true; await sleep(20); }
  return false;
}
const snapshot = (state) => {
  const out = {};
  state.players.forEach((p, id) => { out[id] = { x: p.x, y: p.y, rejected: p.rejected }; });
  return { tick: state.tick, players: out };
};

export default async function run() {
  const port = await freePort();
  const transport = new WebSocketTransport();
  const server = new Server({ transport, greet: false, gracefullyShutdown: false });
  server.define('arena', ArenaRoom);
  await server.listen(port, '127.0.0.1');
  const details = { colyseusCore: version('@colyseus/core'), colyseusSdk: version('@colyseus/sdk'), schema: version('@colyseus/schema'), host: '127.0.0.1', port, boundAddress: transport.server?.address()?.address };
  if (details.boundAddress !== '127.0.0.1') { await server.gracefullyShutdown(false).catch(() => {}); return { pass: false, details: { ...details, error: 'server is not bound to loopback only' } }; }
  try {
    const endpoint = `http://127.0.0.1:${port}`;
    const a = await new Client(endpoint).joinOrCreate('arena', { spawn: 0 });
    const b = await new Client(endpoint).joinOrCreate('arena', { spawn: 10 });
    details.sameRoom = a.roomId === b.roomId;
    for (const r of [a, b]) r.reconnection.enabled = false; // we test the explicit reconnect path below

    // 3 right steps from A, 2 down steps from B.
    for (let i = 0; i < 3; i++) a.send('input', { dx: 1, dy: 0 });
    for (let i = 0; i < 2; i++) b.send('input', { dx: 0, dy: 1 });
    // A client tries to write a position directly. The server must ignore it.
    let rejectedMsg = null;
    a.onMessage('rejected', (m) => { rejectedMsg = m; });
    a.send('input', { dx: 0, dy: 0, x: 9999 });
    // A large dx is clamped to one step by the server.
    b.send('input', { dx: 500, dy: 0 });

    const want = (s) => s.tick === 6 && s.players[a.sessionId]?.x === 6 && s.players[b.sessionId]?.y === 4 && s.players[b.sessionId]?.x === 12 && s.players[a.sessionId]?.rejected === 1;
    await until(() => want(snapshot(a.state)) && want(snapshot(b.state)) && rejectedMsg);
    const sa = snapshot(a.state); const sb = snapshot(b.state);
    details.clientA = sa; details.clientB = sb;
    details.bothSeeSameState = JSON.stringify(sa) === JSON.stringify(sb);
    details.authoritativeMath = want(sa);
    details.teleportRejected = sa.players[a.sessionId].x === 6 && rejectedMsg?.reason === 'unknown field';
    details.speedClamped = sa.players[b.sessionId].x === 12;

    // Reconnect: B drops without consent, then rejoins with its token and keeps its seat and position.
    const token = b.reconnectionToken; const oldId = b.sessionId;
    await b.leave(false);
    await sleep(150);
    const b2 = await new Client(endpoint).reconnect(token);
    b2.reconnection.enabled = false;
    b2.send('input', { dx: 1, dy: 0 });
    await until(() => b2.state?.players?.get(oldId)?.x === 14 && a.state.players.get(oldId)?.x === 14);
    details.reconnect = { sameSession: b2.sessionId === oldId, positionKept: b2.state.players.get(oldId)?.x === 14, otherClientSaw: a.state.players.get(oldId)?.x === 14 };

    await a.leave(true); await b2.leave(true);
    const pass = details.sameRoom && details.bothSeeSameState && details.authoritativeMath && details.teleportRejected && details.speedClamped
      && details.reconnect.sameSession && details.reconnect.positionKept && details.reconnect.otherClientSaw;
    return { pass, details };
  } finally {
    await server.gracefullyShutdown(false).catch(() => {});
    details.shutdown = true;
  }
}
