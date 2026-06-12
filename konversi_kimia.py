import streamlit as st

# ─── Shared CSS helper (injected once per module call) ──────────────────────
SHARED_CSS = """
<style>
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.7rem;
    color: #0f2027;
    border-left: 4px solid #2c8faf;
    padding-left: .8rem;
    margin: 1.5rem 0 1rem;
}
.result-box {
    background: linear-gradient(135deg, #e8f8ff, #d0effa);
    border: 1.5px solid #7ecfea;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    margin-top: .8rem;
}
.result-box .result-label {
    font-size: .8rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #2c8faf;
    margin-bottom: .3rem;
}
.result-box .result-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #0f2027;
    font-weight: 700;
}
.info-box {
    background: #fff8e1;
    border-left: 4px solid #f9a825;
    border-radius: 0 8px 8px 0;
    padding: .9rem 1.2rem;
    margin-bottom: 1rem;
    color: #5d4e12;
    font-size: .92rem;
    line-height: 1.6;
}
</style>
"""

# ─── Rumus / penjelasan singkat per satuan ──────────────────────────────────
INFO = {
    "Normalitas (N)": "N = jumlah ekuivalen zat terlarut per liter larutan. N = M × valensi",
    "Molaritas (M)": "M = mol zat terlarut per liter larutan. M = (massa/Mr) / V(L)",
    "Molalitas (m)": "m = mol zat terlarut per kg pelarut. m = (massa/Mr) / kg_pelarut",
    "%b/v": "% b/v = (massa zat terlarut (g) / volume larutan (mL)) × 100",
    "%b/b": "% b/b = (massa zat terlarut (g) / massa larutan (g)) × 100",
    "ppm (mg/L)": "ppm = mg zat per liter larutan (≈ mg/kg untuk larutan encer)",
    "ppb (µg/L)": "ppb = µg zat per liter larutan",
}

SATUAN_LIST = list(INFO.keys())


# ─── Fungsi konversi ─────────────────────────────────────────────────────────
# Strategi: konversi semua ke "mol/L" (Molaritas) sebagai satuan pivot,
# kemudian dari pivot ke satuan tujuan.
# Beberapa konversi butuh parameter tambahan (Mr, valensi, densitas, dll.).

def ke_molaritas(nilai, satuan_asal, **kw):
    """Konversi nilai dari satuan_asal → Molaritas (mol/L). Kembalikan float atau raise."""
    mr = kw.get("mr", 1.0)          # Massa molar (g/mol)
    valensi = kw.get("valensi", 1)  # Valensi ion
    rho = kw.get("rho", 1.0)        # Densitas larutan (g/mL) — default air
    kg_pelarut = kw.get("kg_pelarut", 1.0)  # kg pelarut (untuk molalitas)

    if satuan_asal == "Normalitas (N)":
        return nilai / valensi
    elif satuan_asal == "Molaritas (M)":
        return nilai
    elif satuan_asal == "Molalitas (m)":
        # m = mol/kg_pelarut; butuh densitas utk ubah ke M (approx untuk larutan encer)
        # M ≈ (m * rho * 1000) / (1000 + m * mr)  — rumus eksak
        return (nilai * rho * 1000) / (1000 + nilai * mr)
    elif satuan_asal == "%b/v":
        # % b/v = g/100mL → g/L = nilai*10 → mol/L = (nilai*10)/mr
        return (nilai * 10) / mr
    elif satuan_asal == "%b/b":
        # % b/b: rho diperlukan
        # g zat per g larutan × rho(g/mL) × 1000 mL/L / mr
        return (nilai / 100) * rho * 1000 / mr
    elif satuan_asal == "ppm (mg/L)":
        # ppm = mg/L → mol/L = (mg/L) / (mr * 1000)
        return nilai / (mr * 1000)
    elif satuan_asal == "ppb (µg/L)":
        # ppb = µg/L → mol/L = (µg/L) / (mr * 1e6)
        return nilai / (mr * 1e6)
    else:
        raise ValueError(f"Satuan tidak dikenal: {satuan_asal}")


def dari_molaritas(molaritas, satuan_tujuan, **kw):
    """Konversi Molaritas → satuan_tujuan."""
    mr = kw.get("mr", 1.0)
    valensi = kw.get("valensi", 1)
    rho = kw.get("rho", 1.0)

    if satuan_tujuan == "Molaritas (M)":
        return molaritas
    elif satuan_tujuan == "Normalitas (N)":
        return molaritas * valensi
    elif satuan_tujuan == "Molalitas (m)":
        # m = M / (rho*1000 - M*mr) * 1000
        denom = rho * 1000 - molaritas * mr
        if denom <= 0:
            raise ValueError("Densitas terlalu kecil untuk konversi molalitas.")
        return (molaritas * 1000) / denom
    elif satuan_tujuan == "%b/v":
        return (molaritas * mr) / 10
    elif satuan_tujuan == "%b/b":
        return (molaritas * mr) / (rho * 10)
    elif satuan_tujuan == "ppm (mg/L)":
        return molaritas * mr * 1000
    elif satuan_tujuan == "ppb (µg/L)":
        return molaritas * mr * 1e6
    else:
        raise ValueError(f"Satuan tidak dikenal: {satuan_tujuan}")


