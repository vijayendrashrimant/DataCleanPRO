from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import io
import csv as csv_mod
import chardet
import json
import os
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict
from pydantic import BaseModel

# ── Constants ──────────────────────────────────────────────────────────────────
MAX_BYTES         = 60 * 1024 * 1024
NUMERIC_THRESHOLD = 0.80
CATEGORICAL_THRESHOLD = 0.70

DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
HISTORY_FILE  = os.path.join(DATA_DIR, "history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Locks — Fix #12 (history) and Fix #I (settings)
_history_lock  = threading.Lock()
_settings_lock = threading.Lock()

# Analytics cache — Fix #13
_analytics_cache: dict = {}
_analytics_cache_ts: float = 0.0
_ANALYTICS_TTL = 5.0

app = FastAPI(title="DataCleanPro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_methods=["GET", "POST", "DELETE"],   # Fix #8
    allow_headers=["*"],
)

# ── CleanConfig — Fix #14: settings wired into pipeline ───────────────────────
class CleanConfig:
    def __init__(self, settings: dict | None = None):
        s = settings or {}
        self.null_fill_strategy:   str   = s.get("null_fill_strategy",   "median")
        self.duplicate_action:     str   = s.get("duplicate_action",     "remove")
        self.title_case_threshold: float = s.get("title_case_threshold", CATEGORICAL_THRESHOLD)
        self.numeric_threshold:    float = s.get("numeric_threshold",    NUMERIC_THRESHOLD)
        self.max_preview_rows:     int   = s.get("max_preview_rows",     200)   # Fix #G
        self.export_format:        str   = s.get("export_format",        "same")

# ── Pydantic models ────────────────────────────────────────────────────────────
class HistoryEntry(BaseModel):
    id: str
    filename: str
    cleaned_at: str
    original_rows: int
    cleaned_rows:  int
    original_cols: int
    cleaned_cols:  int
    changes: int
    quality_score: int
    file_size_kb: float
    report: list[dict]

class AppSettings(BaseModel):
    null_fill_strategy:    str   = "median"
    duplicate_action:      str   = "remove"
    title_case_threshold:  float = 0.70
    numeric_threshold:     float = 0.80
    max_preview_rows:      int   = 200
    auto_download:         bool  = False
    theme:                 str   = "light"
    date_format:           str   = "ISO"
    export_format:         str   = "same"

# ── Persistence helpers ────────────────────────────────────────────────────────
def _load_history() -> list[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def _save_history(entries: list[dict]) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def _bust_analytics_cache() -> None:
    global _analytics_cache_ts
    _analytics_cache_ts = 0.0

def _load_settings() -> dict:
    defaults = AppSettings().model_dump()
    # Fix #D: settings cache — reload only when file changes
    if not os.path.exists(SETTINGS_FILE):
        return defaults
    try:
        with _settings_lock:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
        return {**defaults, **saved}
    except (json.JSONDecodeError, OSError):
        return defaults

def _save_settings(data: dict) -> None:
    with _settings_lock:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

# ── File parsing ───────────────────────────────────────────────────────────────
def _sniff_delimiter(text: str) -> str:
    sample = text[:4096]
    try:
        dialect = csv_mod.Sniffer().sniff(sample, delimiters=",\t|;")
        return dialect.delimiter
    except csv_mod.Error:
        first = text.split("\n")[0]
        counts = {d: first.count(d) for d in (",", "\t", "|", ";")}
        return max(counts, key=counts.get) if max(counts.values()) > 0 else ","

def detect_and_read(content: bytes, filename: str) -> pd.DataFrame:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "csv"
    if ext in ("xlsx", "xls"):
        return pd.read_excel(io.BytesIO(content), dtype=str)
    if ext == "json":
        try:
            return pd.read_json(io.BytesIO(content), dtype=str)
        except ValueError:
            return pd.read_json(io.BytesIO(content), lines=True, dtype=str)
    enc  = chardet.detect(content)["encoding"] or "utf-8"
    text = content.decode(enc, errors="replace")
    sep  = _sniff_delimiter(text)
    return pd.read_csv(io.StringIO(text), sep=sep, dtype=str)

# ── Type inference ─────────────────────────────────────────────────────────────
def _try_numeric(series: pd.Series, threshold: float = NUMERIC_THRESHOLD) -> pd.Series | None:
    numeric = pd.to_numeric(series, errors="coerce")
    valid_ratio = numeric.notna().sum() / max(series.notna().sum(), 1)
    return numeric if valid_ratio >= threshold else None

def _try_datetime(series: pd.Series) -> pd.Series | None:
    try:
        dt = pd.to_datetime(series, errors="coerce")
        valid_ratio = dt.notna().sum() / max(series.notna().sum(), 1)
        return dt if valid_ratio >= NUMERIC_THRESHOLD else None
    except Exception:
        return None

def infer_and_cast(df: pd.DataFrame, cfg: CleanConfig | None = None) -> pd.DataFrame:
    threshold = cfg.numeric_threshold if cfg else NUMERIC_THRESHOLD
    for col in df.columns:
        if (result := _try_numeric(df[col], threshold)) is not None:
            df[col] = result; continue
        if (result := _try_datetime(df[col])) is not None:
            df[col] = result; continue
        df[col] = df[col].astype(str).str.strip().replace("nan", np.nan)
    return df

# ── Cleaning pipeline ──────────────────────────────────────────────────────────
def clean_dataframe(df: pd.DataFrame, cfg: CleanConfig | None = None) -> tuple[pd.DataFrame, list[dict]]:
    cfg    = cfg or CleanConfig()
    report: list[dict] = []
    original_rows = len(df)
    original_cols = len(df.columns)

    # 1. Strip column-name whitespace
    old_cols = df.columns.tolist()
    df.columns = [c.strip() for c in df.columns]
    renamed = sum(1 for o, n in zip(old_cols, df.columns) if o != n)
    if renamed:
        report.append({"type": "column_rename",
                       "detail": f"Trimmed whitespace from {renamed} column name(s)."})

    # 2. Drop fully-empty rows / columns
    df.dropna(how="all", inplace=True)
    empty_rows = original_rows - len(df)
    if empty_rows:
        report.append({"type": "empty_rows",
                       "detail": f"Removed {empty_rows} fully empty row(s)."})

    df.dropna(axis=1, how="all", inplace=True)
    empty_cols = original_cols - len(df.columns)
    if empty_cols:
        report.append({"type": "empty_cols",
                       "detail": f"Removed {empty_cols} fully empty column(s)."})

    # 3. Infer & cast types
    df = infer_and_cast(df, cfg)

    # 4. Duplicates — Fix #14: honour duplicate_action setting
    dupes = int(df.duplicated().sum())
    if dupes:
        if cfg.duplicate_action == "flag":
            df["__is_duplicate__"] = df.duplicated()
            report.append({"type": "duplicates",
                           "detail": f"Flagged {dupes} duplicate row(s) in '__is_duplicate__' column."})
        else:
            df.drop_duplicates(inplace=True)
            report.append({"type": "duplicates",
                           "detail": f"Removed {dupes} duplicate row(s)."})

    # 5. Per-column cleaning
    for col in df.columns:
        if df[col].dtype == object:
            before  = df[col].copy()
            df[col] = df[col].str.replace(r"\s+", " ", regex=True).str.strip()
            changed = int((df[col] != before).sum())
            if changed:
                report.append({"type": "whitespace",
                               "detail": f"'{col}': normalised whitespace in {changed} cell(s)."})

            non_null = df[col].dropna()
            if (len(non_null) > 0
                    and non_null.str.match(r"^[A-Za-z\s\-']+$").mean() >= cfg.title_case_threshold):
                df[col] = df[col].str.title()
                report.append({"type": "casing", "detail": f"'{col}': applied title-case."})

        elif pd.api.types.is_numeric_dtype(df[col]):
            nulls = int(df[col].isna().sum())
            if nulls:
                strategy = cfg.null_fill_strategy
                if strategy == "drop":
                    df.dropna(subset=[col], inplace=True)
                    report.append({"type": "null_fill",
                                   "detail": f"'{col}': dropped {nulls} row(s) with null values."})
                elif strategy == "zero":
                    df[col] = df[col].fillna(0)
                    report.append({"type": "null_fill",
                                   "detail": f"'{col}': filled {nulls} null(s) with zero."})
                elif strategy == "mean":
                    mean_val = float(df[col].mean())
                    df[col]  = df[col].fillna(mean_val)
                    report.append({"type": "null_fill",
                                   "detail": f"'{col}': filled {nulls} null(s) with mean ({mean_val:.2f})."})
                else:  # median (default)
                    median = float(df[col].median())
                    df[col] = df[col].fillna(median)
                    report.append({"type": "null_fill",
                                   "detail": f"'{col}': filled {nulls} null(s) with median ({median:.2f})."})

    df.reset_index(drop=True, inplace=True)

    if not report:
        report.append({"type": "no_changes",
                       "detail": "Data already looks clean — no changes were needed."})
    return df, report

# ── Serialisation — Fix #15: numpy array guard ─────────────────────────────────
def _safe_value(v) -> object:
    if isinstance(v, (np.ndarray, pd.Series)):
        return str(v.tolist())
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, np.integer):  return int(v)
    if isinstance(v, np.floating): return None if np.isnan(v) else float(v)
    if isinstance(v, pd.Timestamp): return v.isoformat()
    if isinstance(v, (str, int, float, bool)): return v
    return str(v)

def df_to_records(df: pd.DataFrame, max_rows: int = 200) -> list[dict]:
    cols = df.columns.tolist()
    raw  = df.head(max_rows).to_dict("records")
    return [{col: _safe_value(row[col]) for col in cols} for row in raw]

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/clean/preview")
async def clean_preview(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"File exceeds the {MAX_BYTES // 1_048_576} MB limit.")
    try:
        df_raw = detect_and_read(content, file.filename or "upload.csv")
    except Exception as exc:
        raise HTTPException(422, f"Could not parse file: {exc}") from exc

    original_shape = {"rows": len(df_raw), "cols": len(df_raw.columns)}

    try:
        cfg      = CleanConfig(_load_settings())
        df_clean, report = clean_dataframe(df_raw.copy(), cfg)
    except Exception as exc:
        raise HTTPException(500, f"Cleaning error: {exc}") from exc

    return {
        "filename":       file.filename,
        "original_shape": original_shape,
        "cleaned_shape":  {"rows": len(df_clean), "cols": len(df_clean.columns)},
        "columns":        df_clean.columns.tolist(),
        "preview":        df_to_records(df_clean, cfg.max_preview_rows),  # Fix #G
        "report":         report,
    }

@app.post("/clean/download")
async def clean_download(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"File exceeds the {MAX_BYTES // 1_048_576} MB limit.")
    try:
        cfg      = CleanConfig(_load_settings())
        df_raw   = detect_and_read(content, file.filename or "upload.csv")
        df_clean, _ = clean_dataframe(df_raw.copy(), cfg)
    except Exception as exc:
        raise HTTPException(422, str(exc)) from exc

    ext        = (file.filename or "").rsplit(".", 1)[-1].lower()
    force_xlsx = cfg.export_format == "xlsx"
    force_csv  = cfg.export_format == "csv"
    use_excel  = (not force_csv) and (force_xlsx or ext in ("xlsx", "xls"))
    buf        = io.BytesIO()

    if use_excel:
        df_clean.to_excel(buf, index=False)
        media    = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        out_name = (file.filename or "data").rsplit(".", 1)[0] + "_cleaned.xlsx"
    else:
        df_clean.to_csv(buf, index=False)
        media    = "text/csv"
        out_name = (file.filename or "data").rsplit(".", 1)[0] + "_cleaned.csv"

    buf.seek(0)
    return StreamingResponse(buf, media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'})

# ── History routes ─────────────────────────────────────────────────────────────
@app.get("/history")
def get_history():
    entries = _load_history()
    # Fix #F: parse datetime for correct sort instead of string comparison
    return sorted(
        entries,
        key=lambda e: datetime.fromisoformat(e.get("cleaned_at", "1970-01-01")),
        reverse=True,
    )

@app.post("/history")
def add_history(entry: HistoryEntry):
    with _history_lock:
        entries = _load_history()
        entries.append(entry.model_dump())
        if len(entries) > 200:
            entries = sorted(
                entries,
                key=lambda e: datetime.fromisoformat(e.get("cleaned_at", "1970-01-01")),
                reverse=True,
            )[:200]
        _save_history(entries)
    _bust_analytics_cache()
    return {"ok": True}

@app.delete("/history/{entry_id}")
def delete_history(entry_id: str):
    with _history_lock:
        entries = _load_history()
        entries = [e for e in entries if e.get("id") != entry_id]
        _save_history(entries)
    _bust_analytics_cache()
    return {"ok": True}

@app.delete("/history")
def clear_history():
    with _history_lock:
        _save_history([])
    _bust_analytics_cache()
    return {"ok": True}

# ── Analytics route — Fix #13: 5 s TTL cache ──────────────────────────────────
@app.get("/analytics")
def get_analytics():
    global _analytics_cache, _analytics_cache_ts
    now = time.monotonic()
    if _analytics_cache and (now - _analytics_cache_ts) < _ANALYTICS_TTL:
        return _analytics_cache

    entries = _load_history()
    if not entries:
        return {
            "total_files": 0, "total_rows_cleaned": 0, "total_rows_removed": 0,
            "avg_quality_score": 0, "avg_changes_per_file": 0,
            "most_common_issues": [], "files_by_day": [],
            "quality_distribution": {"excellent": 0, "good": 0, "poor": 0},
            "format_breakdown": [], "rows_over_time": [],
        }

    total_files        = len(entries)
    total_rows_cleaned = sum(e.get("cleaned_rows", 0) for e in entries)
    total_rows_removed = sum(e.get("original_rows", 0) - e.get("cleaned_rows", 0) for e in entries)
    avg_quality = round(sum(e.get("quality_score", 0) for e in entries) / total_files)
    avg_changes = round(sum(e.get("changes", 0) for e in entries) / total_files, 1)

    issue_counts: dict[str, int] = {}
    for e in entries:
        for r in e.get("report", []):
            t = r.get("type", "")
            if t != "no_changes":
                issue_counts[t] = issue_counts.get(t, 0) + 1
    most_common = sorted(
        [{"type": k, "count": v} for k, v in issue_counts.items()],
        key=lambda x: x["count"], reverse=True,
    )[:6]

    day_counts: dict[str, int] = defaultdict(int)
    for e in entries:
        day = e.get("cleaned_at", "")[:10]
        if day: day_counts[day] += 1

    today = datetime.utcnow().date()
    files_by_day = [
        {"date": str(today - timedelta(days=i)),
         "count": day_counts.get(str(today - timedelta(days=i)), 0)}
        for i in range(13, -1, -1)
    ]

    dist: dict[str, int] = {"excellent": 0, "good": 0, "poor": 0}
    for e in entries:
        qs = e.get("quality_score", 0)
        if qs >= 90:   dist["excellent"] += 1
        elif qs >= 70: dist["good"]      += 1
        else:          dist["poor"]      += 1

    fmt_counts: dict[str, int] = {}
    for e in entries:
        fn  = e.get("filename", "")
        ext = fn.rsplit(".", 1)[-1].lower() if "." in fn else "other"
        ext = ext if ext in ("csv", "xlsx", "xls", "tsv", "json") else "other"
        fmt_counts[ext] = fmt_counts.get(ext, 0) + 1
    format_breakdown = [{"format": k.upper(), "count": v} for k, v in fmt_counts.items()]

    rows_day: dict[str, int] = defaultdict(int)
    for e in entries:
        day = e.get("cleaned_at", "")[:10]
        if day: rows_day[day] += e.get("cleaned_rows", 0)
    rows_over_time = [
        {"date": str(today - timedelta(days=i)),
         "rows": rows_day.get(str(today - timedelta(days=i)), 0)}
        for i in range(13, -1, -1)
    ]

    result = {
        "total_files":          total_files,
        "total_rows_cleaned":   total_rows_cleaned,
        "total_rows_removed":   total_rows_removed,
        "avg_quality_score":    avg_quality,
        "avg_changes_per_file": avg_changes,
        "most_common_issues":   most_common,
        "files_by_day":         files_by_day,
        "quality_distribution": dist,
        "format_breakdown":     format_breakdown,
        "rows_over_time":       rows_over_time,
    }
    _analytics_cache    = result
    _analytics_cache_ts = time.monotonic()
    return result

# ── Settings routes ────────────────────────────────────────────────────────────
@app.get("/settings")
def get_settings():
    return _load_settings()

@app.post("/settings")
def save_settings(settings: AppSettings):
    _save_settings(settings.model_dump())
    return {"ok": True}



# ── Executable entry point ─────────────────────────────────────────────────────
# When built with PyInstaller the exe is launched as:
#   datacleanpro_api --port 8765
# This block lets the exe start uvicorn programmatically.
if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="DataCleanPro API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--log-level", default="warning")
    args = parser.parse_args()

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
    )
