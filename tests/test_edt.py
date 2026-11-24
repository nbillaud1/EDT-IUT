"""python -I tests/test_edt.py  — vérifie la lecture de vrais PDF : ancienne mise en page (A1 S13, 2026-11-22)
et nouvelle « régénérée à partir des ICS » (A2 S13, 2026-11-24)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import edt

assert edt.split_rooms("104") == ["104"]
assert edt.split_rooms("104-5") == ["104", "105"]
assert edt.split_rooms("111-2") == ["111", "112"]
assert edt.split_rooms("R50") == ["R50"] and edt.split_rooms("AC") == ["AC"]
assert edt.split_rooms(".") == [None] and edt.split_rooms("03-12") == [None]

w = edt.parse_pdf((Path(__file__).parent / "fixtures" / "A1_S13.pdf").read_bytes())
assert (w["num"], w["start"], w["end"]) == (13, "2026-11-30", "2026-12-05"), w
ev = {(d, s, e, r) for d, s, e, r, _ in w["events"]}
assert len(w["events"]) == 84, len(w["events"])
# Lus à la main dans le PDF : lundi 8h-10h S1.03 en 108, lundi 13h30-15h30 R1.10B en R52, lundi 17h30-19h30 R1.01 en 104.
assert ("LUNDI", 480, 600, "108") in ev
assert ("LUNDI", 810, 930, "R52") in ev
assert ("LUNDI", 1050, 1170, "104") in ev
# Nouvelle mise en page : CM sur 3 lignes (Module - Intitulé / Prof / Salle), créneaux d'1 h 30, page tournée.
w = edt.parse_pdf((Path(__file__).parent / "fixtures" / "A2_S13_ics.pdf").read_bytes())
assert (w["num"], w["start"]) == (13, "2026-11-30"), w
ev = {(d, s, e, r) for d, s, e, r, _ in w["events"]}
assert len(w["events"]) == 29, len(w["events"])
# Lus à la main dans le PDF :
assert ("LUNDI", 600, 720, "R46") in ev          # R3.11 Droit du numérique, salle sur la 3e ligne
assert ("LUNDI", 810, 930, "112") in ev          # S3.01A en 111-2
assert ("JEUDI", 810, 900, "R47") in ev          # R3.10 de 13h30 à 15h00
assert ("JEUDI", 900, 1020, "105") in ev         # R3.14 de 15h00 à 17h00
assert ("MARDI", 480, 600, None) in ev           # R3.04 salle « . »
assert ("VENDREDI", 930, 1050, "111") in ev
# Calendrier .ics (source principale depuis le 2026-11-24) : groupe G7, semaine 12.
w = edt.parse_ics((Path(__file__).parent / "fixtures" / "G7_S12.ics").read_text(encoding="utf-8"), 12)
assert (w["num"], w["start"], w["end"]) == (12, "2026-11-23", "2026-11-28"), w
ev = {(d, s, e, r) for d, s, e, r, _ in w["events"]}
assert len(w["events"]) == 24, len(w["events"])
assert ("MARDI", 810, 1050, "208") in ev        # SAE libre G7A, 13h30-17h30
assert ("MARDI", 540, 630, "AC") in ev          # Anglais 9h00-10h30
assert ("LUNDI", 480, 600, "103") in ev
# Fuseau non prévu -> erreur (rien n'est publié) plutôt qu'un horaire décalé.
try:
    edt.parse_ics("BEGIN:VEVENT\nDTSTART:20261123T080000Z\nDTEND:20261123T100000Z\nLOCATION:103\nEND:VEVENT\n", 1)
    raise AssertionError("heure UTC acceptée")
except ValueError:
    pass
print("ok")