def needs_valensi(s_asal, s_tujuan):
    return "Normalitas (N)" in (s_asal, s_tujuan)

def needs_rho(s_asal, s_tujuan):
    return any(x in (s_asal, s_tujuan) for x in ["%b/b", "Molalitas (m)"])

def needs_mr(s_asal, s_tujuan):
    # Jika kedua satuan adalah mol-based (N, M, m) saja, mr tidak selalu wajib
    mol_only = {"Normalitas (N)", "Molaritas (M)", "Molalitas (m)"}
    return not ({s_asal, s_tujuan}.issubset(mol_only))


# ─── Kalkulator Valensi / Biloks (Opsi 2) ───────────────────────────────────
# Asumsi versi 1 (sesuai pilihan user):
# - Rumus hanya boleh mengandung: H, O, dan 1 unsur target (mis. S pada H2SO4).
# - Nilai biloks default:
#     H = +1
#     O = -2
# - Jika ada unsur lain selain H, O, dan unsur target, tampilkan error (karena perlu aturan tambahan).
#
# Output:
# - Biloks unsur target (perkiraan) sehingga jumlah biloks * jumlah atom = 0 (senyawa netral)

def _parse_formula_simple(formula: str) -> dict:
    """
    Parse rumus kimia sederhana tanpa tanda kurung.
    Contoh: H2SO4 -> {'H':2,'S':1,'O':4}
    Mendukung: simbol unsur (1 huruf besar + opsional huruf kecil) + angka subscript (opsional).
    """
    import re

    if any(ch in formula for ch in "()[]{}"):
        raise ValueError("Rumus dengan tanda kurung belum didukung di versi ini.")

    s = formula.strip().replace(" ", "")
    if not s:
        raise ValueError("Rumus tidak boleh kosong.")

    tokens = re.findall(r"([A-Z][a-z]?)(\d*)", s)
    if not tokens:
        raise ValueError("Rumus tidak dikenali. Pastikan pakai format seperti H2SO4 atau KMnO4.")

    parsed = {}
    consumed = "".join([f"{el}{cnt}" for el, cnt in tokens])
    # Jika re regex tidak menutupi seluruh string, berarti ada karakter aneh
    if consumed != s:
        # Contoh: karakter seperti +, -, ^, atau angka tanpa konteks
        raise ValueError("Rumus mengandung karakter yang tidak didukung (mis. muatan ion). Versi ini fokus senyawa netral tanpa muatan.")

    for el, cnt in tokens:
        n = int(cnt) if cnt else 1
        parsed[el] = parsed.get(el, 0) + n

    return parsed


def _to_number_maybe_int(x: float, tol: float = 1e-6):
    # bantu formatting: jika mendekati bilangan bulat, kembalikan int
    import math
    r = round(x)
    if abs(x - r) <= tol:
        return int(r)
    return x


def hitung_biloks_dari_rumus_target(formula: str, target: str, biloks_h: float = 1.0, biloks_o: float = -2.0):
    """
    Hitung biloks unsur target untuk senyawa netral (jumlah biloks = 0).
    Return: (biloks_target, detail_dict)
    """
    parsed = _parse_formula_simple(formula)

    target = target.strip()
    if not target:
        raise ValueError("Unsur target tidak boleh kosong.")

    # Validasi target harus ada di rumus
    if target not in parsed:
        raise ValueError(f"Unsur target '{target}' tidak ditemukan di rumus {formula}.")

    allowed = {target, "H", "O"}
    extra = [el for el in parsed.keys() if el not in allowed]
    if extra:
        raise ValueError(
            "Rumus mengandung unsur lain selain H, O, dan unsur target. "
            f"Unsur tambahan: {', '.join(extra)}. Untuk versi ini, butuh aturan tambahan."
        )

    nh = parsed.get("H", 0)
    no = parsed.get("O", 0)
    nx = parsed.get(target, 0)

    # Total biloks senyawa netral: nh*H + no*O + nx*X = 0
    # => nx*X = -(nh*H + no*O)
    rhs = -(nh * biloks_h + no * biloks_o)
    if nx == 0:
        raise ValueError("Jumlah atom unsur target tidak valid (0).")

    biloks_x = rhs / nx
    biloks_x_fmt = _to_number_maybe_int(biloks_x)

    detail = {
        "parsed": parsed,
        "biloks_H": biloks_h,
        "biloks_O": biloks_o,
        "atoms_H": nh,
        "atoms_O": no,
        "atoms_target": nx,
        "biloks_target": biloks_x_fmt,
        "biloks_target_raw": biloks_x,
    }
    return biloks_x_fmt, detail


