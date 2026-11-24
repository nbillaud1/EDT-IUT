# Salles libres IUT

Site mobile qui liste les salles libres du département info (IUT Limousin) sur un créneau de la semaine en cours, d'après les PDF https://edt-iut-info.unilim.fr/edt/A1|A2|A3/.
Fiche validée : `docs/FICHE.md` (2026-11-22). Maquette de référence : `maquette/index.html` (validée le 2026-11-22).

## Décisions (utilisateur, 2026-11-22)
- Site en ligne, mobile d'abord, pour l'utilisateur + quelques amis
- MVP : créneau → salles libres, bouton « Maintenant », « libre jusqu'à »
- Python → JSON ; page statique sur GitHub Pages
- Source : calendriers .ics des groupes (G1…G8), PDF en secours (utilisateur, 2026-11-24)
- Les SAE libres restent affichées comme occupées (utilisateur, 2026-11-24)
- Style sombre : #0F172A / #1E293B / #E2E8F0 / libre #4ADE80 / occupé #475569 / accent #38BDF8
- Mise en ligne uniquement avec accord explicite

## Décisions déléguées
- 2026-11-22 : données de secours commitées (`site/data.json`) + `tools/maj.ps1`, car le serveur de l'IUT bloque les machines de GitHub ; workflow en 2 jobs.

## En ligne
- https://github.com/nbillaud1/EDT-IUT · https://nbillaud1.github.io/EDT-IUT/
- Mise à jour : tâche planifiée Windows « EDT-IUT mise a jour » (7h30 et 12h30) jusqu'au 2027-06-30 ; arrêt anticipé : `Unregister-ScheduledTask -TaskName "EDT-IUT mise a jour"`.
