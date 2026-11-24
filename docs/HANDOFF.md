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

## 2026-11-24 : nouvelle mise en page des PDF (« régénéré à partir des ICS »)
- Cassait la lecture sans erreur (13 salles au lieu de 16) : textes placés par BT/Td, page tournée par cm, une seule bande pour les jours, CM sur 3 lignes (Module - Intitulé / Prof / Salle).
- Corrigé dans `tools/edt.py` (les deux mises en page sont lues) ; contrôles stricts : texte hors case, jour introuvable, horaire hors 8h-19h30 -> erreur, rien n'est écrit ni publié.
- Test : `tests/fixtures/A2_S13_ics.pdf` ajouté. Vérifié à l'œil : A1 S13, A2 S13, A3 S12.

## Suite
1. (fait 2026-11-22, accord utilisateur) Tâche planifiée Windows « EDT-IUT mise a jour » : `tools/maj.ps1` chaque jour à 7h30 et 12h30 (rattrapée si PC éteint), fin le 2027-06-30, auto-suppression le lendemain. Le site reste en ligne après. Journal : `tools/maj.log`. Essai manuel : résultat 0, « aucun changement ». Cron GitHub retiré (inutile).
2. Vérifier « Maintenant » un jour de cours ; rendu sur vrai téléphone.

## Agents lancés
| Agent | Tâche | État |
|---|---|---|
| — | — | — |
