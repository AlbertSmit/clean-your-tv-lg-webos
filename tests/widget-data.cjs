const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const acorn = require('acorn');

const source = fs.readFileSync(path.join(__dirname, '../launcher/widget-data.js'), 'utf8');
acorn.parse(source, {ecmaVersion: 5});

function client(options = {}) {
  const requests = [];
  const sockets = [];
  const timers = new Map();
  let timerId = 0;
  let config = {ha: {url: 'https://ha.example.test', token: 'test-only', ...options.ha}};
  const context = vm.createContext({
    window: {WidgetPreview: options.preview},
    setTimeout(fn, delay) {const id = ++timerId; timers.set(id, {fn, delay}); return id;},
    clearTimeout(id) {timers.delete(id);},
    WebSocket: function (url) {
      this.url = url;
      this.sent = [];
      this.send = value => {this.sent.push(JSON.parse(value));};
      this.close = () => {this.closed = true;};
      this.message = value => {if (this.onmessage) this.onmessage({data: JSON.stringify(value)});};
      sockets.push(this);
    },
    localStorage: {
      getItem() {return JSON.stringify(config);},
      setItem(key, value) {config = JSON.parse(value);}
    },
    document: {createElement() {
      let parsed;
      return {
        set href(value) {parsed = new URL(value, 'https://preview.example.test/');},
        get href() {return parsed.href;},
        get protocol() {return parsed.protocol;},
        get host() {return parsed.host;}
      };
    }},
    XMLHttpRequest: function () {
      this.headers = {};
      this.open = (method, url) => {this.method = method; this.url = url;};
      this.setRequestHeader = (key, value) => {this.headers[key] = value;};
      this.send = () => {requests.push(this);};
    },
    FileReader: function () {
      this.readAsDataURL = () => {
        if (options.readerFails) this.onerror();
        else {this.result = 'data:image/png;base64,TEST'; this.onload();}
      };
    }
  });
  vm.runInContext(source, context);
  let snapshot = 'pending';
  function refresh() {
    snapshot = 'pending';
    context.window.WidgetData.refresh(value => {snapshot = value && JSON.parse(JSON.stringify(value));});
  }
  function respond(value, status = 200) {
    const request = requests[requests.length - 1];
    request.status = status;
    request.response = typeof value === 'string' ? value : JSON.stringify(value);
    request.onload();
  }
  return {requests, sockets, timers, refresh, respond,
    watch(callback) {return context.window.WidgetData.watch(callback);},
    load() {return context.window.WidgetData.load();},
    get snapshot() {return snapshot;},
    save(value) {context.window.WidgetData.save(value);}
  };
}

function media(id, state = 'playing', attributes = {}) {
  return {entity_id: 'media_player.' + id, state, attributes: {
    media_content_type: 'music', media_title: 'Song', media_artist: 'Artist',
    media_album_name: 'Album', friendly_name: id, ...attributes
  }};
}

const auto = client();
auto.refresh();
auto.respond([
  null, {}, media('idle', 'idle'), media('video', 'playing', {media_content_type: 'video'}),
  media('kitchen'), media('bedroom'),
  {entity_id: 'weather.home', state: 'sunny', attributes: {temperature: 20, temperature_unit: '°C'}}
]);
assert.deepEqual(auto.snapshot.nowPlaying, {
  playing: true, title: 'Song', artist: 'Artist', album: 'Album', source: 'kitchen', artwork: null
});
assert.equal(auto.snapshot.weather.temp, 20, 'music filtering must preserve weather');

for (const entity of [
  media('idle', 'idle'), media('paused', 'paused'), media('off', 'off'),
  media('unknown', 'unknown'), media('video', 'playing', {media_content_type: 'video'}),
  media('tv', 'playing', {media_content_type: 'tvshow'}),
  media('unknown-type', 'playing', {media_content_type: undefined}),
  media('empty-title', 'playing', {media_title: '  '}),
  media('missing-title', 'playing', {media_title: undefined}),
  {...media('wrong-domain'), entity_id: 'sensor.music'}
]) {
  auto.refresh();
  auto.respond([entity]);
  assert.equal(auto.snapshot.nowPlaying, null, entity.entity_id + ' must not show Now Playing');
}

const explicit = client({ha: {mediaEntity: 'media_player.bedroom'}});
explicit.refresh();
explicit.respond([media('kitchen'), media('bedroom')]);
assert.equal(explicit.snapshot.nowPlaying.source, 'bedroom');
for (const entities of [[media('kitchen')], [media('kitchen'), media('bedroom', 'paused')]]) {
  explicit.refresh();
  explicit.respond(entities);
  assert.equal(explicit.snapshot.nowPlaying, null, 'an explicit entity must never fall back to another room');
}

