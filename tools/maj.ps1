# Met à jour les données du site depuis ce PC (le serveur de l'IUT bloque les machines de GitHub).
# Usage : powershell -File tools\maj.ps1   — relit les PDF, puis commit + push de site/data.json s'il a changé.
# Lancé chaque jour par la tâche planifiée « EDT-IUT mise a jour » jusqu'au 30/06/2027 ; journal : tools\maj.log
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
Start-Transcript -Path "tools\maj.log" -Append | Out-Null
try {
    python -I tools/edt.py site
    if ($LASTEXITCODE -ne 0) { throw "Lecture des PDF impossible, rien n'est envoyé." }
    git diff --quiet -- site/data.json
    if ($LASTEXITCODE -eq 0) { Write-Host "Aucun changement dans les emplois du temps."; exit 0 }
    git add site/data.json
    git commit -m "Mise à jour des emplois du temps"
    git push
    if ($LASTEXITCODE -ne 0) { throw "git push a échoué (connexion GitHub ?)." }
    Write-Host "Envoyé : le site sera à jour dans 1 à 2 minutes."
} finally {
    Stop-Transcript | Out-Null
}
