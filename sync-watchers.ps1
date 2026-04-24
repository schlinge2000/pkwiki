# sync-watchers.ps1 - Synchronisiert Scheduled Tasks mit watchers.json
#
# Liest $VAULT_ROOT\watchers.json (oder -WatchersFile) und stellt sicher,
# dass fuer jeden Eintrag ein Scheduled Task 'KnowledgeTree-<name>' existiert
# und den konfigurierten Parametern entspricht. Entfernt Tasks, deren Eintrag
# aus der Config entfernt wurde (schuetzt 'KnowledgeTree-MetaSync' selbst).
#
# Wird von setup.ps1 als Task 'KnowledgeTree-MetaSync' alle 15 Min getriggert,
# damit Aenderungen an watchers.json ohne Neuausfuehrung von setup.ps1 wirken.
#
# Usage:
#   .\sync-watchers.ps1
#   .\sync-watchers.ps1 -WatchersFile C:\pfad\watchers.json

param(
    [string]$WatchersFile = ""
)

$ErrorActionPreference = "Stop"

# Geschuetzter Task-Name — wird nie entfernt (das ist unser eigener Trigger).
$MetaTaskName = "KnowledgeTree-MetaSync"
$TaskPrefix = "KnowledgeTree-"

# -- Config-Pfad ermitteln ---------------------------------------------------

function Resolve-WatchersFile {
    param([string]$Explicit)

    if ($Explicit) { return $Explicit }

    # Versuche $env:VAULT_ROOT (aus .env gesetzt)
    if ($env:VAULT_ROOT -and (Test-Path (Join-Path $env:VAULT_ROOT "watchers.json"))) {
        return Join-Path $env:VAULT_ROOT "watchers.json"
    }

    # .env im Skript-Verzeichnis lesen
    $envFile = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envFile) {
        $vaultLine = (Get-Content $envFile) | Where-Object { $_ -match '^VAULT_ROOT=' } | Select-Object -First 1
        if ($vaultLine) {
            $vault = ($vaultLine -replace '^VAULT_ROOT=', '').Trim().Trim('"')
            $candidate = Join-Path $vault "watchers.json"
            if (Test-Path $candidate) { return $candidate }
        }
    }

    # Fallback: watchers.json neben dem Skript
    $local = Join-Path $PSScriptRoot "watchers.json"
    if (Test-Path $local) { return $local }

    return $null
}

$path = Resolve-WatchersFile -Explicit $WatchersFile
if (-not $path) {
    Write-Host "sync-watchers: keine watchers.json gefunden (VAULT_ROOT gesetzt?)" -ForegroundColor Red
    exit 1
}

Write-Host "sync-watchers: Config = $path"

try {
    $config = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Write-Host "sync-watchers: watchers.json ungueltig: $_" -ForegroundColor Red
    exit 1
}

if (-not $config.watchers) {
    Write-Host "sync-watchers: keine watchers-Eintraege." -ForegroundColor Yellow
    exit 0
}

# -- Soll-Zustand aus Config -------------------------------------------------

$desired = @{}
foreach ($w in $config.watchers) {
    if (-not $w.name) { continue }
    $desired["$TaskPrefix$($w.name)"] = $w
}

# -- Ist-Zustand aus Task Scheduler ------------------------------------------

$existing = @(Get-ScheduledTask -ErrorAction SilentlyContinue |
    Where-Object { $_.TaskName -like "$TaskPrefix*" })

$existingNames = @($existing | ForEach-Object { $_.TaskName })

# -- Register / Update -------------------------------------------------------

foreach ($name in $desired.Keys) {
    $w = $desired[$name]

    $cwd = if ($w.cwd) { $w.cwd } else { $PSScriptRoot }
    $scriptPath = Join-Path $cwd $w.script

    if (-not (Test-Path $scriptPath)) {
        Write-Host "  ! $name : Skript nicht gefunden ($scriptPath)" -ForegroundColor Red
        continue
    }

    $runner = if ($w.runner) { $w.runner } else { "uv" }
    $triggerType = if ($w.trigger) { $w.trigger } else { "interval" }

    $desc = if ($w.description) { $w.description } else { "Knowledge Tree Watcher: $($w.name)" }
    $interval = if ($w.interval_minutes) { $w.interval_minutes } else { 15 }
    $timeout = if ($w.timeout_minutes) { $w.timeout_minutes } else { 30 }

    try {
        # -- Action: runner bestimmt, wie das Skript aufgerufen wird ----------

        switch ($runner) {
            "powershell" {
                $extraArgs = if ($w.args) { " " + ($w.args -join " ") } else { "" }
                $action = New-ScheduledTaskAction `
                    -Execute "powershell.exe" `
                    -Argument "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File `"$scriptPath`"$extraArgs" `
                    -WorkingDirectory $cwd
            }
            default {
                # "uv" (default): uv run <script> <args...>
                $argList = @("run", "`"$scriptPath`"")
                if ($w.args) { $argList += $w.args }
                $action = New-ScheduledTaskAction `
                    -Execute "uv" `
                    -Argument ($argList -join " ") `
                    -WorkingDirectory $cwd
            }
        }

        # -- Trigger + Settings: trigger-Type bestimmt das Takt-Modell --------

        switch ($triggerType) {
            "at_logon" {
                # Langlaufender Daemon, startet beim User-Login.
                $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
                # ExecutionTimeLimit 0 = unbegrenzt
                $settings = New-ScheduledTaskSettingsSet `
                    -MultipleInstances IgnoreNew `
                    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
                    -StartWhenAvailable
                $modeLabel = "at_logon"
            }
            default {
                # "interval": Single-Poll alle N Minuten
                $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
                    -RepetitionInterval (New-TimeSpan -Minutes $interval) `
                    -RepetitionDuration (New-TimeSpan -Days 9999)
                $settings = New-ScheduledTaskSettingsSet `
                    -MultipleInstances IgnoreNew `
                    -ExecutionTimeLimit (New-TimeSpan -Minutes $timeout) `
                    -StartWhenAvailable
                $modeLabel = "alle $interval Min"
            }
        }

        Register-ScheduledTask `
            -TaskName $name `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Description $desc `
            -Force | Out-Null

        if ($existingNames -contains $name) {
            Write-Host "  UPDATE  $name ($modeLabel)" -ForegroundColor DarkCyan
        } else {
            Write-Host "  CREATE  $name ($modeLabel)" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ! $name konnte nicht registriert werden: $_" -ForegroundColor Red
    }
}

# -- Remove obsolete ---------------------------------------------------------

foreach ($task in $existing) {
    $n = $task.TaskName
    if ($n -eq $MetaTaskName) { continue }       # niemals selbst entfernen
    if ($desired.ContainsKey($n)) { continue }   # noch in Config

    try {
        Unregister-ScheduledTask -TaskName $n -Confirm:$false
        Write-Host "  DELETE  $n (nicht mehr in Config)" -ForegroundColor Yellow
    } catch {
        Write-Host "  ! $n konnte nicht entfernt werden: $_" -ForegroundColor Red
    }
}
