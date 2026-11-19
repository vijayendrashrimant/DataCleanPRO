using DataCleanPro.Services;
using MudBlazor.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();

// Register ServerSideBlazor once with detailed errors enabled
builder.Services.AddServerSideBlazor(options =>
{
    options.DetailedErrors = true;
});

builder.Services.AddMudServices();

// Correctly configure the named HttpClient ("api") pointing to FastAPI
builder.Services.AddHttpClient("api", client =>
{
    client.BaseAddress = new Uri("http://127.0.0.1:8765/");
    client.Timeout = TimeSpan.FromSeconds(120);
});

// Pass "api" to CreateClient so scoped injections use the correct BaseAddress
builder.Services.AddScoped(sp =>
    sp.GetRequiredService<IHttpClientFactory>().CreateClient("api"));

// FastAPI process manager — starts Python on startup, kills it on shutdown
builder.Services.AddSingleton<FastApiService>();
builder.Services.AddHostedService(sp => sp.GetRequiredService<FastApiService>());

var app = builder.Build();

if (!app.Environment.IsDevelopment())
    app.UseExceptionHandler("/Error");

app.UseStaticFiles();
app.UseRouting();

app.MapRazorPages();
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();