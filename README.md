# CSV → ShowAds Integration Connector

A Python data connector that:
- Reads customer data from a CSV file
- Validates and transforms rows
- Authenticates with the ShowAds API
- Sends data in compliant batches with retries and backoff

## Quick start

1) Install dependencies
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Configure environment
Create a `.env` file in the project root or export variables in your shell:
```bash
SHOWADS_API_URL="https://api.showads.example.com"
PROJECT_KEY="your-project-key"
# Optional
CSV_PATH="data.csv"           # relative to repo root
BATCH_SIZE="10000"            # capped to 1000 by API
MAX_RETRIES="3"              # request retries
REQUEST_DELAY="0.5"          # seconds between batches
LOG_LEVEL="INFO"
```

3) Run the connector
```bash
python3 src/main.py
```

## CSV schema and validation
Input file defaults to `data.csv` in the repo root. Required headers:

- `Name`: non-empty alphabetic characters and spaces only
- `Age`: positive integer (> 0)
- `Banner_id`: integer in [0, 99]
- `Cookie`: non-empty string

Rows failing validation are skipped. Valid rows are transformed to:
```json
{
  "customer_name": "John Doe",
  "customer_age": 25,
  "customer_cookies": "cookie-string (UUID format)",
  "customer_banner_id": 15
}
```

## API contract and request pattern
- Authentication: `POST {SHOWADS_API_URL}/auth` with JSON `{ "ProjectKey": PROJECT_KEY }` returns `{ "AccessToken": "..." }`.
- Show banner (single-item): `POST {SHOWADS_API_URL}/banners/show` with body:
```json
{ "VisitorCookie": "...", "BannerId": 15 }
```
- Show banners (bulk): `POST {SHOWADS_API_URL}/banners/show/bulk` with body:
```json
{ "Data": [ { "VisitorCookie": "...", "BannerId": 15 }, { "VisitorCookie": "...", "BannerId": 9 } ] }
```
- Bulk request size limit: max 1000 records per request (excess is truncated by the connector).
- Processing windows: data is iterated in windows of size `BATCH_SIZE` for throttling, but each row is sent individually to the single-item endpoint.
- Exponential backoff with jitter on 500/429 responses; other HTTP errors raise.
- Empty 200 OK responses are treated as success.

## Project structure

- `src/main.py`: CLI entrypoint; loads env, configures logging, runs the connector
- `src/connector.py`: abstract `DataConnector` with `read/transform/write/run`
- `src/csv_connector.py`: concrete implementation for CSV → ShowAds
- `src/transform.py`: `validate_row` and `transform_row` logic
- `src/client.py`: `ApiClient` that injects bearer token and handles responses
- `src/auth.py`: `APIToken` service to authenticate and cache/refresh tokens
- `src/http_handler.py`: HTTP client with retries and backoff
- `src/interface.py`: thin interfaces for `AuthService` and `RequestHandler`
- `tests/`: unit tests for API client, retry policy, batching, and validation runner

## Configuration reference

- `SHOWADS_API_URL` (required): Base URL of the ShowAds API
- `PROJECT_KEY` (required): Project credential used to obtain an access token
- `CSV_PATH` (default `data.csv`): CSV file path relative to repo root
- `BATCH_SIZE` (default `10000`, capped to 1000): desired rows per request
- `UPLOAD_MODE` (default `bulk`): `bulk` to use POST /banners/show/bulk, `single` to use POST /banners/show
- `MAX_RETRIES` (default `3`): retries for HTTP 5xx/429 and network errors
- `REQUEST_DELAY` (default `0.5`): wait time between batch calls in seconds
- `LOG_LEVEL` (default `INFO`): Python logging level

## Development

- Run tests
```bash
python3 -m unittest discover -s tests -p "*_tests.py" -v
```

- Detailed validation demo
```bash
python3 tests/validation_test.py
```

## Notes and assumptions

- Names are restricted to alphabetic characters and spaces.
- `Banner_id` accepted range is 0–99 per assignment spec; adjust in `transform.py` if API changes.
- Network stack uses `requests` with exponential backoff; tune in `http_handler.py`.
- Token lifetime currently assumed to be 24h; refresh occurs when expired.

## Troubleshooting

- Missing credentials
  - Ensure `SHOWADS_API_URL` and `PROJECT_KEY` are set (shell or `.env`).

- HTTP 401/403
  - Verify `PROJECT_KEY`; check that auth endpoint is reachable from your network.

- CSV not found
  - Confirm `CSV_PATH` and working directory; default path resolves relative to repo root.

- Partial sends
  - The connector logs totals sent/failed; re-run after fixing upstream issues. Batches are independent.



