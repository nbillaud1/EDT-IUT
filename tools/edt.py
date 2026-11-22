"""Lit les PDF d'emploi du temps A1/A2/A3 et écrit site/data.json (salles occupées par semaine et par jour).

Usage : python tools/edt.py [dossier_de_sortie]   (défaut : site/)
Seule dépendance : pypdf.
"""
import json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader
from pypdf.generic import ContentStream

BASE = "https://edt-iut-info.unilim.fr/edt/"
PROMOS = ["A1", "A2", "A3"]
DAYS = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI"]
COURSE = re.compile(r"^\s*(\S+)\s+-\s+(\S+)\s+-\s+(\S+)\s*$")  # Module - Prof/Groupe - Salle
WEEK = re.compile(r"Semaine\s+(\d+)\s+\((\d+)\)\s*:\s*du\s+(\d\d/\d\d/\d{4})\s+au\s+(\d\d/\d\d/\d{4})")


def split_rooms(code):
    """« 104 » -> [104] ; « 104-5 » -> [104, 105] (salles jumelées) ; « . » ou code inconnu (« 03-12 ») -> [None]."""
    if m := re.fullmatch(r"(\d{3})-(\d)", code):
        return [m.group(1), m.group(1)[:2] + m.group(2)]
    if re.fullmatch(r"\d{3}|R\d{1,3}|[A-Z]{2,}", code):
        return [code]
    return [None]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "salles-libres-iut"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _mul(m, n):
    return [m[0]*n[0] + m[1]*n[2], m[0]*n[1] + m[1]*n[3], m[2]*n[0] + m[3]*n[2],
            m[2]*n[1] + m[3]*n[3], m[4]*n[0] + m[5]*n[2] + n[4], m[4]*n[1] + m[5]*n[3] + n[5]]


def _pt(x, y, m):
    return m[0]*x + m[2]*y + m[4], m[1]*x + m[3]*y + m[5]


def _shapes(reader):
    """Rectangles remplis (x0, x1, y0, y1) et textes (x, y, str) du dessin de la page."""
    page = reader.pages[0]
    xobjs = page["/Resources"].get("/XObject", {})
    streams = [xobjs[k].get_object() for k in xobjs] or [page.get_contents()]
    fills, texts = [], []
    for st in streams:
        ctm, stack, pts, tm = [1, 0, 0, 1, 0, 0], [], [], [1, 0, 0, 1, 0, 0]
        for args, op in ContentStream(st, reader).operations:
            if op == b"q": stack.append(ctm[:])
            elif op == b"Q": ctm = stack.pop() if stack else [1, 0, 0, 1, 0, 0]
            elif op == b"cm": ctm = _mul([float(a) for a in args], ctm)
            elif op in (b"m", b"l"): pts.append(_pt(float(args[0]), float(args[1]), ctm))
            elif op == b"re":
                x, y, w, h = (float(a) for a in args)
                pts += [_pt(x, y, ctm), _pt(x + w, y + h, ctm)]
            elif op in (b"f", b"f*", b"F", b"B", b"b"):
                if pts:
                    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                    fills.append((min(xs), max(xs), min(ys), max(ys)))
                pts = []
            elif op in (b"S", b"s", b"n"): pts = []
            elif op == b"Tm": tm = [float(a) for a in args]
            elif op == b"Td": tm = tm[:4] + [tm[4] + float(args[0]), tm[5] + float(args[1])]
            elif op == b"Tj":
                s = args[0]
                s = s.decode("latin-1") if isinstance(s, bytes) else str(s)
                texts.append((*_pt(tm[4], tm[5], ctm), s))
    return fills, texts


