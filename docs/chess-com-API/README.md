# Chess.com Published Data API

This directory documents the chess.com public API endpoints for fetching user games, based on the official API documentation and live verification.

## Overview

- **Base URL**: `https://api.chess.com/pub/`
- **Authentication**: None required (public data)
- **HTTP Method**: GET only (read-only API)
- **Response Format**: JSON-LD (or raw PGN for PGN endpoint)
- **Rate Limiting**: Serial requests unlimited; parallel requests may receive 429 responses
- **Caching**: All responses include ETag and Last-Modified headers for conditional requests

## Game-Related Endpoints

### 1. Current Daily Chess Games
**URL**: `GET /pub/player/{username}/games`

Returns daily chess games currently in progress.

**Response Structure**:
```json
{
  "games": [
    {
      "white": {"username": "string", "rating": number, "result": "string", "@id": "string"},
      "black": {"username": "string", "rating": number, "result": "string", "@id": "string"},
      "url": "string",
      "fen": "string",
      "pgn": "string",
      "turn": number,
      "move_by": number,
      "draw_offer": "string (optional)",
      "last_activity": number,
      "start_time": number,
      "time_control": "string",
      "time_class": "daily",
      "rules": "string",
      "tournament": "string (optional)",
      "match": "string (optional)"
    }
  ]
}
```

**Notes**:
- Returns empty array `{"games": []}` when no games in progress
- `start_time` only present for daily chess games
- `draw_offer` only present when a draw has been offered

---

### 2. Games To Move
**URL**: `GET /pub/player/{username}/games/to-move`

Returns daily chess games where it's the player's turn to move.

**Response Structure**:
```json
{
  "games": [
    {
      "url": "string",
      "move_by": number,
      "draw_offer": "string (optional)",
      "last_activity": number
    }
  ]
}
```

**Notes**:
- May include games where it's not the player's turn if a draw offer was made
- When `move_by` is "0", the game sorts to the top

---

### 3. List of Monthly Archives
**URL**: `GET /pub/player/{username}/games/archives`

Returns list of all monthly archive URLs for the player.

**Response Structure**:
```json
{
  "archives": [
    "https://api.chess.com/pub/player/{username}/games/2014/01",
    "https://api.chess.com/pub/player/{username}/games/2014/02",
    ...
    "https://api.chess.com/pub/player/{username}/games/2026/08"
  ]
}
```

**Notes**:
- URLs are in ascending chronological order
- Final entry is the current (in-progress) month
- No pagination; full list returned in one response
- **Primary endpoint for incremental fetching**: compare against previously fetched months

**Example** (verified live for user "hikaru"):
- 152 archive URLs from 2014/01 through 2026/08
- Response includes ETag, Last-Modified headers
- Cache-Control: `public, max-age=60`

---

### 4. Complete Monthly Archive (Primary Bulk Endpoint)
**URL**: `GET /pub/player/{username}/games/{YYYY}/{MM}`

**Parameters**:
- `YYYY`: Four-digit year (required)
- `MM`: Two-digit month (required)

Returns all games that ended in the specified month.

**Response Structure**:
```json
{
  "games": [
    {
      "url": "string",
      "pgn": "string",
      "time_control": "string",
      "end_time": number,
      "rated": true,
      "accuracies": {
        "white": number,
        "black": number
      },
      "tcn": "string",
      "uuid": "string",
      "initial_setup": "string",
      "fen": "string",
      "time_class": "string",
      "rules": "string",
      "eco": "string",
      "white": {
        "rating": number,
        "result": "string",
        "@id": "string",
        "username": "string",
        "uuid": "string"
      },
      "black": {
        "rating": number,
        "result": "string",
        "@id": "string",
        "username": "string",
        "uuid": "string"
      },
      "tournament": "string (optional)",
      "match": "string (optional)"
    }
  ]
}
```

**Game Object Fields**:
- `url`: Game URL on chess.com
- `pgn`: Full game notation in PGN format
- `time_control`: Time control in PGN notation (e.g., "180+2")
- `end_time`: Unix timestamp when game ended
- `rated`: Boolean indicating if game was rated (live time controls only)
- `accuracies`: Accuracy percentages for both players
- `tcn`: Transmitted chess notation (undocumented)
- `uuid`: Unique game identifier (undocumented)
- `initial_setup`: Starting FEN position (undocumented)
- `fen`: Final position FEN
- `time_class`: "daily", "rapid", "blitz", or "bullet"
- `rules`: "chess", "chess960", "bughouse", "kingofthehill", "threecheck", "crazyhouse"
- `eco`: Opening classification code
- `white`/`black`: Player objects with rating, result, username, uuid
- `tournament`: Tournament identifier if applicable
- `match`: Team match identifier if applicable

