$pyPaths = @(
    'C:\Program Files\Python*\python.exe',
    'C:\Program Files (x86)\Python*\python.exe',
    'C:\Users\marku\AppData\Local\Programs\Python\Python*\python.exe'
)

foreach ($pattern in $pyPaths) {
    $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
    if ($found) {
        Write-Output $found
        break
    }
}
