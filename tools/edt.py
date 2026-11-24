"""Lit les emplois du temps A1/A2/A3 (calendriers .ics des groupes, PDF en secours) et écrit site/data.json (salles occupées par semaine et par jour).

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
    """Rectangles remplis de couleur (x0, x1, y0, y1) et textes (x, y, str) du dessin de la page.
    Les rectangles blancs (cases vides de la grille) sont ignorés."""
    page = reader.pages[0]
    xobjs = page["/Resources"].get("/XObject", {})
    streams = [xobjs[k].get_object() for k in xobjs] or [page.get_contents()]
    fills, texts = [], []
    for st in streams:
        ctm, stack, pts, tm, color = [1, 0, 0, 1, 0, 0], [], [], [1, 0, 0, 1, 0, 0], (0, 0, 0)
        for args, op in ContentStream(st, reader).operations:
            if op == b"q": stack.append(ctm[:])
            elif op == b"Q": ctm = stack.pop() if stack else [1, 0, 0, 1, 0, 0]
            elif op == b"cm":
                m = [float(a) for a in args]
                if m[0] == 0 and m[3] == 0:
                    continue  # rotation qui met la page en paysage : on lit le dessin non tourné (heures sur l'axe x)
                ctm = _mul(m, ctm)
            elif op in (b"rg", b"sc", b"scn") and len(args) == 3: color = tuple(float(a) for a in args)
            elif op == b"g": color = (float(args[0]),) * 3
            elif op in (b"m", b"l"): pts.append(_pt(float(args[0]), float(args[1]), ctm))
            elif op == b"re":
                x, y, w, h = (float(a) for a in args)
                pts += [_pt(x, y, ctm), _pt(x + w, y + h, ctm)]
            elif op in (b"f", b"f*", b"F", b"B", b"B*", b"b", b"b*"):
                if pts and min(color) < 0.99:
                    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                    fills.append((min(xs), max(xs), min(ys), max(ys)))
                pts = []
            elif op in (b"S", b"s", b"n"): pts = []
            elif op == b"BT": tm = [1, 0, 0, 1, 0, 0]  # chaque bloc de texte repart de l'origine
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
    tick_txt = [(x, y, s.strip()) for x, y, s in texts if re.fullmatch(r"\s*\d{1,2}:\d\d", s)]
    ticks = sorted({(round(x, 1), s) for x, _, s in tick_txt})
    if len(ticks) < 2:
        raise ValueError("axe des heures introuvable")
    (x0, t0), (x1, t1) = ticks[0], ticks[1]
    tick_y = max(y for _, y, _ in tick_txt)
    to_min = lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1])
    step = x1 - x0  # largeur d'une demi-heure
    # Le libellé est décalé dans sa case : le bord gauche de la grille est le bord du rectangle d'en-tête qui le contient.
    left = max((f[0] for f in fills if f[0] < x0 <= f[0] + step and f[2] <= tick_y <= f[3]), default=None)
    if left is None:
        raise ValueError("bord gauche de la grille introuvable")
    minute_at = lambda x: to_min(t0) + round((x - left) / step * 30 / 15) * 15
    # Jours : libellés LUNDI, MARDI… Ancienne mise en page : un rectangle par jour ; nouvelle : une seule
    # bande pour tous les jours, de hauteur égale -> on prend le libellé le plus proche.
    labels = {s.strip(): y for x, y, s in texts if s.strip() in DAYS and x < left}
    if len(labels) < 5:
        raise ValueError(f"jours introuvables ({sorted(labels)})")
    bands = {}
    for d, y in labels.items():
        cand = [f for f in fills if f[1] < left + 1 and f[2] <= y <= f[3]]
        if cand:
            bands[d] = max(((f[2], f[3]) for f in cand), key=lambda b: b[1] - b[0])
    if len(set(bands.values())) < len(labels):
        bands = None

    def day_of(cy):
        if bands:
            return next((d for d, (lo, hi) in bands.items() if lo <= cy <= hi), None)
        return min(labels, key=lambda d: abs(labels[d] - cy))

    # Chaque cours est un rectangle de couleur ; ses lignes de texte sont lues ensemble, de haut en bas :
    # « Module - Prof - Salle » sur une ligne, ou « Module - Intitulé » / « Prof » / « Salle » sur trois.
    in_grid = lambda x, y: x >= left - 1 and y < tick_y - 1
    boxes = {}
    for x, y, s in texts:
        if not s.strip() or not in_grid(x, y) or re.fullmatch(r"\s*\d{1,2}:\d\d", s):
            continue
        cand = [f for f in fills if f[0] - 1 <= x <= f[1] and f[2] <= y <= f[3] and f[0] >= left - 1]
        if not cand:  # intitulé long qui déborde sous sa case : on le rattache à la case juste au-dessus
            below = [f for f in fills if f[0] - 1 <= x <= f[1] and 0 < f[2] - y <= step / 2 and f[0] >= left - 1]
            cand = [min(below, key=lambda f: f[2] - y)] if below else []
        if not cand:
            raise ValueError(f"texte hors d'une case de cours : {s.strip()!r}")
        boxes.setdefault(min(cand, key=lambda f: (f[1] - f[0]) * (f[3] - f[2])), []).append((y, s.strip()))
    events = []
    for b, lines in boxes.items():
        lines = [s for _, s in sorted(lines, reverse=True)]
        m = next((m for s in lines if (m := COURSE.match(s))), None)
        if m:
            module, code = m.group(1), m.group(3)
        else:
            module, code = lines[0].split(" - ")[0], (lines[-1] if len(lines) >= 3 else ".")  # salle = dernière ligne
        day, start, end = day_of((b[2] + b[3]) / 2), minute_at(b[0]), minute_at(b[1])
        if day is None or not (8 * 60 <= start < end <= 19 * 60 + 30):
            raise ValueError(f"cours mal placé : {lines} ({day}, {start}-{end} min)")
        for room in split_rooms(code):
            events.append((day, start, end, room, module))
    fmt = lambda d: datetime.strptime(d, "%d/%m/%Y").date().isoformat()
    return {"num": int(header.group(1)), "start": fmt(header.group(3)), "end": fmt(header.group(4)), "events": events}


def parse_ics(text, num):
    """Calendrier .ics d'un groupe pour une semaine -> même forme que parse_pdf (None si la semaine est vide)."""
    from datetime import date, timedelta
    text = text.replace("\r\n", "\n").replace("\n ", "").replace("\n\t", "")  # lignes repliées (RFC 5545)
    events, monday = [], None
    for block in re.findall(r"BEGIN:VEVENT\n(.*?)END:VEVENT", text, re.S):
        f = {}
        for line in block.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                f[k.split(";")[0]] = (k, v)
        if f.get("STATUS", ("", ""))[1].strip().upper() == "CANCELLED":
            continue
        times = []
        for key in ("DTSTART", "DTEND"):
            k, v = f.get(key, ("", ""))
            m = re.fullmatch(r"(\d{4})(\d\d)(\d\d)T(\d\d)(\d\d)\d\d", v.strip())
            if not m or ("TZID=Europe/Paris" not in k):  # heure UTC ou autre fuseau : format non prévu
                raise ValueError(f"horaire illisible : {k}:{v}")
            y, mo, d, hh, mm = map(int, m.groups())
            times.append((date(y, mo, d), hh * 60 + mm))
        (day, start), (_, end) = times
        if day.weekday() > 5 or end <= start:
            raise ValueError(f"cours mal placé : {f.get('SUMMARY', ('', '?'))[1]} le {day}")
        mon = day - timedelta(days=day.weekday())
        if monday and mon != monday:
            raise ValueError("cours de plusieurs semaines dans le même fichier")
        monday = mon
        loc = f.get("LOCATION", ("", "."))[1].replace("\\,", ",").strip() or "."
        for code in loc.split(","):
            for room in split_rooms(code.strip()):
                events.append((DAYS[day.weekday()], start, end, room, f.get("SUMMARY", ("", ""))[1].strip()))
    if monday is None:
        return None  # shortcut: semaine sans aucun cours (vacances) absente du site ; suffisant tant qu'on ne veut pas l'afficher vide
    return {"num": num, "start": monday.isoformat(), "end": (monday + timedelta(days=5)).isoformat(), "events": events}


