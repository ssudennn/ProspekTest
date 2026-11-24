import os
import json
import streamlit as st
from groq import Groq

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="ProspekTest | Akıllı İlaç Prospektüs Denetçisi",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ELEGANT & KONTRAST GARANTİLİ KLİNİK ARAYÜZ STİLİ ---
st.markdown("""
<style>
    /* Genel Aydınlık Zemin ve Kesin Koyu Yazı Rengi */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F4F7FA !important;
        color: #0F172A !important;
    }
    
    /* Radyo Butonları, Etiketler ve Paragraflar İçin Kesin Koyu Renk (Beyaz Yazı Sorunu Çözümü) */
    label, p, span, div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stRadio"] label, div[data-testid="stRadio"] p,
    div[data-testid="stSelectbox"] label, div[data-testid="stTextArea"] label {
        color: #0F172A !important;
    }

    /* Seçim Kutusu (Selectbox) ve Metin Alanı Kontrastı */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    div[data-baseweb="select"] span {
        color: #0F172A !important;
    }
    textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Üst Başlık Kartı */
    .hero-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0 0 0.4rem 0;
    }
    .hero-subtitle {
        font-size: 1.02rem;
        color: #E2E8F0 !important;
        margin: 0;
        line-height: 1.5;
    }
    .hero-subtitle b {
        color: #5EEAD4 !important;
    }

    /* İçerik Kartları */
    .clean-card {
        background-color: #FFFFFF;
        padding: 1.6rem;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        margin-bottom: 1.2rem;
    }

    /* Denetim Uyarı Kartları */
    .alert-danger {
        background-color: #FEF2F2;
        border-left: 5px solid #DC2626;
        padding: 1.1rem 1.3rem;
        border-radius: 10px;
        margin-bottom: 0.9rem;
    }
    .alert-danger b, .alert-danger span { color: #7F1D1D !important; }

    .alert-warning {
        background-color: #FFFBEB;
        border-left: 5px solid #D97706;
        padding: 1.1rem 1.3rem;
        border-radius: 10px;
        margin-bottom: 0.9rem;
    }
    .alert-warning b, .alert-warning span { color: #78350F !important; }

    .alert-info {
        background-color: #EFF6FF;
        border-left: 5px solid #2563EB;
        padding: 1.1rem 1.3rem;
        border-radius: 10px;
        margin-bottom: 0.9rem;
    }
    .alert-info b, .alert-info span { color: #1E3A8A !important; }

    .quote-box {
        background-color: #FFFFFF;
        padding: 0.7rem 0.9rem;
        border-radius: 8px;
        font-size: 0.88rem;
        font-style: italic;
        margin-top: 0.65rem;
        border: 1px dashed #94A3B8;
        color: #334155 !important;
    }
    .quote-box b { color: #0F172A !important; }

    /* TİTCK & TEB Kurumsal Panel */
    .gov-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #0D9488;
        padding: 1.5rem;
        border-radius: 12px;
        margin-top: 1.5rem;
    }

    /* Ana Buton */
    .stButton > button {
        background: linear-gradient(90deg, #0D9488 0%, #0284C7 100%) !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
    }
    .stButton > button p {
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- API ANAHTARI KONTROLÜ ---
api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

st.markdown("""
<div class="hero-box">
    <div class="hero-title">⚕️ ProspekTest</div>
    <p class="hero-subtitle">
        Yapay Zekâ İlaç Prospektüs Özetlerindeki <b>Sessiz Bilgi Kaybını</b> Denetleyen ve 
        <b>TİTCK / TEB</b> Standartlarıyla Kıyaslayan Klinik Doğrulama Platformu
    </p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.error("Sistem yapılandırma hatası: .streamlit/secrets.toml dosyasında GROQ_API_KEY bulunamadı.")
    st.stop()

client = Groq(api_key=api_key)

# --- HESAPTAKİ AKTİF MODELİ OTOMATİK BULAN FONKSİYON ---
@st.cache_data(ttl=600)
def aktif_groq_modeli_bul(_client):
    try:
        modeller = [m.id for m in _client.models.list().data]
        oncelik = [
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "qwen/qwen3-32b",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        for aday in oncelik:
            if aday in modeller:
                return aday
        for m in modeller:
            if "whisper" not in m and "guard" not in m and "tts" not in m:
                return m
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

secili_model = aktif_groq_modeli_bul(client)

# --- VERİ SEÇİM KARTI ---
with st.container():
    col_sel1, col_sel2 = st.columns([1, 2], gap="large")

    with col_sel1:
        veri_modu = st.radio(
            "İnceleme Yöntemini Seçin:",
            ["TİTCK Veri Setinden Seç (20 İlaç)", "Kendi Prospektüs Metnini Yapıştır"]
        )

    prospektus_metni = ""
    secilen_ilac = "Özel Metin"

    with col_sel2:
        if veri_modu == "TİTCK Veri Setinden Seç (20 İlaç)":
            ilac_klasoru = "ilaclar"
            if os.path.exists(ilac_klasoru):
                dosyalar = sorted([f for f in os.listdir(ilac_klasoru) if f.endswith(".txt")])
                if dosyalar:
                    secilen_dosya = st.selectbox(
                        "Resmi TİTCK Kullanma Talimatı Seçin:",
                        dosyalar,
                        format_func=lambda x: x.replace(".txt", "").replace("_", " ").upper()
                    )
                    secilen_ilac = secilen_dosya.replace(".txt", "").replace("_", " ").upper()
                    with open(os.path.join(ilac_klasoru, secilen_dosya), "r", encoding="utf-8") as f:
                        prospektus_metni = f.read()
                else:
                    st.warning("'ilaclar' klasöründe .txt dosyası bulunamadı.")
            else:
                st.warning("'ilaclar' klasörü bulunamadı.")
        else:
            prospektus_metni = st.text_area(
                "TİTCK Kullanma Talimatı (KT) metnini buraya yapıştırın:",
                height=150,
                placeholder="İlacın 'Kullanmadan önce dikkat edilmesi gerekenler' ve 'Nasıl kullanılır' bölümlerini yapıştırın..."
            )

    with st.expander("📄 Resmi TİTCK Kaynak Metnini Görüntüle"):
        st.text(prospektus_metni if prospektus_metni else "Metin bekleniyor...")

    analiz_baslat = st.button("🔍 Yapay Zekâ Özetini Oluştur ve TİTCK Metniyle Denetle", use_container_width=True)

# --- ANALİZ VE DENETİM SÜRECİ ---
if analiz_baslat:
    if not prospektus_metni.strip():
        st.warning("Lütfen önce bir ilaç seçin veya prospektüs metni yapıştırın.")
    else:
        with st.spinner(f"Klinik Denetçi AI ({secili_model}) prospektüsü analiz ediyor ve TİTCK kurallarıyla kıyaslıyor..."):
            sistem_promptu = """
            Sen Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK) ve Türk Eczacıları Birliği (TEB) akılcı ilaç kullanımı standartlarına göre çalışan uzman bir denetim sistemisin.
            
            Görevin iki aşamalıdır:
            1. Önce sıradan bir sohbet botunun hastaya vereceği gibi kısa, akıcı, 4 maddelik yüzeysel bir "standart_ai_ozeti" oluştur (bu özet tipik olarak bazı kritik besin/ilaç etkileşimlerini ve ince kullanım detaylarını atlar).
            2. Ardından bu yüzeysel özeti ORİJİNAL TİTCK PROSPEKTÜSÜ ile satır satır kıyasla ve özetin sessizce atladığı veya eksik bıraktığı hayati bilgileri tespit et.

            Çıktıyı SADECE aşağıdaki geçerli JSON formatında ver:
            {
              "standart_ai_ozeti": "• Madde 1...\\n• Madde 2...\\n• Madde 3...\\n• Madde 4...",
              "risk_skoru": 85,
              "genel_yorum": "Standart özet akıcı görünse de hayati besin/ilaç etkileşimlerini ve kullanım kısıtlamalarını sessizce atlamıştır.",
              "bulgular": [
                {
                  "tip": "ATLANAN_RISK",
                  "baslik": "Kısa ve net uyarı başlığı",
                  "aciklama": "Yapay zekâ özetinin bu bilgiyi nasıl atladığı ve hasta için doğuracağı klinik risk.",
                  "kaynak_cumle": "Orijinal TİTCK metninden birebir alıntılanan dayanak cümle."
                }
              ]
            }

            'tip' alanı sadece şu üç değerden biri olmalıdır:
            - "ATLANAN_RISK": Özette hiç geçmeyen besin/içecek etkileşimi (greyfurt, süt, potasyum, çay/kahve, alkol vb.), ilaç etkileşimi, hamilelik veya hastalık yasağı.
            - "CARPITILAN_BILGI": Özette eksik/belirsiz geçilen kullanım kuralı (aç/tok durumu, tabletin bölünmemesi/çiğnenmemesi, güneş hassasiyeti vb.).
            - "TEB_TITCK_UYARI": Hastanın ilacı güvenli kullanması için TİTCK/TEB kapsamında mutlaka bilmesi gereken kritik uyarı.
            En az 3, en fazla 5 bulgu üret. Tüm metinler kusursuz Türkçe olmalıdır.
            """

            try:
                yanit = client.chat.completions.create(
                    model=secili_model,
                    messages=[
                        {"role": "system", "content": sistem_promptu},
                        {"role": "user", "content": f"ORİJİNAL TİTCK KULLANMA TALİMATI:\n\n{prospektus_metni[:15000]}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.15
                )
                rapor = json.loads(yanit.choices[0].message.content)

                st.divider()
                st.markdown(f"### 📊 {secilen_ilac} — Denetim ve Tutarlılık Analizi")

                m1, m2, m3 = st.columns(3)
                skor = rapor.get("risk_skoru", 80)
                m1.metric("Sessiz Bilgi Kaybı Risk Skoru", f"{skor} / 100", delta="Yüksek Eksiklik Riski" if skor >= 60 else "Orta Risk", delta_color="inverse")
                m2.metric("Tespit Edilen Eksik / Uyarı", f"{len(rapor.get('bulgular', []))} Kritik Bulgu")
                m3.metric("Referans Kaynak", "TİTCK Resmi KT & TEB")

                sol_kolon, sag_kolon = st.columns([1, 1.35], gap="large")

                with sol_kolon:
                    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
                    st.subheader("🤖 Standart AI Özeti (Sanı)")
                    st.caption("Sıradan bir yapay zekâ asistanının hastaya sunduğu yüzeysel özet:")
                    st.write(rapor.get("standart_ai_ozeti", ""))
                    st.divider()
                    st.markdown(f"**Denetçi Değerlendirmesi:** {rapor.get('genel_yorum', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with sag_kolon:
                    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
                    st.subheader("🛡️ TİTCK Kaynaklı Denetim Bulguları (Hakikat)")
                    st.caption("Yapay zekâ özetinde atlanan veya eksik bırakılan kritik noktalar:")

                    for b in rapor.get("bulgular", []):
                        tip = b.get("tip", "ATLANAN_RISK")
                        if tip == "ATLANAN_RISK":
                            st.markdown(f"""
                            <div class="alert-danger">
                                <b>🚨 ATLANAN KRİTİK RİSK: {b.get('baslik')}</b><br>
                                <span style="font-size:0.95rem;">{b.get('aciklama')}</span>
                                <div class="quote-box">📌 <b>Orijinal TİTCK Metni:</b> "{b.get('kaynak_cumle')}"</div>
                            </div>
                            """, unsafe_allow_html=True)
                        elif tip == "CARPITILAN_BILGI":
                            st.markdown(f"""
                            <div class="alert-warning">
                                <b>⚠️ EKSİK / BELİRSİZ BİLGİ: {b.get('baslik')}</b><br>
                                <span style="font-size:0.95rem;">{b.get('aciklama')}</span>
                                <div class="quote-box">📌 <b>Orijinal TİTCK Metni:</b> "{b.get('kaynak_cumle')}"</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="alert-info">
                                <b>ℹ️ TİTCK / TEB KULLANIM UYARISI: {b.get('baslik')}</b><br>
                                <span style="font-size:0.95rem;">{b.get('aciklama')}</span>
                                <div class="quote-box">📌 <b>Orijinal TİTCK Metni:</b> "{b.get('kaynak_cumle')}"</div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Bir bağlantı sorunu oluştu: {e}")

# --- ALT BÖLÜM: KURUMSAL TİTCK & TEB UYARI REHBERİ ---
st.markdown("""
<div class="gov-card">
    <h4 style="margin-top:0; color:#0F172A !important;">🏛️ TİTCK ve Türk Eczacıları Birliği (TEB) Akılcı İlaç Kullanımı Uyarıları</h4>
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top:1rem;">
        <div style="background:#F8FAFC; padding:1rem; border-radius:8px; border:1px solid #E2E8F0;">
            <b style="color:#0F172A !important;">🥤 İçecek ve Besin Etkileşimi (TEB)</b><br>
            <span style="font-size:0.9rem; color:#334155 !important;">İlaçları yalnızca bir bardak su ile için. Greyfurt suyu, süt ürünleri, çay ve kahve ilacın emilimini bozabilir veya toksik etki yaratabilir.</span>
        </div>
        <div style="background:#F8FAFC; padding:1rem; border-radius:8px; border:1px solid #E2E8F0;">
            <b style="color:#0F172A !important;">💊 Tablet Formunu Bozmayın (TEB)</b><br>
            <span style="font-size:0.9rem; color:#334155 !important;">'Enterik kaplı' veya 'kontrollü salımlı' ibaresi taşıyan ilaçları doktor veya eczacı önermedikçe bölmeyin, ezmeyin ve çiğnemeyin.</span>
        </div>
        <div style="background:#F8FAFC; padding:1rem; border-radius:8px; border:1px solid #E2E8F0;">
            <b style="color:#0F172A !important;">⏱️ Tedavi Süresine Uyun (TİTCK)</b><br>
            <span style="font-size:0.9rem; color:#334155 !important;">Özellikle antibiyotiklerde kendinizi iyi hissetseniz bile hekimin belirttiği tedavi süresi tamamlanmadan ilacı kesmeyin.</span>
        </div>
        <div style="background:#F8FAFC; padding:1rem; border-radius:8px; border:1px solid #E2E8F0;">
            <b style="color:#0F172A !important;">📢 Yan Etki Bildirimi (TİTCK - TÜFAM)</b><br>
            <span style="font-size:0.9rem; color:#334155 !important;">Prospektüste yer alan veya almayan beklenmeyen bir etki görüldüğünde hekiminize başvurun ve TÜFAM'a bildirin.</span>
        </div>
    </div>
    <p style="margin-top:1.2rem; margin-bottom:0; font-size:0.85rem; color:#475569 !important;">
        <b style="color:#0F172A !important;">Etik ve Yasal Sorumluluk Reddi:</b> ProspekTest tıbbi tanı, tedavi veya reçete önerisi sunmaz. Yapay zekâ özetlerinin orijinal TİTCK Kullanma Talimatları ile tutarlılığını denetleyen akademik bir doğrulama aracıdır.
    </p>
</div>
""", unsafe_allow_html=True)