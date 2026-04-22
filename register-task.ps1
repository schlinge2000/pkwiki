# Knowledge Wiki — Windows Task Scheduler Registration
# Führt watch.ps1 automatisch beim Windows-Login aus.
#
# Einmalig ausführen (als Admin nicht nötig — Task läuft als aktueller User):
#   powershell -ExecutionPolicy Bypass -File ".\register-task.ps1"
#
# Status prüfen:
#   Get-ScheduledTask -TaskName "KnowledgeWikiWatcher"
#
# Manuell starten/stoppen:
#   Start-ScheduledTask -TaskName "KnowledgeWikiWatcher"
#   Stop-ScheduledTask  -TaskName "KnowledgeWikiWatcher"
#
# Task entfernen:
#   Unregister-ScheduledTask -TaskName "KnowledgeWikiWatcher" -Confirm:$false

$taskName   = "KnowledgeWikiWatcher"
$scriptPath = Join-Path $PSScriptRoot "watch.ps1"
$logPath    = Join-Path $PSScriptRoot "logs\task-scheduler.log"

# Bestehenden Task entfernen falls vorhanden
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Alter Task entfernt."
}

$action  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`"" `
    -WorkingDirectory $PSScriptRoot

# Trigger: beim Login des aktuellen Users
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `  # kein Timeout
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Knowledge Wiki Auto-Ingest Watcher (watch.ps1)" `
    -RunLevel Limited | Out-Null

Write-Host "Task '$taskName' registriert."
Write-Host "Starte Task jetzt..."
Start-ScheduledTask -TaskName $taskName

$state = (Get-ScheduledTask -TaskName $taskName).State
Write-Host "Status: $state"
