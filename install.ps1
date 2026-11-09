[CmdletBinding()]
param(
    [string]$SourcePath,
    [switch]$NoSetup,
    [switch]$NoPath
)

& {
    param($MsshiSourcePath, $MsshiNoSetup, $MsshiNoPath)
    $ErrorActionPreference = 'Stop'
    $repository = 'https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git'
    $scratch = $null
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

    try {
        if ($MsshiSourcePath) {
            $source = (Resolve-Path -LiteralPath $MsshiSourcePath).ProviderPath
        } else {
            $git = Get-Command git -CommandType Application -ErrorAction Stop | Select-Object -First 1
            $tempBase = (Resolve-Path -LiteralPath ([IO.Path]::GetTempPath())).ProviderPath.TrimEnd('\')
            $scratch = Join-Path $tempBase ("msshi-bootstrap-" + [Guid]::NewGuid().ToString('N'))
            [IO.Directory]::CreateDirectory($scratch) | Out-Null
            $source = Join-Path $scratch 'repo'
            $gitEnv = @{
                GIT_CONFIG_NOSYSTEM = '1'
                GIT_CONFIG_GLOBAL = 'NUL'
                GIT_TERMINAL_PROMPT = '0'
                GIT_LFS_SKIP_SMUDGE = '1'
            }
            $priorEnv = @{}
            try {
                foreach ($key in $gitEnv.Keys) {
                    $priorEnv[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
                    [Environment]::SetEnvironmentVariable($key, $gitEnv[$key], 'Process')
                }
                & $git.Source -c core.longpaths=true -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= clone '--template=' --depth 1 --no-tags --branch main -- $repository $source
            } finally {
                foreach ($key in $priorEnv.Keys) {
                    [Environment]::SetEnvironmentVariable($key, $priorEnv[$key], 'Process')
                }
            }
            if ($LASTEXITCODE -ne 0) { throw 'Could not download MSSHI from GitHub.' }
        }
        $cli = Join-Path $source 'scripts\msshi_cli.py'
        if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) {
            throw 'This source does not contain the Stage 2 CLI yet.'
        }
        $bootArgs = @('bootstrap')
        if ($MsshiNoPath) { $bootArgs += '--no-path' }
        & $runtime @pythonArgs -B -X utf8 $cli @bootArgs
        if ($LASTEXITCODE -ne 0) { throw 'MSSHI bootstrap failed.' }
        $dataDir = $env:MSSHI_HOME
        if (-not $dataDir) { $dataDir = Join-Path $env:LOCALAPPDATA 'MSSHI' }
        $binDir = Join-Path $dataDir 'bin'
        if (-not $MsshiNoPath -and ($env:Path -split ';') -notcontains $binDir) {
            $env:Path = "$binDir;$env:Path"
        }
        if (-not $MsshiNoSetup -and -not [Console]::IsInputRedirected) {
            & $runtime @pythonArgs -B -X utf8 $cli setup
            if ($LASTEXITCODE -ne 0) { throw 'MSSHI setup was interrupted or failed. Run msshi setup again.' }
        } elseif (-not $MsshiNoSetup) {
            Write-Host 'Run msshi setup from an interactive terminal.'
        }
    } finally {
        if ($scratch -and (Test-Path -LiteralPath $scratch -PathType Container)) {
            $resolved = (Resolve-Path -LiteralPath $scratch).ProviderPath
            if ([IO.Path]::GetDirectoryName($resolved) -eq $tempBase -and
                [IO.Path]::GetFileName($resolved) -match '^msshi-bootstrap-[a-f0-9]{32}$') {
                Remove-Item -LiteralPath $resolved -Recurse -Force
            }
        }
    }
} $SourcePath $NoSetup $NoPath
