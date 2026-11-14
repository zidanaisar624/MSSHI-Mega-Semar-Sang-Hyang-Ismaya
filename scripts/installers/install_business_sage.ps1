# Preview by default. Pass --apply to write the selected skills.
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
& python (Join-Path $repoRoot 'scripts\install_msshi.py') --mode selective --packs business @args
exit $LASTEXITCODE
