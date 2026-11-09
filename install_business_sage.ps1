# Preview by default. Pass --apply to write the selected skills.
& python (Join-Path $PSScriptRoot 'scripts/install_msshi.py') --mode selective --packs business @args
exit $LASTEXITCODE
