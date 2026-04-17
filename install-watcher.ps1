# Installiert den KnowledgeWikiWatcher als dauerhaften Task
# Einmalig als Admin ausfuehren: .\install-watcher.ps1

$taskName = "KnowledgeWikiWatcher"
$scriptPath = Join-Path $PSScriptRoot "watch.ps1"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory $PSScriptRoot

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force

Write-Host "Task '$taskName' registriert." -ForegroundColor Green
Write-Host "Startet automatisch beim naechsten Login." -ForegroundColor Cyan
Write-Host ""
Write-Host "Jetzt sofort starten:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
Write-Host ""
Write-Host "Status pruefen:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$taskName' | Select-Object State"
Write-Host ""
Write-Host "Deinstallieren:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