for (const picture of ['/api/image/1', 'api/image/1', 'https://ha.example.test/api/image/1']) {
  const artwork = client();
  artwork.refresh();
  artwork.respond([media('kitchen', 'playing', {entity_picture: picture})]);
  assert.equal(artwork.requests.length, 2, 'same-origin artwork must be requested');
  assert.equal(new URL(artwork.requests[1].url).origin, 'https://ha.example.test');
  assert(artwork.requests[1].headers.Authorization, 'same-origin artwork needs HA authorization');
  artwork.respond('image-bytes');
  assert.equal(artwork.snapshot.nowPlaying.artwork, 'data:image/png;base64,TEST');
}

for (const picture of [
  'https://external.example.test/cover.png', '//external.example.test/cover.png',
  'https://ha.example.test.external.example.test/cover.png',
  'https://ha.example.test@external.example.test/cover.png',
  'http://ha.example.test/cover.png', 'https://ha.example.test:8443/cover.png',
  'data:image/png;base64,TEST', 'javascript:alert(1)'
]) {
  const artwork = client();
  artwork.refresh();
  artwork.respond([media('kitchen', 'playing', {entity_picture: picture})]);
  assert.equal(artwork.requests.length, 1, 'external artwork must never receive an authenticated request');
  assert.equal(artwork.snapshot.nowPlaying.artwork, null);
}

for (const failure of ['status', 'error', 'timeout', 'reader']) {
  const artwork = client({readerFails: failure === 'reader'});
  artwork.refresh();
  artwork.respond([media('kitchen', 'playing', {entity_picture: '/api/image/1'})]);
  if (failure === 'error') artwork.requests[1].onerror();
  else if (failure === 'timeout') artwork.requests[1].ontimeout();
  else artwork.respond('image-bytes', failure === 'status' ? 403 : 200);
  assert.equal(artwork.snapshot.nowPlaying.artwork, null, 'failed artwork must not expose an authenticated URL');
}

for (const response of ['invalid json', '{}', 'null']) {
  auto.refresh();
  auto.respond(response);
  assert.equal(auto.snapshot, null, 'malformed state responses must clear stale data');
}
auto.refresh();
auto.requests[auto.requests.length - 1].ontimeout();
assert.equal(auto.snapshot, null, 'timeouts must clear stale data');
auto.refresh();
auto.requests[auto.requests.length - 1].onerror();
assert.equal(auto.snapshot, null, 'network failures must clear stale data');
const requestCount = auto.requests.length;
auto.save({ha: {url: '', token: ''}});
auto.refresh();
assert.equal(auto.snapshot, null, 'missing configuration must clear stale data');
assert.equal(auto.requests.length, requestCount, 'unconfigured HA must not issue requests');
console.log('PASS WidgetData HA music selection and authenticated artwork');

function handshake(socket) {
  socket.message({type: 'auth_required'});
  assert.equal(socket.sent[0].type, 'auth');
  assert(socket.sent[0].access_token, 'authentication must include the configured access token');
  socket.message({type: 'auth_ok'});
  assert.deepEqual(socket.sent[1], {id: 1, type: 'subscribe_events', event_type: 'state_changed'});
  assert.equal(socket.sent.length, 2, 'snapshot must wait until the subscription is established');
  socket.message({id: 1, type: 'result', success: true, result: null});
  assert.deepEqual(socket.sent[2], {id: 2, type: 'get_states'});
}

function stateChanged(socket, entity, id = entity.entity_id) {
  socket.message({id: 1, type: 'event', event: {event_type: 'state_changed',
    data: {entity_id: id, new_state: entity}}});
}

function states(socket, entities) {
  socket.message({id: 2, type: 'result', success: true, result: entities});
}

const streaming = client();
assert.equal(streaming.load().enabled.weather, false, 'new configurations must hide weather');
const streamConfig = streaming.load();
streamConfig.enabled.weather = true;
streaming.save(streamConfig);
const updates = [];
const stop = streaming.watch(value => {updates.push(value && JSON.parse(JSON.stringify(value)));});
const socket = streaming.sockets[0];
assert.equal(socket.url, 'wss://ha.example.test/api/websocket');
handshake(socket);
stateChanged(socket, media('kitchen', 'playing', {media_title: 'New Song'}));
states(socket, [media('kitchen', 'playing', {media_title: 'Old Song'})]);
assert.equal(updates.at(-1).nowPlaying.title, 'New Song', 'queued events must supersede the initial snapshot');
assert.equal(streaming.requests.length, 0, 'state streaming must not poll REST');
assert.deepEqual([...streaming.timers.values()].map(timer => timer.delay), [30000],
  'successful startup must replace its deadline with a heartbeat timer');
