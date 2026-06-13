import re
import math
from collections import defaultdict

import pandas as pd
import streamlit as st

# -------------------------
# Data massa atom (g/mol)
# -------------------------
# Nilai relatif (standar IUPAC); cukup untuk kebutuhan kalkulator edukasi.
ATOMIC_MASS = {
    # 1
    "H": 1.008,
    "He": 4.0026,
    # 2
    "Li": 6.94,
    "Be": 9.0122,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Ne": 20.1797,
    # 3
    "Na": 22.9897,
    "Mg": 24.305,
    "Al": 26.9815,
    "Si": 28.085,
    "P": 30.9738,
    "S": 32.06,
    "Cl": 35.45,
    "Ar": 39.948,
    # 4
    "K": 39.0983,
    "Ca": 40.078,
    "Sc": 44.9559,
    "Ti": 47.867,
    "V": 50.9415,
    "Cr": 51.9961,
    "Mn": 54.938,
    "Fe": 55.845,
    "Co": 58.9332,
    "Ni": 58.6934,
    "Cu": 63.546,
    "Zn": 65.38,
    # 5
    "Ga": 69.723,
    "Ge": 72.64,
    "As": 74.9216,
    "Se": 78.96,
    "Br": 79.904,
    "Kr": 83.798,
    # 6
    "Rb": 85.4678,
    "Sr": 87.62,
    "Y": 88.9059,
    "Zr": 91.224,
    "Nb": 92.9064,
    "Mo": 95.96,
    "Tc": 98.0,
    "Ru": 101.07,
    "Rh": 102.9055,
    "Pd": 106.42,
    "Ag": 107.8682,
    "Cd": 112.411,
    # 7
    "In": 114.818,
    "Sn": 118.71,
    "Sb": 121.76,
    "Te": 127.6,
    "I": 126.90447,
    "Xe": 131.293,
    # 8
    "Cs": 132.90545,
    "Ba": 137.327,
    "La": 138.90547,
    "Ce": 140.116,
    "Pr": 140.90765,
    "Nd": 144.242,
    "Pm": 145.0,
    "Sm": 150.36,
    "Eu": 151.964,
    "Gd": 157.25,
    "Tb": 158.92535,
    "Dy": 162.5,
    "Ho": 164.93033,
    "Er": 167.259,
    "Tm": 168.93422,
    "Yb": 173.054,
    "Lu": 174.9668,
    # 9
    "Hf": 178.49,
    "Ta": 180.94788,
    "W": 183.84,
    "Re": 186.207,
    "Os": 190.23,
    "Ir": 192.217,
    "Pt": 195.084,
    "Au": 196.96657,
    "Hg": 200.59,
    # 10
    "Tl": 204.38,
    "Pb": 207.2,
    "Bi": 208.9804,
    "Po": 209.0,
    "At": 210.0,
    "Rn": 222.0,
    # 11
    "Fr": 223.0,
    "Ra": 226.0,
    "Ac": 227.0,
    "Th": 232.03806,
    "Pa": 231.03588,
    "U": 238.02891,
    # 12 (opsional beberapa lagi agar input sering terpakai)
    "Np": 237.0,
    "Pu": 244.0,
    "Am": 243.0,
    "Cm": 247.0,
    "Bk": 247.0,
    "Cf": 251.0,
    "Es": 252.0,
    "Fm": 257.0,
    "Md": 258.0,
    "No": 259.0,
    "Lr": 262.0,
}