**Result Codes** (from `white.result` and `black.result`):
- `win`, `checkmated`, `agreed`, `repetition`, `timeout`, `resigned`
- `stalemate`, `lose`, `insufficient`, `50move`, `abandoned`
- `kingofthehill`, `threecheck`, `timevsinsufficient`, `bughousepartnerlose`

**Notes**:
- Games ordered ascending by end_time
- Empty array if no games in that month
- **No pagination within a month** - entire month returned in one response
- Supports conditional requests (ETag/If-None-Match) for change detection
- Cache-Control: `public, max-age=5`

**Example** (verified live for "hikaru" 2026/07):
- 588 games returned
- Response size: ~2.5 MB
- All documented fields present plus undocumented `tcn`, `uuid`, `initial_setup`

---

### 5. Complete Live Archive by Time Control
**URL**: `GET /pub/player/{username}/games/live/{BASETIME}/{INCREMENT}`

**Parameters**:
- `BASETIME`: Base time in seconds (required)
- `INCREMENT`: Increment in seconds (required, despite docs showing it as optional)

Returns all historical games for the specified time control.

**Response Structure**:
```json
{
  "games": [
    {
      "url": "string",
      "pgn": "string",
      "time_control": "string",
      "end_time": number,
      "rated": true,
      "accuracies": {
        "white": number,
        "black": number
      },
      "fen": "string",
      "time_class": "string",
      "rules": "string",
      "eco": "string",
      "white": {
        "rating": number,
        "result": "string",
        "@id": "string",
        "username": "string",
        "uuid": "string"
      },
      "black": {
        "rating": number,
        "result": "string",
        "@id": "string",
        "username": "string",
        "uuid": "string"
      }
    }
  ]
}
```

**Notes**:
- No `start_time` field (only present in daily chess)
- Games ordered ascending by end_time
- **Increment parameter is effectively required** - `/games/live/60` returns 404, but `/games/live/60/0` works
- Returns complete historical set for that time control (not date-parameterized)

**Example** (verified live for "hikaru" 180+2):
- 615 games returned

---

### 6. Multi-Game PGN Download
**URL**: `GET /pub/player/{username}/games/{YYYY}/{MM}/pgn`

**Parameters**:
- `YYYY`: Four-digit year (required)
- `MM`: Two-digit month (required)

Returns raw multi-game PGN file (not JSON).

**Response**:
- Content-Type: `application/vnd.chess-pgn; charset=utf-8` (docs say `application/x-chess-pgn`)
- Content-Disposition: `attachment; filename="ChessCom_{username}_{YYYYMM}.pgn"`
- Raw PGN format following PGN standard

**Notes**:
- Not JSON - raw PGN text
- Contains all games from the month in PGN format
- Cache-Control: `public, max-age=5`

**Example** (verified live for "hikaru" 2026/07):
- File size: 1,855,169 bytes (~1.8 MB)
- Filename: `ChessCom_hikaru_202607.pgn`

---

## Other Relevant Endpoints

### Player Profile
**URL**: `GET /pub/player/{username}`

Returns player profile information including stable `player_id` for detecting username changes.

**Response Structure**:
```json
{
  "url": "string",
  "username": "string",
  "player_id": number,
  "title": "string (optional)",
  "status": "string",
  "name": "string",
  "avatar": "string",
  "location": "string",
  "country": "string",
  "joined": number,
  "last_online": number,
  "followers": number,
  "is_streamer": boolean,
  "twitch_url": "string",
  "fide": number
}
```

---

### Player Stats
**URL**: `GET /pub/player/{username}/stats`

Returns player ratings, records, and statistics.

**Response Structure**:
```json
{
  "chess_blitz": {
    "last": {"rating": number, "date": number, "rd": number},
    "best": {"rating": number, "date": number, "rd": number},
    "record": {"win": number, "loss": number, "draw": number}
  },
  "chess_rapid": {...},
  "chess_daily": {...},
  "chess_bullet": {...},
  "tactics": {...},
  "lessons": {...},
  "puzzle_rush": {...}
}
```

---

## Rate Limiting

### Official Guidance
- **Serial access**: Unlimited - if you wait for each response before making the next request, you should never encounter rate limiting
- **Parallel requests**: May be blocked depending on server load; be prepared to handle 429 responses
- **No numeric quota documented**: No specific requests-per-second or requests-per-minute limits published
- **No rate-limit headers**: Responses do not include `x-ratelimit-*` headers

