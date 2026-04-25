# The World Is Shaking

A real-time seismic activity dashboard powered by a fully automated AWS data pipeline. Earthquake data from the USGS is ingested daily, processed, and served via CloudFront to an interactive map built with Leaflet.js.

**[Live Dashboard](https://faustosp.github.io/the_world_is_shaking)**

![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20CloudFront%20%7C%20EventBridge-FF9900?logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)

---

## Architecture

```mermaid
flowchart LR
    USGS["USGS Feed"]
    EB["EventBridge"]
    L1["Lambda: Ingestor"]
    S3R["S3: Raw"]
    L2["Lambda: Transformer"]
    S3P["S3: Processed"]
    CF["CloudFront"]
    GP["GitHub Pages"]

    EB -->|daily trigger| L1
    USGS -->|GeoJSON| L1
    L1 -->|raw data| S3R
    S3R -->|S3 notification| L2
    L2 -->|processed JSON| S3P
    S3P -->|OAC| CF
    CF -->|fetch| GP
```

### How it works

1. **EventBridge** fires a daily cron at 12:00 UTC
2. The **ingestor Lambda** (Python) fetches the [USGS all-month GeoJSON feed](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson) and stores the raw response in a private S3 bucket
3. The S3 upload triggers the **transformer Lambda** automatically via an S3 ObjectCreated notification
4. The transformer flattens the GeoJSON, filters out null-magnitude events, and writes a clean `earthquakes_processed.json` with a `last_updated` timestamp to a second private S3 bucket
5. **CloudFront** serves the processed file via a CDN, authenticated to S3 using Origin Access Control (OAC)
6. The **GitHub Pages** frontend fetches from CloudFront and renders the dashboard

---

## Features

- **Interactive world map** — earthquake markers colour-coded and sized by magnitude, with popups showing location, depth, and timestamp
- **Magnitude filter** — slider to filter events in real time
- **Stats cards** — total events, strongest earthquake with location, and average magnitude for the past month
- **Distribution chart** — bar chart of event counts by magnitude range
- **Staleness indicator** — warns if the pipeline hasn't updated in over 25 hours

---

## Tech Stack

| Category       | Technology               |
| -------------- | ------------------------ |
| Infrastructure | Terraform                |
| Scheduler      | AWS EventBridge          |
| Compute        | AWS Lambda (Python 3.12) |
| Storage        | AWS S3                   |
| CDN            | AWS CloudFront           |
| Monitoring     | AWS CloudWatch Logs      |
| Frontend       | HTML, CSS, JavaScript    |
| Hosting        | GitHub Pages             |

---

## Infrastructure

All AWS infrastructure is declared in Terraform under [`terraform/`](terraform/). Key design decisions:

- **Least privilege IAM**: the ingestor role can only `PutObject` to `raw/*`, the transformer role can only `GetObject` from raw and `PutObject` to processed
- **Private S3 buckets**: both buckets have all public access blocked; CloudFront accesses the processed bucket exclusively via OAC
- **CORS restricted**: CloudFront only allows requests from `faustosp.github.io`
- **No hardcoded credentials**: the AWS account ID is resolved dynamically via `aws_caller_identity`

---

_Data source: [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)_