# -------------------------
# Periodic table (full grid) - dataset posisi
# -------------------------
# Grup memakai penomoran IUPAC 1..18.
# Blok: s / p / d / f
PERIODIC_META = {
    # Period 1
    "H": (1, 1, "s"),
    "He": (1, 18, "s"),

    # Period 2
    "Li": (2, 1, "s"),
    "Be": (2, 2, "s"),
    "B": (2, 13, "p"),
    "C": (2, 14, "p"),
    "N": (2, 15, "p"),
    "O": (2, 16, "p"),
    "F": (2, 17, "p"),
    "Ne": (2, 18, "p"),

    # Period 3
    "Na": (3, 1, "s"),
    "Mg": (3, 2, "s"),
    "Al": (3, 13, "p"),
    "Si": (3, 14, "p"),
    "P": (3, 15, "p"),
    "S": (3, 16, "p"),
    "Cl": (3, 17, "p"),
    "Ar": (3, 18, "p"),

    # Period 4
    "K": (4, 1, "s"),
    "Ca": (4, 2, "s"),
    "Sc": (4, 3, "d"),
    "Ti": (4, 4, "d"),
    "V": (4, 5, "d"),
    "Cr": (4, 6, "d"),
    "Mn": (4, 7, "d"),
    "Fe": (4, 8, "d"),
    "Co": (4, 9, "d"),
    "Ni": (4, 10, "d"),
    "Cu": (4, 11, "d"),
    "Zn": (4, 12, "d"),
    "Ga": (4, 13, "p"),
    "Ge": (4, 14, "p"),
    "As": (4, 15, "p"),
    "Se": (4, 16, "p"),
    "Br": (4, 17, "p"),
    "Kr": (4, 18, "p"),

    # Period 5
    "Rb": (5, 1, "s"),
    "Sr": (5, 2, "s"),
    "Y": (5, 3, "d"),
    "Zr": (5, 4, "d"),
    "Nb": (5, 5, "d"),
    "Mo": (5, 6, "d"),
    "Tc": (5, 7, "d"),
    "Ru": (5, 8, "d"),
    "Rh": (5, 9, "d"),
    "Pd": (5, 10, "d"),
    "Ag": (5, 11, "d"),
    "Cd": (5, 12, "d"),
    "In": (5, 13, "p"),
    "Sn": (5, 14, "p"),
    "Sb": (5, 15, "p"),
    "Te": (5, 16, "p"),
    "I": (5, 17, "p"),
    "Xe": (5, 18, "p"),

    # Period 6
    "Cs": (6, 1, "s"),
    "Ba": (6, 2, "s"),
    "La": (6, 3, "d"),
    # Lanthanides (deret)
    "Ce": (6, 4, "f"),
    "Pr": (6, 5, "f"),
    "Nd": (6, 6, "f"),
    "Pm": (6, 7, "f"),
    "Sm": (6, 8, "f"),
    "Eu": (6, 9, "f"),
    "Gd": (6, 10, "f"),
    "Tb": (6, 11, "f"),
    "Dy": (6, 12, "f"),
    "Ho": (6, 13, "f"),
    "Er": (6, 14, "f"),
    "Tm": (6, 15, "f"),
    "Yb": (6, 16, "f"),
    "Lu": (6, 17, "f"),

    "Hf": (6, 4, "d"),
    "Ta": (6, 5, "d"),
    "W": (6, 6, "d"),
    "Re": (6, 7, "d"),
    "Os": (6, 8, "d"),
    "Ir": (6, 9, "d"),
    "Pt": (6, 10, "d"),
    "Au": (6, 11, "d"),
    "Hg": (6, 12, "d"),
    "Tl": (6, 13, "p"),
    "Pb": (6, 14, "p"),
    "Bi": (6, 15, "p"),
    "Po": (6, 16, "p"),
    "At": (6, 17, "p"),
    "Rn": (6, 18, "p"),

    # Period 7
    "Fr": (7, 1, "s"),
    "Ra": (7, 2, "s"),
    "Ac": (7, 3, "d"),
    # Actinides (deret)
    "Th": (7, 4, "f"),
    "Pa": (7, 5, "f"),
    "U": (7, 6, "f"),
    "Np": (7, 7, "f"),
    "Pu": (7, 8, "f"),
    "Am": (7, 9, "f"),
    "Cm": (7, 10, "f"),
    "Bk": (7, 11, "f"),
    "Cf": (7, 12, "f"),
    "Es": (7, 13, "f"),
    "Fm": (7, 14, "f"),
    "Md": (7, 15, "f"),
    "No": (7, 16, "f"),
    "Lr": (7, 17, "f"),
}

# -------------------------
# Parser rumus kimia
# -------------------------
TOKEN_RE = re.compile(r"([A-Z][a-z]?|\(|\)|\d+|\.|·)")


def _normalize_formula(formula: str) -> str:
    formula = formula.strip().replace(" ", "")
    return formula.replace("·", ".")


def _parse_tokens(formula: str):
    tokens = TOKEN_RE.findall(formula)
    if not tokens:
        raise ValueError("Rumus tidak dapat diparse. Pastikan format benar, mis. H2O atau Ca(OH)2")
    return tokens


def parse_formula(formula: str) -> dict[str, int]:
    formula = _normalize_formula(formula)
    formula = formula.strip().replace(" ", "")
    if not formula:
        raise ValueError("Rumus kosong")

    # Dot-hydrate: mis. Na2B4O7.10H2O atau CuSO4·5H2O (diubah jadi dot '.')
    if "." in formula:
        parts = formula.split(".")
        if len(parts) == 2 and parts[1]:
            m = re.match(r"^(\d+)(.*)$", parts[1])
            if m:
                mult = int(m.group(1))
                rest = m.group(2)
                base_counts = parse_formula(parts[0])
                hydrate_counts = parse_formula(rest)
                merged: defaultdict[str, int] = defaultdict(int)
                for el, cnt in base_counts.items():
                    merged[el] += cnt
                for el, cnt in hydrate_counts.items():
                    merged[el] += cnt * mult
                return dict(merged)

    tokens = _parse_tokens(formula)
    stack: list[defaultdict[str, int]] = [defaultdict(int)]

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append(defaultdict(int))
            i += 1
        elif tok == ")":
            if len(stack) == 1:
                raise ValueError("Kurung ')' tidak memiliki pasangan '('")
            group_counts = stack.pop()

            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 1

            for el, cnt in group_counts.items():
                stack[-1][el] += cnt * mult
            i += 1
        elif tok.isdigit():
            raise ValueError("Angka tanpa elemen/kurung sebelumya")
        else:
            el = tok
            if el not in ATOMIC_MASS:
                raise ValueError(f"Unsur tidak dikenal: {el}")

            cnt = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                cnt = int(tokens[i + 1])
                i += 1

            stack[-1][el] += cnt
            i += 1

    if len(stack) != 1:
        raise ValueError("Kurung '(' tidak ditutup")

    return dict(stack[0])


def calculate_molar_mass(counts: dict[str, int]) -> float:
    total = 0.0
    for el, cnt in counts.items():
        total += ATOMIC_MASS[el] * cnt
    return total


# -------------------------
# UI Streamlit
# -------------------------
st.set_page_config(page_title="Kalkulator Bobot Molekul", layout="wide")

