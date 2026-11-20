# Preview by default. Pass --apply to write the selected skills.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$runtime = $null
$pythonArgs = @()
foreach ($candidate in @('py', 'python', 'python3')) {
    $app = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $app) { continue }
    $prefix = @()
    if ($candidate -eq 'py') { $prefix = @('-3') }
    & $app.Source @prefix -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>$null
    if ($LASTEXITCODE -eq 0) {
        $runtime = $app.Source
        $pythonArgs = $prefix
        break
    }
}
if (-not $runtime) { throw 'MSSHI requires Python 3.10 or newer.' }
& $runtime @pythonArgs -B -X utf8 (Join-Path $repoRoot 'scripts\install_msshi.py') --mode selective --packs business @args
exit $LASTEXITCODE
