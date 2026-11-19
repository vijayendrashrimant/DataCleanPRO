[DataCleanPro](#)

[Features](#features) [How it works](#how) [Install](#install)

Open Source · MIT License

# Smart Data Cleaning powered by AI

Upload CSV, Excel, TSV or JSON — DataCleanPro automatically detects and fixes quality issues. No Python required by end users.

[Download for free] [View on GitHub](https://github.com/vijayendrashrimant/DataCleanPRO)

v1.0.0 stable Blazor Server .NET 8 · FastAPI MIT License

localhost:5000

DataCleanPro

Dashboard

History

Analytics

Settings

Engine Online · exe mode

Data Cleaner

☁️

Drop your file here or click to browse\
CSV · Excel · TSV · JSON · Max 50 MB

✨ Clean Data

1,200

Original Rows

1,187

Cleaned Rows

8

Columns

5

Changes Applied

9

Cleaning ops

4

File formats

0

Python needed\*

50MB

Max file size

3

Platforms

Features

## Everything you need to clean data

From upload to download in seconds. No configuration, no code, no guesswork.

Drag-and-drop upload

CSV, Excel (.xlsx/.xls), TSV and JSON — up to 50 MB. Auto-detects encoding and delimiter.

9 automated cleaning ops

Removes empties, deduplicates, normalises whitespace, infers types, fills nulls and more.

Live preview table

See up to 500 rows of cleaned data before downloading. Null cells are highlighted.

Session history

Every cleaning session is logged with quality score, change report, and retry support.

Analytics dashboard

14-day activity charts, quality distribution, format breakdown, most common issues.

Configurable settings

Null fill strategy, duplicate action, thresholds, export format — all persisted to disk.

Cleaning operations

## What gets fixed automatically

Every operation is applied in order, and each change is recorded in the cleaning report.

Empty rows & columns

100% null rows and columns dropped

Duplicate rows

Remove or flag in a new column

Whitespace

Trims leading/trailing, collapses runs

Type inference

Auto-casts to numeric or datetime

Null fill

Median, mean, zero, or drop row

Title-case

Applied to categorical string columns

Column name cleaning

Strips whitespace from headers

Export format

Same as input, always CSV, or always Excel

Quality score

0–100 score of original data quality

How it works

## Four steps from dirty to clean

No configuration required — the engine figures it out.

1

Upload

Drop any CSV, Excel, TSV or JSON file

2

Clean

Click once — 9 operations run in sequence

3

Review

See the full report and 500-row preview

4

Download

Get the full cleaned file in your format

Application pages

## Four powerful views

Every page communicates with the FastAPI engine running silently in the background.

Drag-and-drop upload zone

Accepts CSV, Excel, TSV, JSON up to 50 MB with format validation

7-step animated pipeline

Parse → Detect Types → Remove Empties → Fix Nulls → Deduplicate → Normalise → Done

Live preview table

Scrollable up to 500 rows, null cells styled, fixed header columns

Quality score 0–100

Rates the original data quality before cleaning with a progress bar and rating label

Search and filter

Filter by filename, file format (CSV/Excel/TSV/JSON) and quality band

Expandable reports

Click the eye icon on any entry to see the full per-operation cleaning report inline

Delete and clear

Remove individual entries or clear all history with a confirmation dialog

Quality badges

Green / amber / red badges show original data quality score for each session

14-day activity charts

Files cleaned per day and rows processed per day — today highlighted in primary colour

Quality distribution

Excellent / Good / Poor breakdown with percentage bars and average score

Most common issues

Ranked horizontal bars showing which cleaning ops fire most often across all files

Format breakdown

Count and percentage tiles per file format — CSV, Excel, TSV, JSON

Null fill strategy

Choose median, mean, zero, or drop row — applied to all numeric columns

Duplicate action

Remove duplicates or flag them in a new `__is_duplicate__` column

Threshold sliders

Tune title-case and numeric-cast thresholds with live percentage readout

Export format

Same as input, always CSV, or always Excel — applied on every download


#### What's new

- Blazor Server web app — instant load, no WebAssembly download, persistent SignalR connection
- Self-contained FastAPI executable via PyInstaller — no Python required by end users
- FastApiService IHostedService — Python process starts and stops with the .NET host automatically
- Smart launch priority: bundled exe → backend/dist → Python venv → system Python
- Dashboard, History, Analytics and Settings pages — full CRUD, search, charts
- 9 configurable cleaning operations wired to saved settings
- Threading lock on history file writes — concurrent sessions safe
- 5-second analytics cache — avoids re-parsing JSON on every page load
- Live API status pill in sidebar — shows exe/python mode and port

#### Known limitations

- PyInstaller exe first cold-start can take 3–8 s depending on hardware
- macOS Gatekeeper may require right-click → Open on first launch
- Files over 50 MB are rejected at the upload layer

v1.0.0 .NET 8 · MudBlazor 7.6.0 · FastAPI 0.111 [Full changelog →](https://github.com/yourusername/datacleanpro/compare/v0.0.0...v1.0.0)

Installation

## Up and running in 60 seconds

The run script handles everything — venv setup, process management, and browser launch.

### Quick start

1

Download the zip for your platform from the Releases section above and extract it

2

Run `./run.sh` on macOS/Linux or `run.bat` on Windows

3

Browser opens automatically at `http://localhost:5000`

4

Press `Ctrl+C` to stop — both the web server and the API engine close cleanly

### Build the executable (optional)

Build a self-contained API binary — users need no Python at runtime. Requires Python 3.11+ and pip.

\# macOS / Linux

./build_exe.sh

\# Windows

build_exe.bat

\# Output

backend/dist/datacleanpro_api

### Requirements

⚙️

.NET Runtime 8

dotnet.microsoft.com/download

Required

🐍

Python 3.11+

Only to build the exe

Build only

📦

FastAPI engine

Bundled in release zip

Bundled

🪟

Windows 10/11

x64

Supported

🍎

macOS 12+

Intel & Apple Silicon

Supported

🐧

Linux x64

Ubuntu 20.04+

Supported

### How the exe is launched

FastApiService resolves the engine using this priority order:

\# Priority 1 — deployed layout

frontend/api/datacleanpro_api

\# Priority 2 — dev build output

backend/dist/datacleanpro_api

\# Priority 3 — Python venv

venv/bin/python -m uvicorn main:app

\# Priority 4 — system Python

python3 -m uvicorn main:app

DataCleanPro

AI-powered data cleaning for everyone. No Python required. No cloud. Just clean data.

.NET 8 Blazor Server FastAPI MudBlazor PyInstaller pandas SignalR

#### Project

[GitHub Repository](https://github.com/vijayendrashrimant/DataCleanPRO)  [Documentation](https://github.com/yourusername/datacleanpro/blob/main/README.md)


© 2025 DataCleanPro · MIT License · Replace `vijayendrashrimant` 

[License](https://github.com/vijayendrashrimant/DataCleanPRO/blob/main/LICENSE) [GitHub](https://github.com/vijayendrashrimant/DataCleanPRO)