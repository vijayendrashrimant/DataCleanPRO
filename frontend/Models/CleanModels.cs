using System.Text.Json.Serialization;

namespace DataCleanPro.Models;

public class ShapeInfo     { [JsonPropertyName("rows")] public int Rows { get; set; } [JsonPropertyName("cols")] public int Cols { get; set; } }
public class CleanReport   { [JsonPropertyName("type")] public string Type { get; set; } = ""; [JsonPropertyName("detail")] public string Detail { get; set; } = ""; }

public class PreviewResponse
{
    [JsonPropertyName("filename")]       public string   Filename      { get; set; } = "";
    [JsonPropertyName("original_shape")] public ShapeInfo OriginalShape { get; set; } = new();
    [JsonPropertyName("cleaned_shape")]  public ShapeInfo CleanedShape  { get; set; } = new();
    [JsonPropertyName("columns")]        public List<string> Columns    { get; set; } = new();
    [JsonPropertyName("preview")]        public List<Dictionary<string, object?>> Preview { get; set; } = new();
    [JsonPropertyName("report")]         public List<CleanReport> Report { get; set; } = new();
}

public class HistoryEntry
{
    [JsonPropertyName("id")]            public string Id           { get; set; } = "";
    [JsonPropertyName("filename")]      public string Filename     { get; set; } = "";
    [JsonPropertyName("cleaned_at")]    public string CleanedAt    { get; set; } = "";
    [JsonPropertyName("original_rows")] public int    OriginalRows { get; set; }
    [JsonPropertyName("cleaned_rows")]  public int    CleanedRows  { get; set; }
    [JsonPropertyName("original_cols")] public int    OriginalCols { get; set; }
    [JsonPropertyName("cleaned_cols")]  public int    CleanedCols  { get; set; }
    [JsonPropertyName("changes")]       public int    Changes      { get; set; }
    [JsonPropertyName("quality_score")] public int    QualityScore { get; set; }
    [JsonPropertyName("file_size_kb")]  public double FileSizeKb   { get; set; }
    [JsonPropertyName("report")]        public List<CleanReport> Report { get; set; } = new();
}

public class IssueCount  { [JsonPropertyName("type")] public string Type { get; set; } = ""; [JsonPropertyName("count")] public int Count { get; set; } }
public class DayCount    { [JsonPropertyName("date")] public string Date { get; set; } = ""; [JsonPropertyName("count")] public int Count { get; set; } }
public class DayRows     { [JsonPropertyName("date")] public string Date { get; set; } = ""; [JsonPropertyName("rows")] public int Rows { get; set; } }
public class FormatCount { [JsonPropertyName("format")] public string Format { get; set; } = ""; [JsonPropertyName("count")] public int Count { get; set; } }
public class QualityDist { [JsonPropertyName("excellent")] public int Excellent { get; set; } [JsonPropertyName("good")] public int Good { get; set; } [JsonPropertyName("poor")] public int Poor { get; set; } }

public class AnalyticsResponse
{
    [JsonPropertyName("total_files")]          public int    TotalFiles           { get; set; }
    [JsonPropertyName("total_rows_cleaned")]   public int    TotalRowsCleaned     { get; set; }
    [JsonPropertyName("total_rows_removed")]   public int    TotalRowsRemoved     { get; set; }
    [JsonPropertyName("avg_quality_score")]    public int    AvgQualityScore      { get; set; }
    [JsonPropertyName("avg_changes_per_file")] public double AvgChangesPerFile    { get; set; }
    [JsonPropertyName("most_common_issues")]   public List<IssueCount>  MostCommonIssues    { get; set; } = new();
    [JsonPropertyName("files_by_day")]         public List<DayCount>    FilesByDay          { get; set; } = new();
    [JsonPropertyName("quality_distribution")] public QualityDist       QualityDistribution { get; set; } = new();
    [JsonPropertyName("format_breakdown")]     public List<FormatCount> FormatBreakdown     { get; set; } = new();
    [JsonPropertyName("rows_over_time")]       public List<DayRows>     RowsOverTime        { get; set; } = new();
}

public class AppSettings
{
    [JsonPropertyName("null_fill_strategy")]   public string NullFillStrategy   { get; set; } = "median";
    [JsonPropertyName("duplicate_action")]     public string DuplicateAction    { get; set; } = "remove";
    [JsonPropertyName("title_case_threshold")] public double TitleCaseThreshold { get; set; } = 0.70;
    [JsonPropertyName("numeric_threshold")]    public double NumericThreshold   { get; set; } = 0.80;
    [JsonPropertyName("max_preview_rows")]     public int    MaxPreviewRows     { get; set; } = 200;
    [JsonPropertyName("auto_download")]        public bool   AutoDownload       { get; set; } = false;
    [JsonPropertyName("theme")]                public string Theme              { get; set; } = "light";
    [JsonPropertyName("date_format")]          public string DateFormat         { get; set; } = "ISO";
    [JsonPropertyName("export_format")]        public string ExportFormat       { get; set; } = "same";
}
