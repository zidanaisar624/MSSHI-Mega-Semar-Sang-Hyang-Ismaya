# Public, two-host installer. Preview both destinations before applying.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$installer = Join-Path $repoRoot 'scripts\install_msshi.py'
$bridge = Join-Path $repoRoot 'scripts\setup_cli_anything_hermes.py'
$python = $null
$pythonPrefix = @()
foreach ($candidate in @('py', 'python', 'python3')) {
    $command = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $command) { continue }
    $prefix = @()
    if ($candidate -eq 'py') { $prefix = @('-3') }
    & $command.Source @prefix -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>$null
    if ($LASTEXITCODE -eq 0) {
        $python = $command.Source
        $pythonPrefix = $prefix
        break
    }
}
if (-not $python) { throw 'MSSHI memerlukan Python 3.10 atau lebih baru.' }

# Preserve the raw Python options accepted by older versions of this script.
if ($args.Count -and $args[0] -like '--*') {
    & $python @pythonPrefix -B -X utf8 $installer @args
    exit $LASTEXITCODE
}

$bothHosts = {
    [CmdletBinding()]
    param(
        [switch]$Apply,
        [string]$HermesHome,
        [string]$AntigravitySkills,
        [ValidateSet('solo', 'selective')][string]$Mode = 'solo',
        [string[]]$Packs,
        [ValidateSet('none', 'auto-reconnect', 'select')][string]$ConnectMode = 'none',
        [string[]]$Targets
    )

    if ($Mode -eq 'selective' -and -not $Packs) { throw 'Mode selective memerlukan -Packs.' }
    if ($Mode -eq 'solo' -and $Packs) { throw '-Packs hanya untuk mode selective.' }
    if ($ConnectMode -eq 'select' -and -not $Targets) { throw 'Gunakan -Targets atau pilih dari menu msshi connect.' }
    if ($ConnectMode -ne 'select' -and $Targets) { throw '-Targets hanya untuk -ConnectMode select.' }

    $common = @('--mode', $Mode)
    if ($Packs) { $common += @('--packs', ($Packs -join ',')) }
    $hermesArgs = @('--platform', 'hermes') + $common
    if ($HermesHome) { $hermesArgs += @('--target-dir', (Join-Path $HermesHome 'skills')) }
    $antigravityArgs = @('--platform', 'antigravity') + $common
    if ($AntigravitySkills) { $antigravityArgs += @('--target-dir', $AntigravitySkills) }
    $connectionArgs = @('--mode', $ConnectMode)
    if ($HermesHome) { $connectionArgs += @('--hermes-home', $HermesHome) }
    if ($Targets) { $connectionArgs += @('--targets', ($Targets -join ',')) }

    function Invoke-MsshiStep {
        param([string]$Entry, [string[]]$Arguments)
        & $python @pythonPrefix -B -X utf8 $Entry @Arguments
        if ($LASTEXITCODE -ne 0) { throw "Langkah MSSHI gagal dengan kode $LASTEXITCODE." }
    }

    Invoke-MsshiStep -Entry $installer -Arguments ($hermesArgs + '--dry-run')
    Invoke-MsshiStep -Entry $installer -Arguments ($antigravityArgs + '--dry-run')
    if ($ConnectMode -ne 'none') {
        Invoke-MsshiStep -Entry $bridge -Arguments ($connectionArgs + '--dry-run')
    }
    if (-not $Apply) {
        Write-Host 'Pratinjau selesai. Tambahkan -Apply untuk menyiapkan kedua host.'
        exit 0
    }

    Invoke-MsshiStep -Entry $installer -Arguments ($hermesArgs + '--apply')
    Invoke-MsshiStep -Entry $installer -Arguments ($antigravityArgs + '--apply')
    if ($ConnectMode -ne 'none') { Invoke-MsshiStep -Entry $bridge -Arguments $connectionArgs }
}

$options = @('-HermesHome', '-AntigravitySkills', '-Mode', '-Packs', '-ConnectMode', '-Targets')
$named = @{}
for ($i = 0; $i -lt $args.Count; $i++) {
    $token = [string]$args[$i]
    $option = $token.TrimEnd(':')
    if ($option -eq '-Apply') {
        if ($token.EndsWith(':')) {
            $i++
            if ($i -ge $args.Count -or $args[$i] -isnot [bool]) { throw '-Apply perlu nilai boolean.' }
            $named['Apply'] = $args[$i]
        } else {
            $named['Apply'] = $true
        }
        continue
    }
    if ($option -notin $options) {
        throw "Opsi tidak dikenal: $option"
    }
    $i++
    if ($i -ge $args.Count) { throw "$option perlu nilai." }
    $named[$option.Substring(1)] = $args[$i]
}
& $bothHosts @named
