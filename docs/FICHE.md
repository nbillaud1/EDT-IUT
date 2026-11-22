# Fiche projet : Salles libres IUT

Statut : validée le 2026-11-22 par l'utilisateur · Dernière modification : 2026-11-22
Une page, en mots simples. Rien n'est construit avant validation.

## 1. Pourquoi
- Objectif : savoir en quelques secondes, depuis son téléphone, quelles salles du département info sont libres sur un créneau précis de la semaine en cours, d'après les PDF d'EDT A1, A2, A3.
- Pour qui : moi + quelques amis (lien partagé)
- Critères de réussite :
  - j'ouvre le lien sur mon téléphone et j'ai la liste des salles libres pour « maintenant » en moins de 5 s ;
  - les salles libres affichées sont justes sur 3 créneaux vérifiés à la main dans les PDF ;
  - la semaine affichée est la semaine actuelle sans rien faire ;
  - coût 0 €.

## 2. Quoi
- Forme et plateforme : site web en ligne, pensé pour mobile (marche aussi sur PC)
- Fonctions MVP :
  - choisir jour + heure de début + heure de fin → liste des salles libres sur tout le créneau ;
  - bouton « Maintenant » (aujourd'hui, heure actuelle → +1 h 30) ;
  - pour chaque salle libre : « libre jusqu'à HHhMM ».
- Ajouté le 2026-11-22 à ta demande : changer de semaine (‹ ›, « Maintenant » revient à la semaine en cours)
- Plus tard : vue grille salles × heures
- Hors périmètre : réserver une salle ; EDT des autres départements ; comptes utilisateurs

## 3. Comment
- Techs principales : script Python (lecture des PDF) lancé automatiquement par GitHub Actions (ex. toutes les 2 h) qui écrit un fichier de données ; page statique HTML/CSS/JS servie par GitHub Pages · pourquoi : gratuit, rapide sur mobile, rien à faire tourner chez toi · prix à payer : dépôt public, données rafraîchies par intervalle · écartés : serveur Python Render (s'endort), Cloudflare Worker (PDF en JS délicat)
- Données : PDF publics de edt-iut-info.unilim.fr ; rien de personnel (les initiales des profs ne sont pas affichées sur le site)
- Style visuel : sombre, tableau d'affichage de salles — fond encre #0E1A2B, zones #17263B, texte craie #EDE6D6, libre #7BD88F, heures ambre #F2B33D ; Barlow Condensed + Barlow ; heures par demi-heure (ajusté le 2026-11-22 à ta demande, à confirmer avec la maquette)
- Contraintes : budget 0 € ; mobile d'abord ; limite assumée : une salle absente des EDT info (autre département, événement) peut être occupée sans qu'on le sache

## 4. Décisions
| Sujet | Choix | Décidé par toi le… |
|---|---|---|
| Forme | site en ligne, mobile | 2026-11-22 |
| Public | toi + quelques amis | 2026-11-22 |
| Fonctions MVP | créneau → salles, « Maintenant », « libre jusqu'à » | 2026-11-22 |
| Mise en page | formulaire en haut + cartes de salles | 2026-11-22 |
| Hébergement | GitHub Pages + Actions (compte GitHub existant) | 2026-11-22 |
| Style | sombre | 2026-11-22 |
| Liste des salles | toutes les salles vues dans les 39 PDF | hypothèse à confirmer (sûr) |
| Fréquence de mise à jour | toutes les 2 h | hypothèse à confirmer (probable) |

Modifications après validation : 2026-11-22, style retravaillé (moins générique) et heures par pas de 30 min, à ta demande pendant la maquette ; 2026-11-22, ajout du changement de semaine et dépôt nommé « EDT-IUT », à ta demande

## 5. Suite
- Prochaine étape et coût : maquette HTML cliquable faite par moi (pas d'agent), données fictives
- Maquette validée : `maquette/index.html` (artifact https://claude.ai/artifact/3s5maRh3rHuDUjiaLJAjZS, version 5), validée le 2026-11-22
- Outils vus au cadrage : navigateur intégré, Artifact (privé), questions à boutons avec aperçu ; MCP Figma (non authentifié, inutile ici)
- Constats techniques (vérifiés le 2026-11-22) :
  - 13 PDF par promo (`A1_S1.pdf` … `A1_S13.pdf`) ; l'en-tête donne les dates (« Semaine 13 (49) : du 30/11/2026 au 05/12/2026 ») → semaine actuelle trouvée automatiquement.
  - Chaque cours = « Module - Prof - Salle » (ex. `R1.01 - LD - 104`) ; salle parfois « . » (inconnue).
  - Salles vues dans 2 PDF : 103, 104, 105, 108, 109, 111, 112, 205, 208, 209, R46, R50, R52, AC.
  - Pas d'en-tête CORS sur le site → lecture des PDF côté script, pas dans la page.
  - Risque principal : retrouver l'heure de chaque cours à partir de sa position dans le PDF (à valider au jalon 1).
- Mise en ligne (push GitHub, activation Pages) : uniquement avec ton accord explicite.
- Questions ouvertes : aucune