def list_pdfs(promo):
    html = fetch(BASE + promo + "/").decode("utf-8", "replace")
    return sorted(set(re.findall(rf'href="({promo}_S\d+\.pdf)"', html)), key=lambda n: int(re.search(r"S(\d+)", n).group(1)))


def list_ics(promo):
    """(chemin, numéro de semaine) des .ics des groupes entiers (G1, G4…) : ils contiennent aussi leurs demi-groupes."""
    groups = sorted(set(re.findall(r'href="(G\d+)/"', fetch(BASE + promo + "/").decode("utf-8", "replace"))))
    for g in groups:
        for name in sorted(set(re.findall(rf'href="({g}_S(\d+)\.ics)"', fetch(f"{BASE}{promo}/{g}/").decode("utf-8", "replace")))):
            yield f"{promo}/{g}/{name[0]}", int(name[1])


def build(source="ics"):
    weeks, rooms, errors = {}, set(), []
    for promo in PROMOS:
        files = list_ics(promo) if source == "ics" else ((f"{promo}/{n}", None) for n in list_pdfs(promo))
        for path, num in files:
            try:
                raw = fetch(BASE + path)
                w = parse_ics(raw.decode("utf-8"), num) if source == "ics" else parse_pdf(raw)
            except Exception as e:  # on note l'erreur et on continue, pour toutes les lister ; rien ne sera publié
                errors.append(f"{path}: {e}")
                continue
            if w is None:
                continue
            wk = weeks.setdefault(w["start"], {"num": w["num"], "start": w["start"], "end": w["end"],
                                               "busy": {}, "unknown": set(), "promos": set()})
            wk["promos"].add(promo)
            for day, s, e, room, what in w["events"]:
                if room is None:
                    wk["unknown"].add((day, s, e, what))  # un CM sans salle apparaît dans chaque groupe : compté une fois
                    continue
                rooms.add(room)
                wk["busy"].setdefault(day, {}).setdefault(room, []).append([s, e])
    for wk in weeks.values():
        for day in wk["busy"].values():
            for r, slots in day.items():
                day[r] = sorted(map(list, {tuple(x) for x in slots}))
        unknown = {}
        for day, *_ in wk["unknown"]:
            unknown[day] = unknown.get(day, 0) + 1
        wk["unknown"], wk["promos"] = unknown, sorted(wk["promos"])
    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "source": source,
        "rooms": sorted(rooms, key=lambda r: (not r[0].isdigit(), r)),
        "weeks": [weeks[k] for k in sorted(weeks)],
        "errors": errors,
    }


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    out.mkdir(parents=True, exist_ok=True)
    data = build("ics")
    if data["errors"] or not data["weeks"]:
        print("Calendriers .ics illisibles, lecture des PDF en secours :")
        for e in data["errors"]:
            print("  !", e)
        data = build("pdf")
    if data["errors"] or not data["weeks"]:
        # Mise en page inattendue : on ne publie rien plutôt que des salles fausses ; le site garde l'ancienne version.
        print("ERREUR, rien n'est écrit :")
        for e in data["errors"]:
            print("  !", e)
        sys.exit(1)
    path = out / "data.json"
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    same = {k: v for k, v in old.items() if k != "generated"} == {k: v for k, v in data.items() if k != "generated"}
    if same:
        print("emplois du temps inchangés, fichier conservé")  # évite un commit quotidien pour rien
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(data['weeks'])} semaines, {len(data['rooms'])} salles (source : {data['source']})")
