[CmdletBinding()]
param(
    [string]$SourcePath,
    [switch]$NoSetup,
    [switch]$NoPath,
    [switch]$DownloadPdf,
    [switch]$NoPdf,
    [string]$PdfVersion,
    [string]$PdfDest,
    [string]$Mode,
    [string]$Platform,
    [string]$DefaultBot,
    [string]$AcademicProject,
    [string]$AcademicLevel,
    [string]$AcademicTopic,
    [string]$AcademicDeadline,
    [string]$AcademicCampusGuideline,
    [string]$PreferredName,
    [switch]$Yes,
    [string]$KatMode,
    [switch]$StageAutoTrim,
    [switch]$InstallSteel, # Deprecated compatibility input; no browser/plugin is installed.
    [string]$ConnectServices, # Deprecated compatibility input; no automatic service setup.
    [ValidateSet('chrome', 'edge', 'firefox', 'none')]
    [string]$Browser,
    [string]$BrowserProfileLabel,
    [string]$BrowserAccountLabel,
    [string]$ConnectApps,
    [string]$ConnectBots,
    [string]$ConnectTargets,
    [switch]$WithRea,
    [switch]$Light,
    [switch]$LowRam,
    [ValidateSet('auto', 'light', 'normal')]
    [string]$ResourceProfile,
    [string]$InstallDir,
    [string]$HermesHome,
    [string]$TargetDir
)

