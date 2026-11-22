# HANDOFF — Salles libres IUT

Mis à jour : 2026-11-22

## État
- Taille : Petite, sans agent. Parcours : Cadrage ✔ → Maquette ✔ (2026-11-22) → Construction ✔ (2026-11-22) → Essai (local ✔) → Livraison (en attente d'accord pour GitHub).
- Fiche validée le 2026-11-22 : `docs/FICHE.md`.
- Maquette v2 (tableau d'affichage, pas de 30 min) : `maquette/index.html`, artifact privé https://claude.ai/artifact/3s5maRh3rHuDUjiaLJAjZS

## Fait le 2026-11-22
- `tools/edt.py` : lit les 39 PDF (géométrie : 75 unités par demi-heure dès 8h, rectangles colorés = cours), écrit `site/data.json` (toutes les semaines ; la page choisit la semaine du jour, heure de Paris). Salles jumelées « 104-5 » séparées ; « . » et codes inconnus (« 03-12 ») comptés à part.
- `tests/test_edt.py` sur `tests/fixtures/A1_S13.pdf` : ok. A2 semaine 12 vérifiée à l'œil sur le PDF (lundi, mardi, mercredi, jeudi) : identique.
- `site/index.html` : page réelle (style de la maquette), testée en local (`.claude/launch.json`, port 8765) : lundi 10h-12h = 7 libres, identique au recalcul Python.
- `.github/workflows/pages.yml` : toutes les 2 h + à chaque push, test puis génération puis déploiement Pages.

## Suite
1. Accord de l'utilisateur : créer le dépôt GitHub public, pousser, activer Pages (source « GitHub Actions »).
2. Ouvrir le lien sur téléphone, vérifier « Maintenant » un jour de cours.

## Agents lancés
| Agent | Tâche | État |
|---|---|---|
| — | — | — |
