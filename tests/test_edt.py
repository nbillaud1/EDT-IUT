"""python -I tests/test_edt.py  — vérifie la lecture d'un vrai PDF (A1, semaine 13, copié le 2026-11-22)."""
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
print("ok")