& {
    param($MsshiSourcePath, $MsshiNoSetup, $MsshiNoPath, $MsshiDownloadPdf, $MsshiNoPdf, $MsshiPdfVersion, $MsshiPdfDest, $MsshiMode, $MsshiPlatform, $MsshiDefaultBot, $MsshiAcademicProject, $MsshiAcademicLevel, $MsshiAcademicTopic, $MsshiAcademicDeadline, $MsshiAcademicCampusGuideline, $MsshiPreferredName, $MsshiYes, $MsshiKatMode, $MsshiStageAutoTrim, $MsshiInstallSteel, $MsshiConnectServices, $MsshiBrowser, $MsshiBrowserProfileLabel, $MsshiBrowserAccountLabel, $MsshiConnectApps, $MsshiConnectBots, $MsshiConnectTargets, $MsshiWithRea, $MsshiLight, $MsshiLowRam, $MsshiResourceProfile, $MsshiInstallDir, $MsshiHermesHome, $MsshiTargetDir)
    $ErrorActionPreference = 'Stop'
    $repository = 'https://github.com/zidanaisar624/MSSHI-Mega-Semar-Sang-Hyang-Ismaya.git'
    $scratch = $null
    $runtime = $null
    $pythonArgs = @()

    # Interactive selection: Light Mode (Win10 RAM 4 GB) & custom install directory (any drive C:/D:/E:/...)
    $isInteractive = (-not $MsshiYes) -and (-not $MsshiNoSetup) -and (-not [Console]::IsInputRedirected)
    if ($isInteractive) {
        if (-not $MsshiLight -and -not $MsshiLowRam -and -not $MsshiResourceProfile) {
            $ramGib = 0.0
            try {
                $cs = Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction Stop
                if ($cs -and $cs.TotalPhysicalMemory) {
                    $ramGib = [Math]::Round(($cs.TotalPhysicalMemory / 1GB), 2)
                }
            } catch {
                $ramGib = 0.0
            }
            $defaultEdition = '1'
            if ($ramGib -gt 0 -and $ramGib -le 6.0) { $defaultEdition = '2' }
            Write-Host ''
            Write-Host '=== Pilihan Mode Instalasi MSSHI ==='
            if ($ramGib -gt 0) { Write-Host ("RAM sistem terdeteksi : $ramGib GiB") }
            Write-Host '  1. Standar / Lengkap (Full Build - semua fitur & paralelisme)'
            Write-Host '  2. Mode Hemat Windows 10 RAM 4 GB (Light Build <= 50 MB + Low-RAM <= 150 MB)'
            $edPick = (Read-Host "Pilih mode instalasi [1/2, Enter=$defaultEdition]").Trim()
            if (-not $edPick) { $edPick = $defaultEdition }
            if ($edPick -eq '2') {
                $MsshiLight = $true
                $MsshiLowRam = $true
            } elseif ($edPick -ne '1') {
                throw 'Pilihan mode instalasi harus 1 atau 2.'
            }
        }
        if (-not $MsshiInstallDir) {
            $defaultInstall = $env:MSSHI_HOME
            if (-not $defaultInstall) { $defaultInstall = Join-Path $env:LOCALAPPDATA 'MSSHI' }
            $driveList = @()
            try {
                foreach ($drv in [System.IO.DriveInfo]::GetDrives()) {
                    if ($drv.IsReady -and ($drv.DriveType -eq 'Fixed' -or $drv.DriveType -eq 'Removable')) {
                        $freeGb = [Math]::Round(($drv.AvailableFreeSpace / 1GB), 1)
                        $driveList += ($drv.Name + " (" + $freeGb + " GB bebas)")
                    }
                }
            } catch {
                $driveList = @()
            }
            Write-Host ''
            if ($driveList.Count -gt 0) {
                Write-Host ('Drive tersedia        : ' + ($driveList -join ', '))
            }
            $pickedDir = (Read-Host "Folder instalasi MSSHI (bebas drive C:/D:/E:/folder mana saja) [$defaultInstall]").Trim()
            if ($pickedDir) { $MsshiInstallDir = $pickedDir }
        }
        if (-not $MsshiHermesHome -and -not $env:HERMES_HOME) {
            $pickedHermes = (Read-Host 'Folder data Hermes / HERMES_HOME (Enter=otomatis adaptif, atau ketik bebas misal E:\HermesData)').Trim()
            if ($pickedHermes) { $MsshiHermesHome = $pickedHermes }
        }
    }

    if ($MsshiInstallDir) {
        if ($MsshiInstallDir.StartsWith('\\') -or -not [IO.Path]::IsPathRooted($MsshiInstallDir)) {
            throw 'InstallDir harus berupa path lokal absolut (misal C:\MSSHI, D:\MSSHI, atau E:\MSSHI).'
        }
        $env:MSSHI_HOME = $MsshiInstallDir
    }
    if ($MsshiHermesHome) {
        if ($MsshiHermesHome.StartsWith('\\') -or -not [IO.Path]::IsPathRooted($MsshiHermesHome)) {
            throw 'HermesHome harus berupa path lokal absolut (misal C:\HermesData, D:\HermesData, atau E:\HermesData).'
        }
        $env:HERMES_HOME = $MsshiHermesHome
    }
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
                if ($MsshiLight) {
                    $sparseOk = $false
                    & $git.Source -c core.longpaths=true -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= clone '--template=' --depth 1 --filter=blob:none --no-tags --no-checkout --sparse --branch main -- $repository $source 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        & $git.Source -C $source sparse-checkout set --no-cone '/scripts/' '/configs/' '/skills/' '/hermes_plugins/' '/templates/' '/business-sage/' '/docs/manuals/pdf_catalog.json' '/optional/manifest.json' '/VERSION.json' '/CHANGELOG.md' '/LICENSE' '/CREDITS.md' '/THIRD_PARTY_NOTICES.md' '/SKILL.md' '/INSTALL_FOR_AGENTS.md' '/package.json' '/install.ps1' '/install.sh' '/MULAI_DI_SINI_PEMULA.bat' '/MULAI_SKRIPSI_DRAG_AND_DROP.bat' '/UPDATE_OTOMATIS_KE_V3.bat' 2>$null
                        if ($LASTEXITCODE -eq 0) {
                            & $git.Source -C $source checkout --quiet HEAD 2>$null
                            if ($LASTEXITCODE -eq 0) { $sparseOk = $true }
                        }
                    }
                    if (-not $sparseOk) {
                        if (Test-Path -LiteralPath $source) { Remove-Item -LiteralPath $source -Recurse -Force }
                        & $git.Source -c core.longpaths=true -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= clone '--template=' --depth 1 --no-tags --branch main -- $repository $source
                    }
                } else {
                    & $git.Source -c core.longpaths=true -c protocol.allow=never -c protocol.https.allow=always -c credential.helper= clone '--template=' --depth 1 --no-tags --branch main -- $repository $source
                }
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
        if ($MsshiLight) { $bootArgs += '--light' }
        if ($MsshiNoPdf -or ($MsshiLight -and -not $MsshiDownloadPdf)) { $bootArgs += '--no-pdf' }
        if ($MsshiPdfVersion) { $bootArgs += @('--pdf-version', $MsshiPdfVersion) }
        if ($MsshiPdfDest) { $bootArgs += @('--pdf-dest', $MsshiPdfDest) }
        & $runtime @pythonArgs -B -X utf8 $cli @bootArgs
        if ($LASTEXITCODE -ne 0) { throw 'MSSHI bootstrap failed.' }
        $dataDir = $env:MSSHI_HOME
        if (-not $dataDir) { $dataDir = Join-Path $env:LOCALAPPDATA 'MSSHI' }
        $binDir = Join-Path $dataDir 'bin'
        if (-not $MsshiNoPath -and ($env:Path -split ';') -notcontains $binDir) {
            $env:Path = "$binDir;$env:Path"
        }
        $setupArgs = @('setup')
        if ($MsshiMode) { $setupArgs += @('--mode', $MsshiMode) }
        if ($MsshiAcademicProject) { $setupArgs += @('--academic-project', $MsshiAcademicProject) }
        if ($MsshiAcademicLevel) { $setupArgs += @('--academic-level', $MsshiAcademicLevel) }
        if ($MsshiAcademicTopic) { $setupArgs += @('--academic-topic', $MsshiAcademicTopic) }
        if ($MsshiAcademicDeadline) { $setupArgs += @('--academic-deadline', $MsshiAcademicDeadline) }
        if ($MsshiAcademicCampusGuideline) { $setupArgs += @('--academic-campus-guideline', $MsshiAcademicCampusGuideline) }
        if ($MsshiPreferredName) { $setupArgs += @('--preferred-name', $MsshiPreferredName) }
        if ($MsshiPlatform) { $setupArgs += @('--platform', $MsshiPlatform) }
        if ($MsshiTargetDir) { $setupArgs += @('--target-dir', $MsshiTargetDir) }
        if ($MsshiDefaultBot) { $setupArgs += @('--default-bot', $MsshiDefaultBot) }
        if ($MsshiYes) { $setupArgs += '--yes' }
        if ($MsshiKatMode) { $setupArgs += @('--kat-mode', $MsshiKatMode) }
        if ($MsshiStageAutoTrim) { $setupArgs += '--stage-auto-trim' }
        if ($MsshiInstallSteel) { $setupArgs += '--install-steel' }
        if ($MsshiConnectServices) { $setupArgs += @('--connect-services', $MsshiConnectServices) }
        if ($MsshiBrowser) { $setupArgs += @('--browser', $MsshiBrowser) }
        if ($MsshiBrowserProfileLabel) { $setupArgs += @('--browser-profile-label', $MsshiBrowserProfileLabel) }
        if ($MsshiBrowserAccountLabel) { $setupArgs += @('--browser-account-label', $MsshiBrowserAccountLabel) }
        if ($MsshiConnectApps) { $setupArgs += @('--connect-apps', $MsshiConnectApps) }
        if ($MsshiConnectBots) { $setupArgs += @('--connect-bots', $MsshiConnectBots) }
        if ($MsshiConnectTargets) { $setupArgs += @('--connect-targets', $MsshiConnectTargets) }
        if ($MsshiWithRea) { $setupArgs += '--with-rea' }
        if ($MsshiLowRam) { $setupArgs += '--low-ram' }
        if ($MsshiResourceProfile) { $setupArgs += @('--resource-profile', $MsshiResourceProfile) }
        if ($MsshiDownloadPdf) { $setupArgs += '--download-pdf' }
        if ($MsshiNoPdf -or ($MsshiLight -and -not $MsshiDownloadPdf)) { $setupArgs += '--no-pdf' }
        if ($MsshiPdfVersion) { $setupArgs += @('--pdf-version', $MsshiPdfVersion) }
        if ($MsshiPdfDest) { $setupArgs += @('--pdf-dest', $MsshiPdfDest) }
        if (-not $MsshiNoSetup -and ($MsshiYes -or -not [Console]::IsInputRedirected)) {
            & $runtime @pythonArgs -B -X utf8 $cli @setupArgs
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
} $SourcePath $NoSetup $NoPath $DownloadPdf $NoPdf $PdfVersion $PdfDest $Mode $Platform $DefaultBot $AcademicProject $AcademicLevel $AcademicTopic $AcademicDeadline $AcademicCampusGuideline $PreferredName $Yes $KatMode $StageAutoTrim $InstallSteel $ConnectServices $Browser $BrowserProfileLabel $BrowserAccountLabel $ConnectApps $ConnectBots $ConnectTargets $WithRea $Light $LowRam $ResourceProfile $InstallDir $HermesHome $TargetDir