st.markdown(
    """
    <style>
    :root{
      /* Light-friendly theme (kontras bagus di laptop layar putih) */
      --bg0:#F7F8FF;
      --bg1:#FFFFFF;

      --card: rgba(255,255,255,.88);
      --card2: rgba(255,255,255,.98);
      --border: rgba(17,24,39,.12);

      --text: rgba(15, 23, 42, .92);     /* slate-900 */
      --muted: rgba(15, 23, 42, .62);    /* slate-700 */

      --brand1:#6D28D9; /* violet  */
      --brand2:#16A34A; /* green    */
      --brand3:#0284C7; /* sky      */

      --shadow: 0 14px 50px rgba(2, 6, 23, .12);
      --radius: 18px;
    }

    /* Background */
    .stApp{
      /* Reduced-visual-noise chemical background (less eye strain) */
      background:
        /* Soft ambient color (low contrast) */
        radial-gradient(900px 650px at 80% 20%, rgba(2,132,199,.06), rgba(2,132,199,0) 65%),
        radial-gradient(900px 650px at 10% 70%, rgba(109,40,217,.05), rgba(109,40,217,0) 65%),

        /* Atom dots (smaller + much lower opacity) */
        radial-gradient(circle at 12px 12px, rgba(2,132,199,.12) 0 1px, rgba(2,132,199,0) 2px) 0 0 / 30px 30px,
        radial-gradient(circle at 22px 8px, rgba(109,40,217,.10) 0 0.9px, rgba(109,40,217,0) 2px) 0 0 / 40px 40px,

        /* Micro mesh (very faint) */
        linear-gradient(rgba(2,132,199,.04) 1px, transparent 1px) 0 0 / 48px 48px,
        linear-gradient(90deg, rgba(109,40,217,.03) 1px, transparent 1px) 0 0 / 48px 48px,

        /* Slight glow blobs (muted) */
        radial-gradient(1200px 600px at 15% -10%, rgba(109,40,217,.14), transparent 62%),
        radial-gradient(900px 480px at 90% 10%, rgba(2,132,199,.10), transparent 62%),

        /* Fallback base */
        linear-gradient(180deg, var(--bg0), var(--bg1));

      color: var(--text);
      background-attachment: fixed;
    }

    /* Streamlit widgets (Sidebar merah) */
    div[data-testid="stSidebar"]{
      background: linear-gradient(160deg, rgba(239,68,68,.22), rgba(254,202,202,.16)) !important;
      backdrop-filter: blur(10px);
      border-right: 1px solid rgba(239,68,68,.30);
    }

    /* Radio/menu items di sidebar */
    div[data-testid="stSidebar"] .stRadio > label,
    div[data-testid="stSidebar"] .stRadio label{
      color: rgba(255,255,255,.92) !important;
    }

    /* Hover item menu */
    div[data-testid="stSidebar"] .stRadio label:hover{
      background: rgba(239,68,68,.10) !important;
      border-radius: 10px;
    }

    /* Aktif/selected */
    div[data-testid="stSidebar"] .stRadio input:checked ~ div,
    div[data-testid="stSidebar"] .stRadio input:checked + div,
    div[data-testid="stSidebar"] .stRadio input:checked ~ label{
      color: #ffffff !important;
    }

    /* Dot/border radio */
    div[data-testid="stSidebar"] input[type="radio"]{
      accent-color: #ef4444 !important;
    }

    /* Card helpers */
    .bb-card{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 18px 18px;
      overflow: hidden;
    }
    .bb-card:before{
      content:"";
      position:absolute;
      inset:-2px;
      background: radial-gradient(circle at 20% 10%, rgba(109,40,217,.22), transparent 45%),
                  radial-gradient(circle at 90% 20%, rgba(2,132,199,.18), transparent 40%);
      pointer-events:none;
      opacity:.9;
    }

    /* Hero */
    .bb-hero{
      padding: 18px 0 8px 0;
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap: 14px;
    }
    .bb-hero-left{ flex: 1; }
    .bb-hero-title{
      font-size: 2.15rem;
      line-height: 1.08;
      margin: 0;
      font-weight: 900;
      letter-spacing: -.02em;
      color: var(--text);
    }
    .bb-hero-sub{
      color: var(--muted);
      margin-top: 8px;
      font-size: 1rem;
    }
    .bb-pillrow{ margin-top: 12px; display:flex; flex-wrap:wrap; gap:10px; }
    .bb-pill{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding: 10px 12px;
      border-radius: 999px;
      border:1px solid rgba(17,24,39,.14);
      background: rgba(255,255,255,.70);
      font-weight: 800;
      color: rgba(15, 23, 42, .90);
      font-size:.92rem;
    }
    .bb-pill .dot{
      width:10px;height:10px;border-radius:50%;
      background: linear-gradient(180deg, var(--brand1), var(--brand3));
      box-shadow: 0 0 0 4px rgba(109,40,217,.12);
    }

    /* Buttons */
    button[kind="primary"]{
      background: linear-gradient(90deg, var(--brand1), var(--brand3)) !important;
      border: 1px solid rgba(2, 132, 199,.20) !important;
      color: #FFFFFF !important;
    }

    /* Inputs focus */
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"] textarea:focus{
      outline: none !important;
      box-shadow: 0 0 0 3px rgba(2,132,199,.20) !important;
      border-color: rgba(2,132,199,.55) !important;
    }

    /* Generic divider tint */
    hr{ border-color: rgba(17,24,39,.14) !important; }

    /* Small captions */
    .bb-muted{ color: var(--muted); }
    </style>
    """,
    unsafe_allow_html=True,
)

