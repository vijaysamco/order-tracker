# Order Tracker

A small order tracking app for the AI Dev Tools Zoomcamp observability homework. It includes a web page, API, tests, and a Docker Compose setup. You add telemetry, alerts, and an incident responder in Homework 4.

The main user flow is creating an order and checking its status. Three sample orders are created on first startup.

## Run it

You need Docker with Compose. To run the tests, you also need Python 3.11+ and `uv`.

```bash
docker compose up --build -d --wait
```

Open <http://127.0.0.1:8000>. The API is at `/api/orders`, and the health check is at `/healthz`. Data is stored in a Docker volume and survives container recreation.

## Observability stack

Docker Compose also starts an OpenTelemetry Collector, Prometheus, Loki, Tempo, and Grafana. The app sends metrics, logs, and traces to the Collector over OTLP gRPC. Grafana is available at <http://127.0.0.1:3000> (default login `admin` / `admin`); change these with `GRAFANA_USER` and `GRAFANA_PASSWORD`. The provisioned **Order Tracker Observability** dashboard shows request counts and HTTP errors. Use Grafana Explore with the Loki and Tempo data sources to inspect lookup logs and traces.

The incident responder is available at <http://127.0.0.1:8001>. It persists each alert and the matching recent Loki logs and Tempo traces under the `incident-response` Docker volume, then invokes GitHub Copilot CLI in programmatic mode. Configure a Copilot CLI token as `COPILOT_GITHUB_TOKEN` in your local `.env` file before starting Compose; do not commit that file. If the assistant is unavailable, the responder still records the incident and returns an explicit unavailable/error status. Test alerts marked `test=true` are only acknowledged and do not request source changes.

To submit a Grafana-style test notification:

```bash
curl -X POST http://localhost:8001/alerts \
	-H 'Content-Type: application/json' \
	-d '{"alerts":[{"status":"firing","labels":{"alertname":"ResponderTest","test":"true"},"annotations":{"summary":"Test notification; no incident to fix"}}]}'
```

The response includes the assistant's result; retrieve the full saved record from `GET /incidents/{incident_id}`.

If port 8000 is occupied, set `ORDER_TRACKER_PORT`, for example:

```bash
ORDER_TRACKER_PORT=18080 docker compose up --build -d --wait
```

Run tests with `uv run --frozen pytest -q`. Stop the app with `docker compose down`. Add `-v` only if you also want to delete the order data.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Web page |
| GET | `/healthz` | Database health check |
| GET | `/api/orders` | List orders |
| POST | `/api/orders` | Create an order |
| GET | `/api/orders/{id}` | Check an order |
| PATCH | `/api/orders/{id}` | Change an order status |

The app uses SQLite to keep setup small. Run one app container at a time. The course exercise is about detecting and handling an incident, not scaling the database.