const beforeUnrelated = updates.length;
stateChanged(socket, {entity_id: 'sensor.temperature', state: '20'});
assert.equal(updates.length, beforeUnrelated, 'unrelated entities must not republish widgets');
stateChanged(socket, media('kitchen', 'paused'));
assert.equal(updates.at(-1).nowPlaying, null, 'pausing must hide music immediately');
stateChanged(socket, media('bedroom'));
assert.equal(updates.at(-1).nowPlaying.source, 'bedroom');
stateChanged(socket, null, 'media_player.bedroom');
assert.equal(updates.at(-1).nowPlaying, null, 'removed entities must disappear');
stateChanged(socket, {entity_id: 'weather.home', state: 'rainy', attributes: {temperature: 12}});
assert.equal(updates.at(-1).weather.temp, 12);

stateChanged(socket, media('bedroom', 'playing', {entity_picture: '/cover-old'}));
assert.equal(updates.at(-1).nowPlaying.artwork, null);
stateChanged(socket, media('bedroom', 'paused'));
streaming.respond('image-bytes');
assert.equal(updates.at(-1).nowPlaying, null, 'old artwork must not revive stopped music');
stateChanged(socket, media('bedroom', 'playing', {entity_picture: '/cover-stop'}));
const beforeStop = updates.length;
stop();
assert(socket.closed);
assert.equal(socket.onmessage, null);
assert.equal(socket.onclose, null);
assert.equal(streaming.timers.size, 0);
streaming.respond('image-bytes');
assert.equal(updates.length, beforeStop, 'stopped watchers must ignore late artwork');

const reconnecting = client();
const reconnectUpdates = [];
const stopReconnect = reconnecting.watch(value => {reconnectUpdates.push(value);});
let transient = reconnecting.sockets[0];
handshake(transient);
states(transient, [media('kitchen')]);
transient.onclose();
assert.equal(reconnectUpdates.at(-1), null, 'disconnects must clear stale music');
for (const delay of [1000, 2000, 4000, 8000, 16000, 30000, 30000]) {
  assert.equal(reconnecting.timers.size, 1);
  const [id, retry] = [...reconnecting.timers][0];
  assert.equal(retry.delay, delay, 'reconnect delay must back off with a finite cap');
  reconnecting.timers.delete(id);
  retry.fn();
  transient = reconnecting.sockets.at(-1);
  transient.onerror();
}
stopReconnect();
assert.equal(reconnecting.timers.size, 0, 'stopping must cancel reconnect timers');

const invalid = client();
const invalidUpdates = [];
const stopInvalid = invalid.watch(value => {invalidUpdates.push(value);});
const invalidMessage = invalid.sockets[0].onmessage;
invalid.sockets[0].message({type: 'auth_invalid'});
assert.equal(invalidUpdates.at(-1), null);
assert.equal(invalid.timers.size, 0, 'invalid credentials must not trigger a reconnect loop');
assert(invalid.sockets[0].closed);
invalidMessage({data: JSON.stringify({type: 'auth_required'})});
assert.equal(invalid.sockets[0].sent.length, 0, 'late socket handlers must be ignored after disconnection');
stopInvalid();

const unavailable = client();
const unavailableUpdates = [];
const stopUnavailable = unavailable.watch(value => {unavailableUpdates.push(value);});
const [deadlineId, deadline] = [...unavailable.timers][0];
unavailable.timers.delete(deadlineId);
deadline.fn();
assert.equal(unavailableUpdates.at(-1), null, 'stalled handshakes must clear data and reconnect');
assert(unavailable.sockets[0].closed);
assert.equal(unavailable.timers.size, 1);
stopUnavailable();

const configuredWeather = client();
configuredWeather.save({enabled: {weather: true}});
assert.equal(configuredWeather.load().enabled.weather, true, 'saved explicit weather preference must survive');

const unconfigured = client({ha: {url: '', token: ''}});
const missingUpdates = [];
const stopMissing = unconfigured.watch(value => {missingUpdates.push(value);});
assert.deepEqual(missingUpdates, [null]);
assert.equal(unconfigured.sockets.length, 0);
stopMissing();