def parse_pdf(data):
    """-> {"num", "start", "end", "events": [(jour, debut_min, fin_min, salle_ou_None, module)]}"""
    from io import BytesIO
    fills, texts = _shapes(PdfReader(BytesIO(data)))
    header = next((m for _, _, s in texts if (m := WEEK.search(s))), None)
    if not header:
        raise ValueError("en-tête de semaine introuvable")
    # Axe des heures : libellés « 8:00 », « 8:30 »… alignés sur une ligne -> x de chaque demi-heure.
    ticks = sorted({(round(x, 1), s.strip()) for x, _, s in texts if re.fullmatch(r"\s*\d{1,2}:\d\d", s)})
    if len(ticks) < 2:
        raise ValueError("axe des heures introuvable")
    (x0, t0), (x1, t1) = ticks[0], ticks[1]
    to_min = lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1])
    step = x1 - x0  # largeur d'une demi-heure
    # Le libellé est décalé dans sa case : la case de t0 commence à la fin de la colonne des groupes.
    left = min((f[0] for f in fills if abs(f[1] - f[0] - step) < 1 and f[0] < x0 <= f[1]), default=x0)
    minute_at = lambda x: to_min(t0) + round((x - left) / step * 30 / 15) * 15
    # Bandes des jours : rectangles qui contiennent le libellé LUNDI, MARDI…
    bands = {}
    for x, y, s in texts:
        if s.strip() in DAYS:
            cand = [f for f in fills if f[0] <= x <= f[1] and f[2] <= y <= f[3] and f[1] < left + 1]
            if cand:
                f = max(cand, key=lambda f: f[3] - f[2])
                bands[s.strip()] = (f[2], f[3])
    events = []
    for x, y, s in texts:
        m = COURSE.match(s)
        if not m:
            continue
        boxes = [f for f in fills if f[0] - 1 <= x <= f[1] and f[2] <= y <= f[3] and f[0] >= left - 1]
        if not boxes:
            continue
        b = min(boxes, key=lambda f: (f[1] - f[0]) * (f[3] - f[2]))
        cy = (b[2] + b[3]) / 2
        day = next((d for d, (lo, hi) in bands.items() if lo <= cy <= hi), None)
        if day is None:
            continue
        for room in split_rooms(m.group(3)):
            events.append((day, minute_at(b[0]), minute_at(b[1]), room, m.group(1)))
    fmt = lambda d: datetime.strptime(d, "%d/%m/%Y").date().isoformat()
    return {"num": int(header.group(1)), "start": fmt(header.group(3)), "end": fmt(header.group(4)), "events": events}


def list_pdfs(promo):
    html = fetch(BASE + promo + "/").decode("utf-8", "replace")
    return sorted(set(re.findall(rf'href="({promo}_S\d+\.pdf)"', html)), key=lambda n: int(re.search(r"S(\d+)", n).group(1)))


def build():
    weeks, rooms, errors = {}, set(), []
    for promo in PROMOS:
        for name in list_pdfs(promo):
            try:
                w = parse_pdf(fetch(BASE + promo + "/" + name))
            except Exception as e:  # un PDF illisible ne doit pas bloquer les autres
                errors.append(f"{name}: {e}")
                continue
            wk = weeks.setdefault(w["start"], {"num": w["num"], "start": w["start"], "end": w["end"],
                                               "busy": {}, "unknown": {}, "promos": []})
            wk["promos"].append(promo)
            for day, s, e, room, _ in w["events"]:
                if room is None:
                    wk["unknown"][day] = wk["unknown"].get(day, 0) + 1
                    continue
                rooms.add(room)
                wk["busy"].setdefault(day, {}).setdefault(room, []).append([s, e])
    for wk in weeks.values():
        for day in wk["busy"].values():
            for r, slots in day.items():
                day[r] = sorted(map(list, {tuple(x) for x in slots}))
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "rooms": sorted(rooms, key=lambda r: (not r[0].isdigit(), r)),
        "weeks": [weeks[k] for k in sorted(weeks)],
        "errors": errors,
    }


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    out.mkdir(parents=True, exist_ok=True)
    data = build()
    (out / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(data['weeks'])} semaines, {len(data['rooms'])} salles, {len(data['errors'])} erreurs")
    for e in data["errors"]:
        print("  !", e)
    if not data["weeks"]:
        sys.exit(1)  # ne pas publier un fichier vide
