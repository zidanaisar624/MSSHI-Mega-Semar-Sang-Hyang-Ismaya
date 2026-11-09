# Compatibility entry point for the MSSHI public installer. Preview is the default.
& python (Join-Path $PSScriptRoot 'scripts/install_msshi.py') @args
exit $LASTEXITCODE