let previewReply;
let previewCalls = 0;
const preview = client({preview: {refresh(config, done) {previewCalls++; previewReply = done;}}});
const previewUpdates = [];
const stopPreview = preview.watch(value => {previewUpdates.push(value);});
previewReply({nowPlaying: null});
assert.equal(previewCalls, 1);
assert.equal(preview.sockets.length, 0, 'fake previews must not contact HA');
assert.equal(previewUpdates.length, 1);
stopPreview();
previewReply({nowPlaying: null});
assert.equal(previewUpdates.length, 1, 'stopped previews must ignore pending callbacks');
console.log('PASS WidgetData WebSocket subscription, events, races and lifecycle');

function runTimer(client, delay) {
  const entry = [...client.timers].find(([, timer]) => timer.delay === delay);
  assert(entry, 'expected a timer with delay ' + delay);
  client.timers.delete(entry[0]);
  entry[1].fn();
}

const live = client();
const liveUpdates = [];
const stopLive = live.watch(value => {liveUpdates.push(value);});
const liveSocket = live.sockets[0];
handshake(liveSocket);
states(liveSocket, [media('kitchen')]);
runTimer(live, 30000);
assert.deepEqual(liveSocket.sent.at(-1), {id: 3, type: 'ping'});
assert.deepEqual([...live.timers.values()].map(timer => timer.delay), [10000]);
liveSocket.message({type: 'pong', id: 99});
assert.deepEqual([...live.timers.values()].map(timer => timer.delay), [10000],
  'a mismatched pong must not mask a silent connection');
liveSocket.message({type: 'pong', id: 3});
assert.deepEqual([...live.timers.values()].map(timer => timer.delay), [30000]);
runTimer(live, 30000);
assert.deepEqual(liveSocket.sent.at(-1), {id: 4, type: 'ping'}, 'each ping must have a unique id');
runTimer(live, 10000);
assert.equal(liveUpdates.at(-1), null, 'missing pong must clear stale widgets');
assert(liveSocket.closed);
assert.deepEqual([...live.timers.values()].map(timer => timer.delay), [1000],
  'a silent connection must reconnect without polling states');
stopLive();
assert.equal(live.timers.size, 0);

const covers = client();
const coverConfig = covers.load();
coverConfig.enabled.weather = true;
covers.save(coverConfig);
const coverUpdates = [];
const stopCovers = covers.watch(value => {coverUpdates.push(value && JSON.parse(JSON.stringify(value)));});
const coverSocket = covers.sockets[0];
handshake(coverSocket);
const track = media('kitchen', 'playing', {entity_picture: '/cover'});
states(coverSocket, [track]);
assert.equal(covers.requests.length, 1);
const beforePosition = coverUpdates.length;
stateChanged(coverSocket, media('kitchen', 'playing', {entity_picture: '/cover', media_position: 20, volume_level: 0.5}));
assert.equal(coverUpdates.length, beforePosition, 'position and volume updates must not redraw widgets');
stateChanged(coverSocket, {entity_id: 'weather.home', state: 'sunny', attributes: {temperature: 18}});
assert.equal(covers.requests.length, 1, 'weather changes must share an artwork request already in flight');
covers.respond('image-bytes');
assert.equal(coverUpdates.at(-1).nowPlaying.artwork, 'data:image/png;base64,TEST');
const beforeLoadedWeather = coverUpdates.length;
stateChanged(coverSocket, {entity_id: 'weather.home', state: 'sunny', attributes: {temperature: 19}});
assert.equal(covers.requests.length, 1, 'weather updates must reuse loaded artwork');
assert.equal(coverUpdates.length, beforeLoadedWeather + 1);
assert.equal(coverUpdates.at(-1).nowPlaying.artwork, 'data:image/png;base64,TEST',
  'updating weather must never clear the existing cover');
stateChanged(coverSocket, track);
assert.equal(covers.requests.length, 1, 'identical track updates must reuse artwork');
stateChanged(coverSocket, media('kitchen', 'playing', {entity_picture: '/cover', media_title: 'Next Song'}));
assert.equal(covers.requests.length, 2, 'a new track identity must fetch new artwork');
stateChanged(coverSocket, media('kitchen', 'playing', {entity_picture: '/new-cover', media_title: 'Next Song'}));
assert.equal(covers.requests.length, 3, 'a changed picture URL must fetch new artwork');
stopCovers();
assert.equal(covers.timers.size, 0, 'stop must cancel heartbeat timers');
console.log('PASS WidgetData heartbeat liveness and stable artwork cache');
