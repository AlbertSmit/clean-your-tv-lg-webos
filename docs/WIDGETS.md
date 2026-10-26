# Widgets (tvOS style): Clock, Weather, Now Playing

The Home screen's **tvOS appearance** shows HomeView-inspired decorative widgets
on the same six-column grid as the dock. The upper-left logo area stays clear:

- **Clock** — a green analog face with large numerals and a short local date, below the logo. Works with no setup.
- **Weather** — an optional blue square with current condition, temperature,
  high/low and humidity. It starts off for new installations; a previously saved
  explicit enabled choice is respected.
- **Now Playing** — artwork, title and artist for music currently
  playing in your home, in a compact 2:1 card on the right. Artwork sits on the
  left, with a localized “Now Playing” label, title and artist at the bottom
  right and a music glyph in the upper corner. Album text is omitted. It appears
  only when current music and a title are confirmed. There are no playback controls.
  Its glass texture, taupe tint, refraction, corners and shadow follow the dock,
  with an opaque fallback when Reduce effects is enabled.

Widgets are **not part of the remote-focus grid**: they are information-only,
never intercept the pointer or the remote, and are hidden in the `Existing`
appearance. They hide while browsing the app grid or using the Home controls,
and respect the **Reduce effects** preference. Empty grid cells have no outlines.

## Show or hide all widgets

The **Widgets** switch in the Home header toggles all widgets together. Click it
with the pointer, or from the dock press **Up → Right → OK** (Settings → Widgets).
Toggling returns focus to the dock. This switch starts on and remembers your
choice across restarts, without changing the individual widget settings.
Switching it off also disconnects Home Assistant live updates.
The `Existing` appearance is unchanged.

## How the data gets in

The widgets read from a single runtime source, `window.WidgetData`
(`launcher/widget-data.js`), which has two modes:

1. **Browser preview** — `preview/bridge.js` provides `window.WidgetPreview`, a
   fake provider, so the widgets render with sample data while developing.
2. **Home Assistant (HA)** — on a real TV, the launcher connects to HA's WebSocket API
   (`/api/websocket`) with a long-lived access token, loads an initial state
   snapshot and then follows state changes. No native/Luna service
   changes are required, so this works identically on the No-root and Root
   editions.

There is no direct Apple Home browser feed. Use Home Assistant media-player
entities, including those created by the official [Apple TV integration](https://www.home-assistant.io/integrations/apple_tv/).
For a HomePod, verify the actual entity and metadata exposed by your HA setup.
A registered device page alone does not prove music metadata support; inspect
its `media_player.*` entity while music plays. The widget requires
`state: playing`, `media_content_type: music`, and a nonempty `media_title`.
See HA's [media-player entity model](https://contributors.home-assistant.io/core/entities/media-player/).
Other players work when their HA integration exposes these fields.

### Configuring Home Assistant

1. Open the dashboard of the Home Assistant server that contains your players.
   Use that server's base URL, including its port if present, as the
   **Home Assistant URL**. Remove dashboard or configuration suffixes such as
   `/lovelace/...` or `/config/devices/...`; do not enter a HomePod's address.
2. In Home Assistant, open your **Profile → Security → Long-lived access tokens**
   and create a token for this TV.
3. On the TV, open **Home settings → Widgets**, enter the base URL and token,
   and save the widget sources. Keep the master Widgets switch on.
4. Play music, then check the player's state and attributes under HA's
   **Developer tools → States**. It must report `playing`,
   `media_content_type: music`, and a nonempty `media_title`. Allow the
   live state update before expecting Now Playing on the TV.

The launcher authenticates its live connection with your token and subscribes
to state changes; see the official [HA WebSocket API reference](https://developers.home-assistant.io/docs/api/websocket/).
A one-shot REST refresh helper remains available for development, but ordinary
launcher updates do not poll `GET /api/states`; see the [REST API reference](https://developers.home-assistant.io/docs/api/rest/).

Optional source fields:

- **Media player entity** *(optional)* — e.g. `media_player.tv_living_room`.
  Leave it blank to scan all `media_player.*` entities for playing music with a
  title. If several qualify, the first in the HA response is shown. Set an entity
  to restrict detection to that player; there is no fallback to another player.
- **Weather entity** *(optional)* — e.g. `weather.home`. If omitted, the first
  `weather.*` entity is used.

Toggle each widget on/off independently. Settings are stored locally in
`localStorage` (`cytv-widgets`); the separate master choice uses
`cytv-widgets-visible` (default `true`). The text fields are edited with the
pointer / Magic Remote (the remote's arrow focus cycles the toggle buttons).

While the master switch is on and the tvOS appearance and document are visible,
Home Assistant pushes live state changes after the initial snapshot. The
connection closes when the master switch is off, the document is hidden or the
Existing appearance is selected, and restarts when needed. Temporary connection
failures retry after 1 second, doubling up to 30 seconds. An invalid-token
response stops automatic retries; correct and save the configuration, or restart
the connection after replacing the token.

### Notes and caveats

- The TV webview targets a Chrome 38-era engine (see `.browserslistrc`). Live
  updates use native WebSocket (`ws:` for an HTTP base URL, `wss:` for HTTPS).
  Authorized artwork still uses `XMLHttpRequest`; configure HA CORS to permit
  the launcher origin where required. HTTPS/WSS connections can fail on the TV's
  old TLS stack, particularly with an untrusted certificate.
- Album artwork is fetched only from the configured HA origin, with the same
  authorization header, and converted to a data URL for display. External artwork
  URLs are ignored. The live endpoint is `/api/websocket`; the separate one-shot
  refresh helper uses `/api/states`.
- If HA is unreachable or not configured, enabled Weather keeps its placeholders and
  the Clock keeps working. Now Playing hides when music is missing, stopped, paused or unreachable. Its reserved position
  remains unchanged, and other widgets do not move. Disabled widgets hide
  independently.
- The long-lived token is stored in plain text in `localStorage` on the TV.
  This is a local, single-user device, but treat it accordingly.
