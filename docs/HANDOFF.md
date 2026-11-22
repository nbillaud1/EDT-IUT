# HANDOFF — Salles libres IUT

Mis à jour : 2026-11-22

## État
- Taille : Petite, sans agent. Parcours : Cadrage ✔ → Maquette ✔ (2026-11-22) → Construction ✔ (2026-11-22) → Essai ✔ → Livraison ✔ (2026-11-22).
- Fiche validée le 2026-11-22 : `docs/FICHE.md`.
- Maquette v2 (tableau d'affichage, pas de 30 min) : `maquette/index.html`, artifact privé https://claude.ai/artifact/3s5maRh3rHuDUjiaLJAjZS

## Fait le 2026-11-22
- `tools/edt.py` : lit les 39 PDF (géométrie : 75 unités par demi-heure dès 8h, rectangles colorés = cours), écrit `site/data.json` (toutes les semaines ; la page choisit la semaine du jour, heure de Paris). Salles jumelées « 104-5 » séparées ; « . » et codes inconnus (« 03-12 ») comptés à part.
- `tests/test_edt.py` sur `tests/fixtures/A1_S13.pdf` : ok. A2 semaine 12 vérifiée à l'œil sur le PDF (lundi, mardi, mercredi, jeudi) : identique.
- `site/index.html` : page réelle (style de la maquette), testée en local (`.claude/launch.json`, port 8765) : lundi 10h-12h = 7 libres, identique au recalcul Python.
- `.github/workflows/pages.yml` : toutes les 2 h + à chaque push, test puis génération puis déploiement Pages.

## En ligne (2026-11-22)
- Dépôt public https://github.com/nbillaud1/EDT-IUT, site https://nbillaud1.github.io/EDT-IUT/ (vérifié en format mobile).
- Changement de semaine ajouté (‹ ›).
- Le serveur edt-iut-info.unilim.fr ne répond pas aux machines de GitHub (délai dépassé, 2 essais) : le workflow garde `site/data.json` du dépôt. Mise à jour depuis le PC : `powershell -File tools\maj.ps1` (relit, commit, push).
- Workflow en 2 jobs (build, deploy) : le déploiement en un seul job ne trouvait pas l'artefact.

## Suite
1. Décision utilisateur : automatiser `tools/maj.ps1` (tâche planifiée Windows) ou le lancer à la main.
2. Vérifier « Maintenant » un jour de cours ; rendu sur vrai téléphone.

## Agents lancés
| Agent | Tâche | État |
|---|---|---|
| — | — | — |
