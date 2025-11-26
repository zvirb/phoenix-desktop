$paths = @(
    'C:\Users\marku\Documents\playground',
    'C:\Users\marku\playground',
    'C:\Users\marku\Desktop\playground',
    'C:\Users\marku\Documents\phoenix-playground',
    'C:\Users\marku\Documents\phoenix_playground',
    'C:\Users\marku\Projects\phoenix-tracker'
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host "Found: $p"
    }
}
