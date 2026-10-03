"""
Lecteur XLSX/XLSM minimaliste et tolérant, basé sur la bibliothèque standard.

Contourne le fait qu'openpyxl échoue sur certains dessins de ce classeur :
on lit directement le XML (feuilles + chaînes partagées + tableaux
structurés). Gère aussi le déchiffrement si un mot de passe est fourni.
"""
import io
import re
import zipfile


def ouvrir(path, mot_de_passe=None) -> zipfile.ZipFile:
    """Ouvre le classeur, en le déchiffrant d'abord si nécessaire."""
    with open(path, "rb") as fh:
        entete = fh.read(8)
    # Signature d'un fichier OLE chiffré (Compound File).
    if entete[:4] == b"\xd0\xcf\x11\xe0":
        if not mot_de_passe:
            raise ValueError(
                "Le fichier est chiffré : fournissez --mot-de-passe."
            )
        import msoffcrypto

        with open(path, "rb") as fh:
            office = msoffcrypto.OfficeFile(fh)
            office.load_key(password=mot_de_passe)
            buf = io.BytesIO()
            office.decrypt(buf)
        buf.seek(0)
        return zipfile.ZipFile(buf)
    return zipfile.ZipFile(path)


def _chaines_partagees(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    xml = z.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
    chaines = []
    for si in re.findall(r"<si>(.*?)</si>", xml, re.S):
        txt = "".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))
        chaines.append(re.sub(r"<[^>]+>", "", txt))
    return chaines


def _carte_feuilles(z):
    """Retourne {nom_onglet: fichier_sheet}."""
    wb = z.read("xl/workbook.xml").decode("utf-8", "ignore")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8", "ignore")
    rid_to_file = {}
    for m in re.finditer(r'Id="([^"]*)"[^>]*Target="(worksheets/[^"]*)"', rels):
        rid_to_file[m.group(1)] = "xl/" + m.group(2)
    noms = {}
    for m in re.finditer(r'<sheet[^>]*name="([^"]*)"[^>]*r:id="([^"]*)"', wb):
        noms[m.group(1)] = rid_to_file.get(m.group(2))
    return noms


def _carte_cellules(z, sheet_file, chaines):
    """Retourne {coord: valeur} pour une feuille."""
    xml = z.read(sheet_file).decode("utf-8", "ignore")
    cellules = {}
    for m in re.finditer(r'<c r="([A-Z]+\d+)"([^>]*)>(.*?)</c>', xml, re.S):
        coord, attrs, inner = m.group(1), m.group(2), m.group(3)
        t = re.search(r't="([^"]*)"', attrs)
        typ = t.group(1) if t else None
        val = None
        mis = re.search(r"<is>.*?<t[^>]*>(.*?)</t>", inner, re.S)
        mv = re.search(r"<v>(.*?)</v>", inner, re.S)
        if mis:
            val = mis.group(1)
        elif mv:
            raw = mv.group(1)
            if typ == "s":
                try:
                    val = chaines[int(raw)]
                except (ValueError, IndexError):
                    val = raw
            else:
                val = raw
        if val is not None:
            cellules[coord] = _decode(val)
    return cellules


def _decode(s):
    return (
        s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        .replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'")
        if isinstance(s, str)
        else s
    )


_COL_RE = re.compile(r"([A-Z]+)(\d+)")


def _col_index(lettres):
    n = 0
    for c in lettres:
        n = n * 26 + (ord(c) - 64)
    return n


def _plage(ref):
    """'A2:C9' -> (col1, row1, col2, row2)."""
    a, b = ref.split(":") if ":" in ref else (ref, ref)
    ma, mb = _COL_RE.match(a), _COL_RE.match(b)
    return (
        _col_index(ma.group(1)), int(ma.group(2)),
        _col_index(mb.group(1)), int(mb.group(2)),
    )


def _lettre(idx):
    s = ""
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def lire_tableaux(z):
    """
    Retourne la liste des tableaux structurés :
    {display, colonnes:[...], ref, sheet_file, lignes:[{col: val}]}.
    """
    chaines = _chaines_partagees(z)
    resultats = []
    sheet_files = [n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
    for sheet_file in sheet_files:
        base = sheet_file.split("/")[-1]
        rels_path = f"xl/worksheets/_rels/{base}.rels"
        if rels_path not in z.namelist():
            continue
        rels = z.read(rels_path).decode("utf-8", "ignore")
        tables = re.findall(r'Target="(\.\./tables/table\d+\.xml)"', rels)
        if not tables:
            continue
        cellules = None
        for t in tables:
            tpath = "xl/" + t.replace("../", "")
            if tpath not in z.namelist():
                continue
            tx = z.read(tpath).decode("utf-8", "ignore")
            disp = re.search(r'displayName="([^"]*)"', tx) or re.search(r'name="([^"]*)"', tx)
            ref = re.search(r'ref="([^"]*)"', tx)
            cols = re.findall(r'<tableColumn[^>]*name="([^"]*)"', tx)
            if not ref:
                continue
            if cellules is None:
                cellules = _carte_cellules(z, sheet_file, chaines)
            c1, r1, c2, r2 = _plage(ref.group(1))
            lignes = []
            for row in range(r1 + 1, r2 + 1):  # +1 : on saute l'en-tête
                enreg = {}
                vide = True
                for ci, col in enumerate(cols):
                    coord = f"{_lettre(c1 + ci)}{row}"
                    v = cellules.get(coord)
                    enreg[_decode(col).strip()] = v
                    if v not in (None, "", 0, "0"):
                        vide = False
                if not vide:
                    lignes.append(enreg)
            resultats.append({
                "display": _decode(disp.group(1)) if disp else "",
                "colonnes": [_decode(c).strip() for c in cols],
                "ref": ref.group(1),
                "sheet_file": sheet_file,
                "lignes": lignes,
            })
    return resultats
