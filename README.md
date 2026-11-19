# DataCleanPro

[Features](#features) | [How it works](#how-it-works) | [Install](#install)

**Open Source · MIT License**

# Smart Data Cleaning Powered by AI

Upload CSV, Excel, TSV or JSON — DataCleanPro automatically detects and fixes data quality issues. No Python required by end users.

[Download for free](#install) | [View on GitHub](https://github.com/vijayendrashrimant/DataCleanPRO)

**v1.0.0 Stable** | Blazor Server | .NET 8 | FastAPI | MIT License

---

## DataCleanPro Dashboard

- Dashboard
- History
- Analytics
- Settings

**Engine Status:** Online · EXE Mode

### Data Cleaner

Upload your file to start cleaning.

> Drop your file here or click to browse
>
> CSV · Excel · TSV · JSON · Max 50 MB

**✨ Clean Data**

| Metric | Value |
|---|---:|
| Original Rows | 1,200 |
| Cleaned Rows | 1,187 |
| Columns | 8 |
| Changes Applied | 5 |
| Cleaning Operations | 9 |
| File Formats | 4 |
| Python Required | 0 |
| Maximum File Size | 50 MB |
| Supported Platforms | 3 |

---

<a id="features"></a>

## Features

### Everything you need to clean data

From upload to download in seconds. No configuration, no code, no guesswork.

#### Drag-and-drop upload

CSV, Excel (.xlsx/.xls), TSV and JSON — up to 50 MB. Auto-detects encoding and delimiter.

#### 9 automated cleaning operations

Removes empty rows and columns, deduplicates, normalises whitespace, infers types, fills nulls and more.

#### Live preview table

See up to 500 rows of cleaned data before downloading. Null cells are highlighted.

#### Session history

Every cleaning session is logged with quality score, change report, and retry support.

#### Analytics dashboard

14-day activity charts, quality distribution, format breakdown, and most common issues.

#### Configurable settings

Null fill strategy, duplicate action, thresholds, export format — all persisted to disk.

---

## Cleaning Operations

### What gets fixed automatically

Every operation is applied in order, and each change is recorded in the cleaning report.

| Operation | Description |
|---|---|
| Empty rows & columns | Drops 100% null rows and columns |
| Duplicate rows | Removes duplicates or flags them in a new column |
| Whitespace | Trims leading/trailing spaces and collapses repeated spaces |
| Type inference | Auto-casts to numeric or datetime |
| Null fill | Median, mean, zero, or drop row |
| Title-case | Applied to categorical string columns |
| Column name cleaning | Strips whitespace from headers |
| Export format | Same as input, CSV, or Excel |
| Quality score | Scores original data quality from 0–100 |

---

<a id="how-it-works"></a>

## How It Works

### Four steps from dirty to clean

No configuration required — the engine figures it out.

**1. Upload**

Drop any CSV, Excel, TSV or JSON file.

**2. Clean**

Click once — 9 operations run in sequence.

**3. Review**

See the full report and 500-row preview.

**4. Download**

Get the full cleaned file in your preferred format.

---

## Application Pages

### Four powerful views

Every page communicates with the FastAPI engine running silently in the background.

#### Dashboard

- Drag-and-drop upload zone
- Accepts CSV, Excel, TSV and JSON up to 50 MB
- Format validation
- 7-step animated pipeline
- Parse → Detect Types → Remove Empties → Fix Nulls → Deduplicate → Normalise → Done
- Live preview table
- Scrollable preview of up to 500 rows
- Null cells styled
- Fixed header columns
- Quality score from 0–100
- Quality progress bar and rating label

#### History

- Search and filter by filename
- Filter by file format (CSV, Excel, TSV, JSON)
- Filter by quality band
- Expandable cleaning reports
- View full per-operation reports inline
- Delete individual history entries
- Clear all history with confirmation
- Green, amber and red quality badges

#### Analytics

- 14-day activity charts
- Files cleaned per day
- Rows processed per day
- Today's activity highlighted
- Quality distribution
- Excellent / Good / Poor breakdown
- Percentage bars and average score
- Most common cleaning issues
- Ranked horizontal bars
- Format breakdown
- CSV, Excel, TSV and JSON counts and percentages

#### Settings

- Null fill strategy
- Choose median, mean, zero or drop row
- Duplicate action
- Remove duplicates or flag duplicates
- Flag column: `__is_duplicate__`
- Threshold sliders
- Tune title-case and numeric-cast thresholds
- Live percentage readout
- Export format
- Same as input, CSV or Excel
- Persistent settings

---

## What's New in v1.0.0

- Blazor Server web app
- Instant load without WebAssembly download
- Persistent SignalR connection
- Self-contained FastAPI executable via PyInstaller
- No Python required by end users
- FastApiService IHostedService
- Python process starts and stops automatically with the .NET host
- Smart launch priority: bundled EXE → backend/dist → Python venv → system Python
- Dashboard, History, Analytics and Settings pages
- Full CRUD, search and charts
- 9 configurable cleaning operations wired to saved settings
- Threading lock on history file writes
- Concurrent sessions safe
- 5-second analytics cache
- Live API status pill in sidebar
- Shows EXE/Python mode and port

---

## Known Limitations

- PyInstaller EXE first cold-start can take 3–8 seconds depending on hardware.
- macOS Gatekeeper may require right-click → Open on first launch.
- Files over 50 MB are rejected at the upload layer.

**v1.0.0** | .NET 8 | MudBlazor 7.6.0 | FastAPI

[Full Changelog](https://github.com/vijayendrashrimant/DataCleanPRO/compare/v0.0.0...v1.0.0)

---

<a id="install"></a>

## Installation

### Up and running in 60 seconds

The run script handles everything — venv setup, process management, and browser launch.

### Quick Start

**1. Download**

Download the ZIP for your platform from the Releases section and extract it.

**2. Run**

Windows:

```bat
run.bat
```

macOS/Linux:

```bash
./run.sh
```

**3. Open**

The browser opens automatically at:

```text
http://localhost:5000
```

**4. Stop**

Press `Ctrl+C` to stop both the web server and API engine cleanly.

---

### Build the Executable (Optional)

Build a self-contained API binary. Requires Python 3.11+ and pip.

macOS/Linux:

```bash
./build_exe.sh
```

Windows:

```bat
build_exe.bat
```

Output:

```text
backend/dist/datacleanpro_api
```

---

## Requirements

| Requirement | Details | Status |
|---|---|---|
| .NET Runtime 8 | dotnet.microsoft.com/download | Required |
| Python 3.11+ | Build EXE only | Build only |
| FastAPI Engine | Bundled in release ZIP | Bundled |
| Windows 10/11 | x64 | Supported |
| macOS 12+ | Intel & Apple Silicon | Supported |
| Linux | Ubuntu 20.04+ / x64 | Supported |

---

### How the EXE Is Launched

FastApiService resolves the engine using this priority order.

#### Priority 1 — Deployed Layout

```text
frontend/api/datacleanpro_api
```

#### Priority 2 — Development Build Output

```text
backend/dist/datacleanpro_api
```

#### Priority 3 — Python Virtual Environment

```bash
venv/bin/python -m uvicorn main:app
```

#### Priority 4 — System Python

```bash
python3 -m uvicorn main:app
```

---

## DataCleanPro

**AI-powered data cleaning for everyone.**

No Python required. No cloud. Just clean data.

**Tech Stack**

.NET 8 · Blazor Server · FastAPI · MudBlazor · PyInstaller · pandas · SignalR

### Project

- [GitHub Repository](https://github.com/vijayendrashrimant/DataCleanPRO)
- [Documentation](https://github.com/vijayendrashrimant/DataCleanPRO/blob/main/README.md)
- [License](https://github.com/vijayendrashrimant/DataCleanPRO/blob/main/LICENSE)

---

© 2025 DataCleanPro · MIT License · `vijayendrashrimant`

