# Salles libres IUT

Site mobile qui liste les salles libres du département info (IUT Limousin) sur un créneau de la semaine en cours, d'après les PDF https://edt-iut-info.unilim.fr/edt/A1|A2|A3/.
Fiche validée : `docs/FICHE.md` (2026-11-22). Maquette de référence : `maquette/index.html` (validée le 2026-11-22).

## Décisions (utilisateur, 2026-11-22)
- Site en ligne, mobile d'abord, pour l'utilisateur + quelques amis
- MVP : créneau → salles libres, bouton « Maintenant », « libre jusqu'à »
- Python (lecture PDF) via GitHub Actions toutes les 2 h → JSON ; page statique sur GitHub Pages
- Style sombre : #0F172A / #1E293B / #E2E8F0 / libre #4ADE80 / occupé #475569 / accent #38BDF8
- Mise en ligne uniquement avec accord explicite

## Décisions déléguées
- (aucune pour l'instant)