### Best Practices
1. **Use serial requests**: Wait for each response before making the next request
2. **Add delays between requests**: Recommended for bulk operations
3. **Handle 429 responses**: Implement retry logic with exponential backoff
4. **Use recognizable User-Agent**: Include contact information in case of issues
5. **Avoid abnormal patterns**: Suspicious activity may result in complete blocking

### Recommended Approach for Bulk Fetching
- Make requests serially (one at a time)
- Add 1-2 second delay between requests
- Implement retry logic for 429 responses
- Use conditional requests (ETag) to avoid re-downloading unchanged data

---

## Caching and Conditional Requests

### HTTP Caching Headers
All responses include:
- `ETag`: Entity tag for conditional requests
- `Last-Modified`: Timestamp of last modification
- `Cache-Control`: Cache duration (varies by endpoint)
- `cf-cache-status`: CDN cache status (HIT/MISS/EXPIRED/REVALIDATED)

### Conditional Requests
Use conditional headers to avoid re-downloading unchanged data:
- `If-None-Match: <ETag>` - Returns 304 if content unchanged
- `If-Modified-Since: <timestamp>` - Returns 304 if not modified since timestamp

**Example**:
```
GET /pub/player/hikaru/games/2026/07
If-None-Match: "abc123"

Response: 304 Not Modified (if unchanged)
```

### Cache Durations (Observed)
- Monthly archives list: `max-age=60` (1 minute)
- Monthly archive: `max-age=5` (5 seconds)
- PGN download: `max-age=5` (5 seconds)
- Current games: `max-age=5` (5 seconds)
- Live time control archive: `max-age=5` (5 seconds)

### Data Refresh Cadence
**Documentation states**:
- "Endpoints refresh at most once every 12 hours" (Cache invalidation section)
- "Endpoints refresh at most once every 24 hours, if not noted otherwise" (Caching section)

**Observed behavior**: Monthly archive content can refresh more frequently than documented (observed updates within ~1 hour window).

---

## Incremental Fetching Strategy

### Monthly Archive Granularity
The API is designed around monthly archives as the incremental unit:

1. **Fetch archive list**: `GET /pub/player/{username}/games/archives`
   - Returns all available monthly archive URLs
   - Final entry is the current (in-progress) month

2. **Track fetched months**: Store which months have been fetched locally

3. **Fetch only new months**: Compare archive list against local state
   - Download only months not yet fetched
   - Re-download current month (it's updated as games finish)

4. **Use conditional requests**: For previously fetched months, use ETag to detect changes
   - If 304 response, skip download
   - If 200 response, download updated data

### No Pagination Within Months
- Each monthly archive returns all games for that month in one response
- No page/offset/cursor parameters exist
- Large months may return hundreds of games (e.g., 588 games in one month)

### Recommended Incremental Approach
```
1. Fetch /games/archives to get list of all months
2. Compare against local state (which months fetched, their ETags)
3. For each month:
   a. If not fetched: download full archive
   b. If fetched but current month: use conditional request (ETag)
      - If 304: skip (unchanged)
      - If 200: download updated archive
   c. If fetched and not current month: skip (historical months don't change)
4. Update local state with new ETags
```

---

## HTTP Response Codes

- **200**: Success
- **301**: Bad URL but known redirect target
- **304**: Not modified (conditional caching)
- **404**: Malformed URL or unavailable data
- **410**: No data will ever be available (do not re-request)
- **429**: Rate limited

**Example 404 response**:
```json
{
  "code": 0,
  "message": "User \"username\" not found."
}
```

---

## Additional Features

### JSONP Support
Any URL supports JSONP via `?callback=` query parameter:
```
GET /pub/player/hikaru/games/archives?callback=myFunction
```
**Notes**: Function names >200 chars or containing non-literal characters are stripped.

### Compression
- Supports gzip when `Accept-Encoding: gzip` header is sent
- Observed: brotli compression (`content-encoding: br`) for browser requests

### JSON-LD Context
Responses include JSON-LD context via `Link` response header:
```
Link: <https://api.chess.com/context/GameArchives.jsonld>; rel="..."
```

---

## Documentation Contradictions

1. **PGN Content-Type**: Docs specify `application/x-chess-pgn`; live server returns `application/vnd.chess-pgn; charset=utf-8`

2. **Live time-control increment**: Docs show increment as optional `(INCREMENT)`; live server requires it (returns 404 without increment)

3. **Refresh cadence**: Docs state both "12 hours" and "24 hours"; live observations show more frequent updates

4. **Compression**: Docs describe gzip; live responses use brotli

---

## References

- Official API documentation: https://www.chess.com/news/view/published-data-api
- API base URL: https://api.chess.com/pub/
- Game result codes: https://www.chess.com/news/view/published-data-api#game-results
