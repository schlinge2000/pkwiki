# Knowledge Wiki — Watcher Status Check
# Zeigt Status beider Watcher (Wiki + Tree)
#
# Aufruf: powershell -ExecutionPolicy Bypass -File ".\watcher-status.ps1"

function Show-WatcherStatus {
    param([string]$TaskName, [string]$Label)

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) {
        Write-Host "[$Label]  NICHT REGISTRIERT — register-task.ps1 ausführen" -ForegroundColor Red
        return
    }

    $info = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue
    $state = $task.State
    $lastRun = if ($info.LastRunTime -and $info.LastRunTime -ne [DateTime]::MinValue) {
        $info.LastRunTime.ToString("yyyy-MM-dd HH:mm:ss")
    } else { "—" }
    $lastResult = $info.LastTaskResult

    $color = switch ($state) {
        "Running" { "Green" }
        "Ready"   { "Yellow" }
        default   { "Red" }
    }

    Write-Host "[$Label]  $state  |  Letzter Start: $lastRun  |  Exit: $lastResult" -ForegroundColor $color
}

Write-Host ""
Write-Host "=== Knowledge Watcher Status ===" -ForegroundColor Cyan
Write-Host ""
Show-WatcherStatus "KnowledgeWikiWatcher" "Wiki-Watcher  (watch.ps1)       "
Show-WatcherStatus "KnowledgeTreeWatcher" "Tree-Watcher  (code-watch.py)   "
Write-Host ""
Write-Host "Befehle:" -ForegroundColor DarkGray
Write-Host "  Start:  Start-ScheduledTask -TaskName KnowledgeWikiWatcher" -ForegroundColor DarkGray
Write-Host "  Stop:   Stop-ScheduledTask  -TaskName KnowledgeWikiWatcher" -ForegroundColor DarkGray
Write-Host "  Log:    Get-Content logs\watcher.log -Tail 20" -ForegroundColor DarkGray