# ─── Halaman valensi/biloks ────────────────────────────────────────────────
def halaman_valensi_biloks():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:2.6rem">Hitung Valensi / Biloks ⚗️</div>', unsafe_allow_html=True)
    st.markdown(
        "Kalkulator bilangan oksidasi (biloks) untuk senyawa netral dengan asumsi H = +1 dan O = −2.",
        unsafe_allow_html=False,
    )
    st.markdown('<hr style="border:none;border-top:1.5px solid rgba(44,83,100,.1);margin:1rem 0">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">🧾 Input</div>', unsafe_allow_html=True)

        rumus = st.text_input("Rumus kimia (tanpa spasi, tanpa tanda kurung)", placeholder="Contoh: H2SO4, Na2CO3, KMnO4")
        target = st.text_input("Unsur target yang ingin dicari biloksnya", placeholder="Contoh: S, C, Mn")

        st.markdown("#### Asumsi biloks")
        biloks_h = st.number_input("Biloks H", value=1.0, format="%.4g")
        biloks_o = st.number_input("Biloks O", value=-2.0, format="%.4g")

        tombol = st.button("🔎 Hitung Biloks", key="btn_biloks")

        st.caption("Catatan: Jika rumus mengandung unsur lain selain H, O, dan unsur target, perhitungan versi ini akan menolak.")

    with col2:
        st.markdown('<div class="section-header">📊 Hasil</div>', unsafe_allow_html=True)

        if tombol:
            try:
                biloks_x, detail = hitung_biloks_dari_rumus_target(rumus, target, biloks_h=biloks_h, biloks_o=biloks_o)

                parsed = detail["parsed"]
                nh = detail["atoms_H"]
                no = detail["atoms_O"]
                nx = detail["atoms_target"]

                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">Biloks {target}</div>
                    <div class="result-value">{biloks_x}</div>
                    <div style="margin-top:.5rem;font-size:.85rem;color:#4a7a90">
                        Rumus: {rumus} → {parsed}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("##### 🧮 Detail Perhitungan")
                st.markdown(
                    f"""
| Komponen | Nilai |
|---------|-------|
| H (atom) | {nh} × {biloks_h} |
| O (atom) | {no} × {biloks_o} |
| Target (atom) | {nx} × X |
| Syarat senyawa netral | Σ (biloks × jumlah atom) = 0 |
| Persamaan | {nh}({biloks_h}) + {no}({biloks_o}) + {nx}(X) = 0 |
| Hasil | X = {biloks_x} |
                    """
                )
            except Exception as e:
                st.error(f"❌ {e}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:1.6rem 1rem;color:#8ab0be">
                <div style="font-size:2rem">⚗️</div>
                <div style="margin-top:.5rem;font-size:1rem">
                    Isi rumus & unsur target, lalu klik <b>Hitung Biloks</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📌 Contoh cepat"):
        st.markdown("""
- **H2SO4**, target **S**  
  Asumsi: H=+1, O=−2 → S = +6
- **Na2CO3**, target **C**  
  Asumsi: H=+1 tidak dipakai (tidak ada H), O=−2 → C = +4
- **KMnO4**, target **Mn**  
  Unsur lain selain H,O,target? Di sini ada K dan itu akan *ditolak* oleh versi 1.
  
Jika ingin mendukung unsur seperti K/Na, versi ini perlu ditingkatkan dengan input biloks unsur tambahan.
        """)
# ─── Halaman utama ───────────────────────────────────────────────────────────
def halaman_kimia():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:2.6rem">Konversi Kimia 🧪</div>', unsafe_allow_html=True)
    st.markdown("Konversi satuan konsentrasi larutan dengan mudah dan akurat.", unsafe_allow_html=False)
    st.markdown('<hr style="border:none;border-top:1.5px solid rgba(44,83,100,.1);margin:1rem 0">', unsafe_allow_html=True)

    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<div class="section-header">⚙️ Parameter Konversi</div>', unsafe_allow_html=True)

        satuan_tujuan = st.selectbox("📌 Satuan Tujuan (yang ingin dicari)", SATUAN_LIST, key="chem_tujuan")

        asal_options = [s for s in SATUAN_LIST if s != satuan_tujuan]
        satuan_asal = st.selectbox("📐 Satuan Asal (yang kamu ketahui)", asal_options, key="chem_asal")

        nilai = st.number_input(
            f"Nilai dalam {satuan_asal}",
            min_value=0.0,
            format="%.6f",
            key="chem_nilai",
        )

        st.markdown("---")
        st.markdown("**Parameter Tambahan**")
        st.caption("Isi sesuai zat yang digunakan. Abaikan jika tidak relevan.")

        mr = 1.0
        valensi = 1
        rho = 1.0

        if needs_mr(satuan_asal, satuan_tujuan):
            mr = st.number_input("Massa Molar (Mr) zat [g/mol]", min_value=0.001, value=58.44,
                                  help="Contoh: NaCl = 58.44, H₂SO₄ = 98.08", key="chem_mr")

        if needs_valensi(satuan_asal, satuan_tujuan):
            valensi = st.number_input("Valensi / Faktor Ekuivalen", min_value=1, value=1,
                                       help="Jumlah H⁺ atau OH⁻ yang dilepaskan. HCl=1, H₂SO₄=2", key="chem_val")

        if needs_rho(satuan_asal, satuan_tujuan):
            rho = st.number_input("Densitas larutan [g/mL]", min_value=0.001, value=1.0,
                                   help="Densitas air = 1.0 g/mL", key="chem_rho")

        tombol = st.button("🔄 Konversi Sekarang", key="btn_kimia")

    with col_result:
        st.markdown('<div class="section-header">📊 Hasil Konversi</div>', unsafe_allow_html=True)

        # Info rumus
        st.markdown(
            f'<div class="info-box">ℹ️ <b>{satuan_tujuan}</b><br>{INFO[satuan_tujuan]}</div>',
            unsafe_allow_html=True,
        )

        if tombol:
            try:
                kw = {"mr": mr, "valensi": valensi, "rho": rho}
                mol_l = ke_molaritas(nilai, satuan_asal, **kw)
                hasil = dari_molaritas(mol_l, satuan_tujuan, **kw)

                # Label singkat untuk tampilan
                unit_labels = {
                    "Normalitas (N)": "N",
                    "Molaritas (M)": "M",
                    "Molalitas (m)": "m",
                    "%b/v": "% b/v",
                    "%b/b": "% b/b",
                    "ppm (mg/L)": "ppm",
                    "ppb (µg/L)": "ppb",
                }
                unit_short = unit_labels.get(satuan_tujuan, "")

                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">Hasil Konversi</div>
                    <div class="result-value">{hasil:,.6g} <span style="font-size:1.1rem;color:#4a9db5">{unit_short}</span></div>
                    <div style="margin-top:.5rem;font-size:.85rem;color:#4a7a90">
                        {nilai} {unit_labels.get(satuan_asal,'')} → {hasil:,.6g} {unit_short}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Detail via molaritas pivot
                st.markdown("---")
                st.markdown("##### 🧮 Detail Perhitungan")
                st.markdown(f"""
                | Langkah | Nilai |
                |---------|-------|
                | Nilai masukan | `{nilai} {unit_labels.get(satuan_asal,'')}` |
                | Konversi ke Molaritas (pivot) | `{mol_l:.6g} M` |
                | Konversi ke {satuan_tujuan} | `{hasil:.6g} {unit_short}` |
                | Mr digunakan | `{mr} g/mol` |
                | Valensi | `{int(valensi)}` |
                | Densitas | `{rho} g/mL` |
                """)

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 1rem;color:#8ab0be">
                <div style="font-size:3rem">⚗️</div>
                <div style="margin-top:.5rem;font-size:1rem">
                    Masukkan parameter di sebelah kiri<br>lalu klik <b>Konversi Sekarang</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabel referensi ──────────────────────────────────────────────────────
    with st.expander("📚 Referensi Rumus Konversi Konsentrasi"):
        st.markdown("""
| Satuan | Definisi | Rumus Utama |
|--------|----------|-------------|
| **Molaritas (M)** | mol zat / L larutan | M = n/V |
| **Normalitas (N)** | ekuivalen / L larutan | N = M × valensi |
| **Molalitas (m)** | mol zat / kg pelarut | m = n / kg_pelarut |
| **% b/v** | g zat / 100 mL larutan | % = (m_zat / V_lar) × 100 |
| **% b/b** | g zat / 100 g larutan | % = (m_zat / m_lar) × 100 |
| **ppm** | mg zat / L larutan | ppm = mg/L |
| **ppb** | µg zat / L larutan | ppb = µg/L |
        """)