# Spacer & Hero (HTML untuk konsisten dengan theme)
st.markdown(
    """
    <div class="bb-hero">
      <div class="bb-hero-left">
        <div class="bb-hero-title">🧪 Kalkulator Bobot Molekul & Bobot Ekuivalen</div>
        <div class="bb-hero-sub">Hitung <b>Mr</b> (massa molar) dan <b>Be</b> dari rumus kimia—cepat, rapi, dan edukatif.</div>
        <div class="bb-pillrow">
          <div class="bb-pill"><span class="dot"></span>Input: <b>H2O</b>, <b>CO2</b>, <b>NaCl</b>, <b>Ca(OH)2</b></div>
          <div class="bb-pill"><span class="dot"></span>Support: <b>( )</b> & <b>dot hydrate</b> (contoh: CuSO4·5H2O)</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar menu (Beranda / Kalkulator / Tabel Periodik)
menu = st.sidebar.radio(
    "Menu",
    options=["Beranda", "Kalkulator", "Hitung Valensi/Biloks", "Tabel Periodik"],
    index=0,
)

if menu == "Beranda":
    st.subheader("Selamat datang")
    st.write(
        "Aplikasi ini membantu menghitung **Mr (bobot molekul)** dari rumus kimia, serta menyediakan **tabel periodik** dari dataset massa atom yang ada."
    )
    st.markdown("---")

    st.markdown(
        """
        <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-top:6px; margin-bottom:10px;">
          <div style="font-size:1.1rem; font-weight:1000;">
            🧠✨ Teori Singkat: Bobot Molekul & Bobot Ekuivalen
          </div>
          <div class="bb-muted" style="font-size:.95rem;">
            Rumusnya tetap sama—tapi tampilannya lebih “kimia banget”.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .element-kartu-wrap{margin-top: .75rem; margin-bottom: .9rem;}
        .element-grid{
            display:grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }
        @media (max-width: 900px){
            .element-grid{grid-template-columns: repeat(2, minmax(0, 1fr));}
        }
        @media (max-width: 560px){
            .element-grid{grid-template-columns: repeat(1, minmax(0, 1fr));}
        }
        .element-card{
            border-radius: 16px;
            padding: 18px 16px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 6px 24px rgba(15,32,39,0.08);
            position: relative;
            overflow: hidden;
            min-height: 150px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
        }
        .element-card:before{
            content:"";
            position:absolute;
            inset:-2px;
            background: radial-gradient(circle at 20% 10%, rgba(255,255,255,0.55), rgba(255,255,255,0) 45%);
            pointer-events:none;
        }
        .element-symbol{
            font-family: 'DM Sans', sans-serif;
            font-weight: 900;
            font-size: 2.25rem;
            letter-spacing: 0.02em;
            line-height: 1;
            margin-bottom: 8px;
            position:relative;
            z-index:1;
        }
        .element-row{
            position:relative;
            z-index:1;
            font-size: .95rem;
            line-height: 1.45;
            color: rgba(15,32,39,0.95);
            font-weight: 650;
        }
        .element-meta{
            position:relative;
            z-index:1;
            margin-top: 10px;
            font-size: .82rem;
            opacity: .98;
        }
        .element-badge{
            display:inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.6);
            border: 1px solid rgba(0,0,0,0.08);
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    default_elements = ["H", "O", "C", "Na", "Cl", "Cu"]

    block_color = {
        "s": "#E3F2FD",
        "p": "#E8F5E9",
        "d": "#FFF3E0",
        "f": "#F3E5F5",
    }

    def label_blok(block: str) -> str:
        return {
            "s": "Blok s",
            "p": "Blok p",
            "d": "Blok d",
            "f": "Blok f",
        }.get(block, f"Blok {block}")

    # Pastikan kartu dirender sebagai HTML murni tanpa f-string entity yang rawan.
    cards_html_parts: list[str] = []
    for sym in default_elements:
        if sym in PERIODIC_META and sym in ATOMIC_MASS:
            _p, _g, blk = PERIODIC_META[sym]
            color = block_color.get(blk, "#FFFFFF")
            mr = ATOMIC_MASS[sym]
            cards_html_parts.append(
                f"""
                <div class="element-card" style="background:{color};">
                    <div>
                        <div class="element-symbol">{sym}</div>
                        <div class="element-row">Mr unsur: {mr:.3f} g/mol</div>
                    </div>
                    <div class="element-meta">
                        <span class="element-badge">{label_blok(blk)}</span>
                    </div>
                </div>
                """.strip()
            )

    cards_html = "\n".join(cards_html_parts)

    st.markdown(
        f"""
        <div class="element-kartu-wrap">
            <div class="element-grid">
                {cards_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 10px;">
          <div class="bb-card">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
              <div style="font-weight:1000; font-size:1.1rem;">🧪 1) Bobot molekul <span style="opacity:.9;">(Mr)</span></div>
              <div style="padding:8px 12px; border-radius:999px; border:1px solid rgba(17,24,39,.14); background:rgba(17,24,39,.04); font-weight:900; color: var(--text);">
                g/mol
              </div>
            </div>
            <div style="margin-top:10px; color: var(--muted); line-height:1.5;">
              <b style="color: var(--text);">Mr</b> = jumlah massa atom relatif dari semua atom penyusun dalam satu rumus kimia.
            </div>
            <div style="margin-top:12px; padding:12px 14px; border-radius:14px; border:1px solid rgba(17,24,39,.10); background: rgba(17,24,39,.03);">
              <div style="font-weight:900; margin-bottom:6px; color: var(--text);">Rumus</div>
              M<sub>r</sub> = ∑ (m<sub>a</sub> × n<sub>a</sub>)
              <div style="margin-top:6px; font-size:.92rem; color: var(--muted);">
                • m<sub>a</sub> = massa atom relatif <br/>
                • n<sub>a</sub> = jumlah atom unsur
              </div>
            </div>
          </div>

          <div class="bb-card">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
              <div style="font-weight:1000; font-size:1.1rem;">⚖️ 2) Bobot ekuivalen <span style="opacity:.9;">(Be)</span></div>
              <div style="padding:8px 12px; border-radius:999px; border:1px solid rgba(17,24,39,.14); background:rgba(17,24,39,.04); font-weight:900; color: var(--text);">
                g/grek
              </div>
            </div>
            <div style="margin-top:10px; color: var(--muted); line-height:1.5;">
              <b style="color: var(--text);">Be</b> = massa per 1 ekuivalen, dihitung dari input <b>n</b> (valensi/faktor ekuivalen).
            </div>
            <div style="margin-top:12px; padding:12px 14px; border-radius:14px; border:1px solid rgba(17,24,39,.10); background: rgba(17,24,39,.03);">
              <div style="font-weight:900; margin-bottom:6px; color: var(--text);">Rumus</div>
              Be = Mr / n
              <div style="margin-top:6px; font-size:.92rem; color: var(--muted);">
                • Mr (g/mol) = bobot molekul <br/>
                • n = jumlah ekuivalen
              </div>
            </div>
            <div style="margin-top:10px; font-size:.92rem; color: rgba(15,23,42,.72);">
              <i>Catatan:</i> nilai <b>n</b> bisa berbeda tergantung konteks reaksi.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.write("**Fitur utama:**")
    st.markdown(
        """
- Input rumus seperti: `H2O`, `CO2`, `NaCl`, `Ca(OH)2`
- Mendukung tanda kurung `()` dan notasi dot hydrates (contoh: `CuSO4·5H2O`)
- Menampilkan komposisi unsur (jumlah atom dan kontribusi Mr)
- Menghitung **berat ekuivalen (Be)** berdasarkan `Be = Mr / n` (input n)
        """
    )
    st.markdown("---")
    st.caption("Tip: gunakan menu di sidebar untuk berpindah halaman.")
    st.markdown(
        """
        <div style="text-align:center; color:#4a7a90; font-size:.9rem; margin-top:1.2rem;">
            <b>Author:</b> 1. Assalwa Gusnia Kurniasih (2560584) 2. Muhammad Zaki (2560690) 3. Rajendra Wirawisesa (2560745) 4. Sri Yunengsih (2560789)  5. Zizi Tsauri Isfahani (2560811)
        </div>
        """,
        unsafe_allow_html=True,
    )

elif menu == "Kalkulator":
    st.markdown(
        """
        <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-top:6px;">
          <div class="bb-card" style="flex:1; min-width:320px;">
            <div style="font-weight:1000; font-size:1.15rem;">🎛️  Kalkulator Bobot Molekul</div>
            <div class="bb-muted" style="margin-top:6px;">
              Masukkan rumus (mis. <b>H2O</b>, <b>CO2</b>, <b>Ca(OH)2</b>, <b>CuSO4·5H2O</b>). Lalu atur nilai <b>n</b> untuk dapat <b>Be</b>.
            </div>
          </div>
          <div class="bb-card" style="min-width:240px; padding:14px 14px;">
            <div style="font-weight:1000;">🧠 Tips cepat</div>
            <div style="margin-top:6px; font-size:.95rem; line-height:1.5; color: var(--muted);">
              Pakai tanda kurung <b>( )</b> untuk pengali.<br/>
              Dot hydrate: <b>CuSO4·5H2O</b> (boleh pakai titik tengah/· atau titik biasa).<br/>
              Input <b>n</b> harus bilangan bulat > 0 agar <b>Be = Mr / n</b> bisa dihitung.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    contoh = ["H2O", "CO2", "NaCl", "Ca(OH)2", "CH3COOH", "CuSO4·5H2O"]
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for idx, c in enumerate([c1, c2, c3, c4, c5, c6]):
        if idx < len(contoh):
            if c.button(f"⚗️ {contoh[idx]}"):
                st.session_state["formula_prefill"] = contoh[idx]

    formula = st.text_input(
        "Rumus kimia",
        value=st.session_state.get("formula_prefill", "Ca(OH)2"),
        help="Gunakan format huruf besar-kecil (mis. Na, Cl) dan angka untuk jumlah atom.",
    )


    col1, col2 = st.columns(2)
    with col1:
        enable_table = st.checkbox("Tampilkan tabel komposisi", value=True)
    with col2:
        decimals = st.slider("Jumlah desimal", min_value=2, max_value=6, value=4)

    # Integrasi sederhana: kalau dipilih dari tab periodik, tampilkan hint
    if "prefill_symbol" in st.session_state and st.session_state.get("prefill_symbol"):
        st.info(f"Unsur dipilih dari tabel: {st.session_state['prefill_symbol']}.")

    if st.button("Hitung", type="primary"):
        try:
            counts = parse_formula(formula)
            total_mr = calculate_molar_mass(counts)

            st.subheader(f"Hasil: Mr({formula}) = {total_mr:.{decimals}f} g/mol")

            # Simpan agar output tidak hilang saat input n berubah (Streamlit rerun).
            st.session_state["last_formula"] = formula
            st.session_state["last_counts"] = counts
            st.session_state["last_total_mr"] = total_mr

        except Exception as e:
            st.error(str(e))

    # BE otomatis tanpa input valensi:
    # n otomatis = jumlah atom unsur target pada rumus (n = counts[target_for_n])
    target_for_n = st.text_input(
        "Unsur target untuk n (ekuivalen) [tanpa valensi]",
        value=str(st.session_state.get("target_for_n", "S")),
        help="n = jumlah atom unsur ini dalam rumus. Contoh: CaSO4 → n(S)=1 (Be = Mr/n).",
    )
    st.session_state["target_for_n"] = target_for_n

    if "last_total_mr" in st.session_state and "last_counts" in st.session_state:
        total_mr = float(st.session_state["last_total_mr"])
        counts = st.session_state["last_counts"]

        target_for_n_clean = (target_for_n or "").strip()
        if not target_for_n_clean:
            st.warning("Unsur target tidak boleh kosong.")
        else:
            n_auto = int(counts.get(target_for_n_clean, 0))
            if n_auto <= 0:
                st.warning(
                    f"Unsur '{target_for_n_clean}' tidak ditemukan di rumus atau jumlahnya 0. "
                    "Coba ganti unsur target."
                )
            else:
                be = total_mr / float(n_auto)
                st.info(
                    f"Berat ekuivalen (Be) = Mr / n = {total_mr:.{decimals}f} / {n_auto} = {be:.{decimals}f} g/ekuiv"
                )

                details = []
                for el in sorted(counts.keys(), key=lambda x: (x != "", x)):
                    cnt = counts[el]
                    mr_el = ATOMIC_MASS[el] * cnt
                    details.append(
                        {
                            "Unsur": el,
                            "Jumlah atom": cnt,
                            "Mr atom (g/mol)": ATOMIC_MASS[el],
                            "Kontribusi (g/mol)": mr_el,
                        }
                    )

                df = pd.DataFrame(details)
                if enable_table:
                    st.dataframe(df, use_container_width=True, hide_index=True)

                st.divider()
                st.caption(
                    "Catatan: n otomatis = jumlah atom unsur target pada rumus. Mr dihitung dari massa atom relatif (g/mol) standar. "
                    "Nilai di dataset dapat berbeda sedikit tergantung sumber."
                )

    st.markdown("---")
    st.markdown(
        "**Contoh input**: `H2O`, `CO2`, `CH3COOH`, `NaCl`, `Ca(OH)2`, `CuSO4·5H2O`\n"
    )

elif menu == "Hitung Valensi/Biloks":
    st.markdown(
        """
        <div class="bb-card">
            <div style="font-weight:1000; font-size:1.15rem;">🧮 Hitung Valensi / Biloks</div>
            <div class="bb-muted" style="margin-top:6px;">
              Menghitung bilangan oksidasi unsur target dari rumus (sesuai aturan versi opsi 2):
              <br/>• Asumsi: H = +1 (default), O = −2 (default)
              <br/>• Unsur selain H dan O boleh muncul, tapi Anda wajib isi biloksnya di bagian “Biloks unsur tambahan”
              <br/>• Hasil: biloks unsur target X (untuk senyawa netral, Σ(n·biloks)=0)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        rumus = st.text_input(
            "Rumus kimia (contoh: H2SO4, Na2CO3, KMnO4)",
            value="H2SO4",
            help="Dukung tanda kurung () dan dot-hydrate: CuSO4·5H2O",
        )
        target = st.text_input(
            "Unsur target yang dicari biloksnya",
            value="S",
            help="Contoh: S pada H2SO4, C pada Na2CO3, Mn pada KMnO4",
        )

        st.markdown("#### Asumsi biloks")
        biloks_h = st.number_input("Biloks H", value=1.0, format="%.4g", step=1.0)
        biloks_o = st.number_input("Biloks O", value=-2.0, format="%.4g", step=1.0)

        st.markdown("#### n (ekuivalen) untuk menghitung Be")
        n_eq_raw = st.text_input(
            "Masukkan n (bilangan bulat > 0)",
            value=str(st.session_state.get("n_eq_valensi_raw", "1")),
            help="Be dipakai rumus: Be = Mr / n (seperti di menu Kalkulator).",
        )
        st.session_state["n_eq_valensi_raw"] = n_eq_raw

        def _parse_int_positive(value: str):
            v = str(value).strip()
            if not v:
                return None
            v = v.replace(",", ".")
            try:
                if "." in v:
                    return None
                n = int(v)
            except Exception:
                return None
            if n <= 0:
                return None
            return n

        n_eq = _parse_int_positive(n_eq_raw)

        tombol = st.button("🔎 Hitung Biloks", type="primary")

        st.caption("Catatan: Unsur selain H dan O bisa ikut muncul. Anda wajib isi biloksnya via input di hasil.")

    with col2:
        if tombol:
            try:
                if n_eq is None:
                    st.warning("Input n tidak valid. Masukkan bilangan bulat > 0 (mis. 1 atau 2).")
                    st.stop()

                counts = parse_formula(rumus)

                target = target.strip()
                if not target:
                    st.error("Unsur target tidak boleh kosong.")
                    st.stop()

                if target not in counts:
                    st.error(f"Unsur target '{target}' tidak ditemukan di rumus '{rumus}'.")
                    st.stop()

                nH = counts.get("H", 0)
                nO = counts.get("O", 0)
                nX = counts.get(target, 0)

                if nX == 0:
                    st.error("Jumlah atom unsur target bernilai 0 (tidak valid).")
                    st.stop()

                extra = sorted([el for el in counts.keys() if el not in {"H", "O", target}])

                # Input biloks untuk unsur ekstra (selain H,O,target)
                biloks_extra = {}
                if extra:
                    st.markdown("#### Biloks unsur tambahan (selain H, O, dan target)")
                    for el in extra:
                        biloks_extra[el] = st.number_input(
                            f"Biloks {el}",
                            value=0.0,
                            format="%.4g",
                            step=1.0,
                            key=f"biloks_{el}",
                        )

                # Persamaan senyawa netral: Σ(n_i * biloks_i) = 0
                # nH*H + nO*O + Σ(n_other*biloks_other) + nX*X = 0
                rhs = -(nH * biloks_h + nO * biloks_o)
                for el in extra:
                    rhs -= counts[el] * biloks_extra[el]

                biloks_x = rhs / nX

                rounded = round(biloks_x)
                if abs(biloks_x - rounded) < 1e-6:
                    biloks_x_out = int(rounded)
                else:
                    biloks_x_out = biloks_x

                st.success(f"Biloks unsur {target} pada {rumus} = {biloks_x_out}")

                # ===== Otomatis hitung Be =====
                total_mr = calculate_molar_mass(counts)
                be = total_mr / float(n_eq)
                st.info(f"Be = Mr / n = {total_mr:.6g} / {n_eq} = {be:.6g} g/ekuiv")

                st.markdown("---")
                st.markdown("##### 🧮 Detail Perhitungan")
                # susun ringkasan Σ
                terms = []
                terms.append((f"H", nH, biloks_h))
                terms.append((f"O", nO, biloks_o))
                for el in extra:
                    terms.append((el, counts[el], biloks_extra[el]))
                terms_sum = sum(cnt * ox for _name, cnt, ox in terms)

                # Σ tanpa target (harus bernilai -nX*X)
                st.markdown(
                    f"""
                    <div style="padding:14px 14px; border-radius:14px; border:1px solid rgba(17,24,39,.10); background: rgba(17,24,39,.03);">
                      <div style="font-weight:900; margin-bottom:8px;">Ringkasan</div>
                      <div style="font-size:.95rem; line-height:1.65;">
                        • Σ(non-target) = {terms_sum}<br/>
                        • {target}: {nX} atom × X<br/>
                        • Syarat: Σ (biloks × jumlah atom) = 0<br/>
                        • Persamaan: (Σ(non-target)) + {nX}(X) = 0<br/>
                        • Hasil: X = {biloks_x}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                details = []
                for el in sorted(counts.keys()):
                    details.append({"Unsur": el, "Jumlah atom": counts[el]})
                import pandas as _pd
                df = _pd.DataFrame(details)
                st.dataframe(df, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(str(e))
        else:
            st.markdown(
                """
                <div class="bb-card" style="padding:18px 18px;">
                  <div style="font-weight:1000; margin-bottom:6px;">Cara pakai</div>
                  <div class="bb-muted" style="line-height:1.6;">
                    Isi <b>rumus</b> dan <b>unsur target</b>, lalu klik <b>Hitung Biloks</b>.<br/>
                    Contoh: <b>H2SO4</b> (target <b>S</b>) → S = +6 (asumsi H=+1, O=−2)
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

elif menu == "Tabel Periodik":
    st.subheader("Tabel Periodik dari dataset massa atom")


    available = sorted(set(ATOMIC_MASS.keys()) & set(PERIODIC_META.keys()))

    selected = st.selectbox("Pilih unsur", options=["(tidak ada)"] + available, index=0)

    # Grid 7x18 (periode x grup)
    grid = []
    for period in range(1, 8):
        row = []
        for group in range(1, 19):
            found = None
            for el in available:
                p, g, _b = PERIODIC_META[el]
                if p == period and g == group:
                    found = el
                    break
            row.append(found)
        grid.append(row)

    # Header labels (row/column)
    column_labels = list(range(1, 19))
    row_labels = list(range(1, 8))


    # Map blok (s/p/d/f) menjadi label yang lebih mudah dimengerti user
    block_label = {
        "s": "Blok s (alkali/alkali tanah & H/He)",
        "p": "Blok p (unsur golongan utama)",
        "d": "Blok d (logam transisi)",
        "f": "Blok f (lantanida & aktinida)",
    }

    block_color = {
        "s": "#E3F2FD",
        "p": "#E8F5E9",
        "d": "#FFF3E0",
        "f": "#F3E5F5",
    }


    import html as _html

    st.markdown(
        """
        <style>
        .periodic-grid{display:grid; grid-template-columns: repeat(18, 1fr); gap: 6px;}
        .cell{height: 62px; border-radius: 10px; border: 1px solid rgba(0,0,0,0.08); display:flex; flex-direction:column; align-items:center; justify-content:center;}
        .cell.empty{background:transparent; border: 1px dashed rgba(0,0,0,0.12);}
        .small{font-size: 11px; opacity: 0.85; margin-top: 2px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    def render_cell(el):
        if el is None:
            return "<div class='cell empty'></div>"
        p, g, block = PERIODIC_META[el]
        color = block_color.get(block, "#FFFFFF")
        return (
            "<div class='cell' style='background:%s' title='%s | Period %s, Group %s | Block %s'>"
            "<b>%s</b>"
            "<div class='small'>%.3f</div>"
            "</div>"
            % (
                _html.escape(color),
                _html.escape(el),
                p,
                g,
                _html.escape(block),
                _html.escape(el),
                ATOMIC_MASS[el],
            )
        )

    for row in grid:
        cols = "".join(render_cell(el) for el in row)
        st.markdown(f"<div class='periodic-grid'>{cols}</div>", unsafe_allow_html=True)

    st.divider()

    if selected != "(tidak ada)":
        p, g, block = PERIODIC_META[selected]
        st.markdown(f"### Detail unsur: **{selected}**")
        # Tambahan keterangan: nama unsur, nomor atom, dan fasa (perkiraan pada suhu ruang)
        # (dataset nama/nomor/fasa dibuat statis mengikuti simbol unsur yang ada di ATOMIC_MASS)
        ELEMENT_NAME = {
            "H": "Hidrogen",
            "He": "Helium",
            "Li": "Litium",
            "Be": "Berilium",
            "B": "Boron",
            "C": "Karbon",
            "N": "Nitrogen",
            "O": "Oksigen",
            "F": "Fluorin",
            "Ne": "Neon",
            "Na": "Natrium",
            "Mg": "Magnesium",
            "Al": "Aluminium",
            "Si": "Silicon",
            "P": "Fosfor",
            "S": "Belerang",
            "Cl": "Klorin",
            "Ar": "Argon",
            "K": "Kalium",
            "Ca": "Kalsium",
            "Sc": "Skandium",
            "Ti": "Titanium",
            "V": "Vanadium",
            "Cr": "Kromium",
            "Mn": "Mangan",
            "Fe": "Besi",
            "Co": "Kobalt",
            "Ni": "Nikel",
            "Cu": "Tembaga",
            "Zn": "Seng",
            "Ga": "Galium",
            "Ge": "Germanium",
            "As": "Arsen",
            "Se": "Selenium",
            "Br": "Bromin",
            "Kr": "Krypton",
            "Rb": "Rubidium",
            "Sr": "Stronsium",
            "Y": "Itrium",
            "Zr": "Zirkonium",
            "Nb": "Nobium",
            "Mo": "Molibdenum",
            "Tc": "Teknesium",
            "Ru": "Rutenium",
            "Rh": "Rodium",
            "Pd": "Palladium",
            "Ag": "Perak",
            "Cd": "Kadmium",
            "In": "Indium",
            "Sn": "Timah",
            "Sb": "Antimon",
            "Te": "Tellurium",
            "I": "Iodin",
            "Xe": "Xenon",
            "Cs": "Sesium",
            "Ba": "Barium",
            "La": "Lantanum",
            "Ce": "Serium",
            "Pr": "Praseodimium",
            "Nd": "Neodimium",
            "Pm": "Prometium",
            "Sm": "Samarium",
            "Eu": "Europium",
            "Gd": "Gadolinium",
            "Tb": "Terbium",
            "Dy": "Disprosium",
            "Ho": "Holmium",
            "Er": "Erbium",
            "Tm": "Tumbalium",
            "Yb": "Ytterbium",
            "Lu": "Lutetium",
            "Hf": "Hafnium",
            "Ta": "Tantalum",
            "W": "Wolfram",
            "Re": "Renium",
            "Os": "Osmium",
            "Ir": "Iridium",
            "Pt": "Platina",
            "Au": "Emas",
            "Hg": "Merkuri",
            "Tl": "Talium",
            "Pb": "Timbal",
            "Bi": "Bismut",
            "Po": "Polonium",
            "At": "Astatin",
            "Rn": "Radon",
            "Fr": "Fransium",
            "Ra": "Radium",
            "Ac": "Aktinium",
            "Th": "Toriium",
            "Pa": "Protaktinium",
            "U": "Uranium",
            "Np": "Neptunium",
            "Pu": "Plutonium",
            "Am": "Amerisium",
            "Cm": "Kuriu",
            "Bk": "Berkelium",
            "Cf": "Kalifornium",
            "Es": "Einsteinium",
            "Fm": "Fermium",
            "Md": "Mendelevium",
            "No": "Nobelium",
            "Lr": "Lawrensium",
        }

        ATOMIC_NUMBER = {
            "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
            "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18,
            "K": 19, "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28,
            "Cu": 29, "Zn": 30, "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36,
            "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46,
            "Ag": 47, "Cd": 48, "In": 49, "Sn": 50, "Sb": 51, "Te": 52, "I": 53, "Xe": 54,
            "Cs": 55, "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64,
            "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71,
            "Hf": 72, "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
            "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86,
            "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90, "Pa": 91, "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96,
            "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100, "Md": 101, "No": 102, "Lr": 103,
        }

        # Fasa pada suhu ruang (perkiraan umum)
        ELEMENT_PHASE = {
            # gas
            "H": "Gas", "He": "Gas", "N": "Gas", "O": "Gas", "F": "Gas", "Cl": "Gas", "Ne": "Gas", "Ar": "Gas", "Kr": "Gas",
            "Xe": "Gas", "Rn": "Gas",
            # cair (umum pada STP): Hg saja yang jelas cair; lainnya padat/kecuali bromin
            "Br": "Cair", "Hg": "Cair",
            # sisanya padat (perkiraan standar)
        }

        phase = ELEMENT_PHASE.get(selected, "Padat")
        element_name = ELEMENT_NAME.get(selected, selected)
        atomic_no = ATOMIC_NUMBER.get(selected)

        st.write(
            {
                "Unsur": element_name,
                "Nomor atom (Z)": atomic_no,
                "Periode": p,
                "Golongan": g,
                "Blok": block,
                "Kategori blok (jelas)": block_label.get(block, block),
                "Fasa pada suhu ruang (perkiraan)": phase,
                "Massa atom (g/mol)": ATOMIC_MASS[selected],
            }
        )


        if st.button("Masukkan simbol ke kalkulator (hint)"):
            st.session_state["prefill_symbol"] = selected
            st.toast(f"{selected} disimpan untuk hint di tab Kalkulator.")

