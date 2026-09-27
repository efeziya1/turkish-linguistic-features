"""docs/dogrulama-raporu.md dosyasını üretir (T31).

Her öznitelik için, dayandığı kaynağın yayımladığı sayıyla karşılaştırmasını
tablolar. Kapsam listesi registry'den üretilir — elle tutulmaz, yani hiçbir
öznitelik rapordan kaçamaz.

Kullanım::

    python scripts/dogrulama_raporu.py

Bu dosya elle DÜZENLENMEZ. Karşılaştırma eklemek için aşağıdaki
``KARSILASTIRMALAR`` tablosuna satır yazın; testler
(``tests/test_kaynak_esligi.py``) aynı tabloyu okuyor, yani rapor ile
testler ayrışamaz.
"""

from __future__ import annotations

import math
from pathlib import Path

import turkish_linguistic_features as tlf

# Kapsam ölçülürken kullanılan örnek metinler. İçerikleri önemsiz —
# yalnız taban şemanın bütün anahtarlarını üretmeye yarıyorlar.
ORNEK_METIN = {
    "tr": "Bu bir deneme metnidir. İkinci cümle burada duruyor, üçüncüsü de geldi.",
    "en": "This is a test sentence. A second one is here, and a third follows.",
}

# ── Kalyoncu & Memiş (2024) Ek-1'deki üç okunabilirlik örneği ─────────
#
# Telif: bunlar makalede yayımlanmış 100 kelimelik örneklerdir ve doğrulama
# amacıyla, hem makale hem özgün ders kitabı gösterilerek alıntılanmıştır.
# Kaynak metinlerin tamamı depoya girmez.

# Metin 1 — Başkaya (2019) s.26, aktaran Kalyoncu & Memiş (2024) Ek-1
METIN_1 = (
    'Yakın zamana kadar köylerde yaşamış veya hâlen yaşamakta olan kişilerin '
    'anılarında dün gibi yaşayan köy odaları geleneği, Türk konukseverliğinin '
    'en iyi örnekleri arasındadır. Köylerdeki köy odalarının konukları, bir '
    'yerden bir yere gitmekte olan yolcular olduğu kadar, köye ticaret amacı '
    'ile gelen veya zanaat sahibi insanlar da olabilmekteydi. Çerçiler, testi '
    'bardak satanlar, ürettiği malı değiş yoluyla veya para ile ticaret '
    'yapanlar, halatçılar, gezici kalaycılar, orakçılar vb. olmak üzere köye '
    'bir nedenle gelenler istediği kadar bu köy odalarında konuk olarak '
    "kalabiliyorlardı. Anadolu'nun birçok köyünde neredeyse her sülalenin köy "
    'odası vardı. Bu köy odaları ya o sülalelerin ya da önde gelen büyüğünün '
    'adıyla anılıyordu.'
)

# Metin 2 — İnan (2023) s.143, aktaran Kalyoncu & Memiş (2024) Ek-1
METIN_2 = (
    'Atatürk, okul programlarıyla bizzat meşgul olur, okutulan kitapları '
    'gözden geçirir ve özellikle tarih derslerinin, ulusun bilincini '
    'yükselteceğine inanır ve Türklük dünyasının tarihini bir bütün olarak, '
    'uygarlık unsurlarına daha çok önem verilerek incelenmesini ve '
    'okutulmasını isterdi. O, Türk büyüklerinden Alparslanlar, Fatihler, '
    'Yavuz ve Kanunilerin hayranı olmakla beraber, bizzat uygarlık eserleri '
    'vücuda getirmiş olan Mimar Sinanlar ve Piri Reislere de ayrı bir değer '
    'verirdi. Çünkü devlet başında ordular yönetmiş kişiler, tarihte Türk '
    'şanını ne kadar yükseltmişlerse diğerleri de Türk dünyasına ölmez '
    'eserler vermişlerdir. Atatürk, her devirde Türk’ün uygarlık yapısına '
    'hizmet eden her bireyin değerini takdir etmenin zorunlu olduğunu prensip '
    'olarak kabul etmişti.'
)

# Metin 3 — Baykent (2017) s.506-507, aktaran Kalyoncu & Memiş (2024) Ek-1
METIN_3 = (
    'Anlam, türetilmiş niyetliliğin bir biçimidir. Konuşan kişinin asli ya da '
    'içsel niyetliliği sözcüklere, cümlelere, işaretlere, sembollere vs. '
    'aktarılmıştır. Anlamlı bir biçimde dile getirilirlerse, bu sözcükler, '
    'cümleler, işaretler ve semboller artık konuşan kişinin düşüncelerinden '
    'türetilmiş niyetliliğe sahiptirler. Sadece uzlaşıma dayalı dilbilimsel '
    'anlam taşımakla kalmazlar, konuşanın kastettiği anlamı da taşırlar. Bir '
    'dilin sözcüklerinin ve cümlelerinin uzlaşımsal niyetliliği, konuşan kişi '
    'tarafından bir söz edimi icra etmek için kullanılabilir. Konuşan kişi '
    'bir söz edimi yerine getirirse, bu semboller üzerine kendi niyetliliğini '
    'yükler. Fakat konuşan kişi bunu tam olarak nasıl yapmaktadır? Daha önce '
    'niyetliliği ele alıp tartışırken yerine getirilme şartlarının açıklamaya '
    'çalıştığım anlamda, niyetliliği anlamak için anahtar mahiyetinde '
    'olduğunu görmüştük.'
)

# ── durum sözlüğü ─────────────────────────────────────────────────────
BIREBIR = "birebir"
SAPMA = "belgelenmis_sapma"
ACIK = "acik"                       # doğrulanabilir ama kaynakta örnek yok
KAYNAK_YOK = "kaynak_yok"           # saf tanım — aday değil
SEMA = "etiket_semasi"              # dış şemanın kategorisi — aday değil
TUREV = "turev"                     # formül kaynaktan, uygulama bizden
UYUSMAZLIK = "uyusmazlik"

_SIMGE = {BIREBIR: "✅", SAPMA: "🟡", ACIK: "🔍", KAYNAK_YOK: "⚪",
          SEMA: "⚫", TUREV: "🔧", UYUSMAZLIK: "❌"}

# Doğrulama ADAYI olan durumlar — gerçek payda bu. Aday olmayanlar (saf
# tanım, etiket şeması, türev) ayrı sayılır; hepsini tek kovada toplamak
# raporu olduğundan kötü gösteriyordu (2026-09-24, Efe).
ADAY_DURUMLAR = (BIREBIR, SAPMA, ACIK, UYUSMAZLIK)
ADAY_OLMAYAN = (KAYNAK_YOK, SEMA, TUREV)

# Formülü bir kaynaktan gelen ama **uygulaması bu kütüphaneye ait** ölçüler.
# Karşılaştırılacak yayımlanmış bir sayı yok ve olamaz: ölçüyü biz tanımladık,
# kimse onu yayımlamadı. ``long_sent_ratio``'yu kendi kalibrasyonumuza karşı
# sınamak kendi cevabımıza bakıp sınav olmak demekti (2026-09-24, Efe).
#
# Liste elle tutulur, künye metninden regex'le çıkarılmaz — künye düz yazıdır
# ve bir sözcük değişince sınıflandırma sessizce kayar.
# ``test_turev_kunyeleri_isaretli`` her birinin künyesinin bunu hâlâ açıkça
# söylediğini sınıyor.
TUREV_ANAHTARLARI = frozenset({
    "entropy_std",              # Shannon'ın entropisi, parçalar arası std bizim
    "punct_entropy",            # Shannon'ın formülü, noktalamaya uygulama bizim
    "sent_len_entropy",         # Shannon'ın formülü, cümle uzunluğuna bizim
    "short_sent_ratio",         # eşik kendi kalibrasyonumuzdan
    "long_sent_ratio",          # eşik kendi kalibrasyonumuzdan
    "polysyllabic_word_ratio",  # SMOG'un girdisinin oran biçimi, McLaughlin'in değil
})

# Bir ÖLÇÜ değil, dış bir ETİKET ŞEMASININ kategorisini sayan öznitelikler.
# de Marneffe'in makalesi "morph_case_loc = 0,07" diye bir sayı basmaz ve
# basamaz — şema kategorileri tanımlar, ölçüm yayımlamaz. Bu satırlar
# doğrulama adayı değildir.
#
# Ölçüt künyenin BAŞLANGICI: künye şemayla başlıyorsa satır şema
# kategorisidir. Şemayı sonradan anan künyeler (``suffix_bigram_entropy``:
# "Shannon (1948) — the entropy formula; Zeyrek …") gerçek bir ölçüdür ve
# açık listede kalır.
SEMA_ONEKLERI = ("de Marneffe et al. (2021)", "Zeyrek (a Python port")

# Birebir sayılmak için gereken yakınlık. Kaynaklar ara değerleri yuvarlayarak
# bastığı için mutlak eşitlik beklenmiyor.
TOLERANS = 0.05


# Kanıtın türü. Aradaki fark önemli: uçtan uca karşılaştırma kaynağın
# **metnini** boru hattından geçirir, yani tokenizasyonu, hecelemeyi ve cümle
# bölmeyi de sınar. Formül karşılaştırması fonksiyona girdileri doğrudan
# verir — formülü doğrular, boru hattını değil.
UCTAN_UCA = "end-to-end"
FORMUL = "formula"


class Karsilastirma:
    """Bir anahtarın kaynaktaki yayımlanmış değeriyle karşılaştırması."""

    def __init__(self, kaynak: str, ornek: str, beklenen: float,
                 hesapla, gerekce: str = "", tur: str = UCTAN_UCA) -> None:
        self.kaynak = kaynak
        self.ornek = ornek
        self.beklenen = beklenen
        self.hesapla = hesapla          # () -> float
        self.gerekce = gerekce          # sapma varsa NEDEN
        self.tur = tur                  # UCTAN_UCA | FORMUL


def _kalyoncu_metin(no: int) -> dict[str, float]:
    """Ek-1'deki metinlerden birinin özniteliklerini verir."""
    return tlf.analyze((METIN_1, METIN_2, METIN_3)[no - 1], lang="tr")


_KM_ONBELLEK: dict[int, dict[str, float]] = {}


def _km(no: int, anahtar: str) -> float:
    if no not in _KM_ONBELLEK:
        _KM_ONBELLEK[no] = _kalyoncu_metin(no)
    return _KM_ONBELLEK[no][anahtar]


_KM = "Kalyoncu & Memiş (2024) Table 9"


def _bezirci_e7(h3: float, h4: float, h5: float, h6: float) -> float:
    """Bezirci & Yılmaz denk. (7): hece sayımlarından ara değer."""
    return h3 * 0.84 + h4 * 1.5 + h5 * 3.5 + h6 * 26.25


def _bezirci_e9(oks: float, e7: float) -> float:
    """Bezirci & Yılmaz denk. (9): karekök adımı.

    Tablo 5 tam olarak bunu tablolıyor — ``E7`` makalenin bastığı ara değer,
    yeniden hesaplanmıyor. Katsayı adımını Tablo 3 satırları sınıyor.
    """
    return math.sqrt(oks * e7)


def _atesman(hece_basina: float, sozcuk_basina: float) -> float:
    """Ateşman denk. (2), doğrudan."""
    return 198.825 - 40.175 * hece_basina - 2.610 * sozcuk_basina


def _jing_liu(alan: str) -> float:
    """Jing & Liu (2015) s.164 Figure 3: 'Mr. Nixon was to leave China today'."""
    from turkish_linguistic_features.features.dependency import dependency_features
    cumle = [(0, "PROPN", "flat", 1), (1, "PROPN", "nsubj", 2),
             (2, "VERB", "root", 2), (3, "PART", "mark", 2),
             (4, "VERB", "xcomp", 3), (5, "PROPN", "obj", 4),
             (6, "NOUN", "obl", 4)]
    return dependency_features([cumle])[alan]


# ── QUITA örnek metinlerinin TAM sıklık dağılımı ──────────────────────
#
# Kaynak: QUITA kılavuzu §15.3 "Word list of Text 1 and Text 2" (s.99-104).
# Text 1 = Nineteen Eighty-Four'ın ikinci paragrafı, Text 2 = Animal Farm'ın
# ilk paragrafları (§15.1, §15.2). Kılavuzun kendi ölçümleri bu iki metne ait.
#
# **Burada yalnız SAYILAR duruyor** — kelime yok, metin yok. Frekans dağılımı
# türetilmiş sayısal bir veridir; ondan metin geri kurulamaz. Telifli eser
# depoya girmiyor (2026-09-24, Efe kararı).
#
# Tokenizasyon bir kez doğrulandı: kılavuzun metinleri
# ``re.findall(r"[a-z]+", metin.lower())`` ile tokenlandığında N=179/202 ve
# V=119/121 çıkıyor — kılavuzun bastığı değerlerin aynısı. Kural tire ve
# kesme işaretini böler (``forty-five`` → ``forty`` + ``five``); kılavuzun
# kelime listesinde hiç tireli ya da kesmeli madde yok.
# Aynı veri ``tests/test_frequency_structure.py``'de de duruyor
# (``ORWELL_1984`` / ``ANIMAL_FARM``); ``test_quita_spektrumlari_ayni``
# ikisinin ayrışmadığını sınıyor.
def _rle(ciftler: list[tuple[int, int]]) -> list[int]:
    """(frekans, kaç tip) çiftlerini düz listeye açar."""
    return [f for f, n in ciftler for _ in range(n)]


_T1 = _rle([(16, 1), (7, 3), (5, 2), (3, 4), (2, 11), (1, 98)])   # N=179, V=119
_T2 = _rle([(20, 1), (9, 1), (8, 1), (7, 1), (4, 5), (3, 6),
            (2, 14), (1, 92)])                                    # N=202, V=121


def _quita_spektrum(bas: list[int], n: int = 0):
    """Sıklık dizisini numpy dizisine çevirir (azalan sırada)."""
    import numpy as np
    return np.array(sorted(bas, reverse=True), dtype=float)


def _h_point(bas: list[int], n: int) -> float:
    from turkish_linguistic_features.features.frequency_structure import h_point
    return h_point(_quita_spektrum(bas, n))


def _r1(bas: list[int], n: int) -> float:
    from turkish_linguistic_features.features.frequency_structure import (
        h_point,
        vocab_richness_r1,
    )
    f = _quita_spektrum(bas, n)
    return vocab_richness_r1(f, n, h_point(f))["vocab_richness_r1"]


def _liu_mdd() -> float:
    """Liu (2008) denk. (1) örneği: 'I actually live in Beijing' → 5/4."""
    from turkish_linguistic_features.features.dependency import dependency_features
    cumle = [(0, "PRON", "nsubj", 2), (1, "ADV", "advmod", 2),
             (2, "VERB", "root", 2), (3, "ADP", "case", 2),
             (4, "PROPN", "obl", 3)]
    return dependency_features([cumle])["arc_len_mean"]


def _mtld_kismi_faktor() -> float:
    """McCarthy & Jarvis (2010) s.385 — kısmi faktörün yayımlanmış örneği.

    Makale şunu yazıyor: ".887 forms **40.4%** of the range between 1.00 and
    the full factor of .720". 47 ayrı tip + aynı tipten 6 tekrar = 53 token
    dizisinde TTR hiç 0,72'ye inmiyor, yani tam faktör kapanmıyor; geriye
    yalnız kısmi faktör kalıyor. MTLD = token / faktör olduğundan faktör
    token/MTLD ile geri okunuyor. Üretim kodu (`_mtld_tek_yon`) çalışıyor,
    formül burada yeniden yazılmıyor.
    """
    from turkish_linguistic_features.features.lexical import _mtld_tek_yon
    tokenlar = [f"w{i}" for i in range(47)] + ["w0"] * 6
    return len(tokenlar) / _mtld_tek_yon(tokenlar, 0.72)


def _cl_sinif(cloze_yuzde: float) -> float:
    """Coleman & Liau (1975) s.284: cloze % → sınıf düzeyi."""
    return -27.4004 * (cloze_yuzde / 100) + 23.06395


_CL_METIN = ("Alpha beta gamma delta epsilon zeta. "
             "Eta theta iota kappa lambda mu nu.")


def _cl_iki_denklem() -> float:
    """Makalenin İKİ denklemi ardışık uygulanınca çıkan sınıf düzeyi.

    Coleman & Liau önce cloze % kestiriyor (``141.8401 - .214590 L +
    1.079812 S``), sonra Tablo 1'in altındaki denklemle sınıfa çeviriyor.
    Bizim ``coleman_liau`` bu ikisinin birleşimi — makalede o hâliyle
    basılmıyor. L ve S üretim kodunun kendi sayımından alınıyor ki iki yol
    aynı girdiyi görsün.
    """
    from turkish_linguistic_features.features.readability import (
        _harf_sayisi, _CUMLE_SONU, cumle_sayisi, kelime_birimleri)
    kelimeler, _ = kelime_birimleri(_CL_METIN, "en")
    cumle = cumle_sayisi(_CL_METIN.split(), _CUMLE_SONU["varsayilan"], "en")
    L = 100 * sum(_harf_sayisi(k) for k in kelimeler) / len(kelimeler)
    S = 100 * cumle / len(kelimeler)
    return _cl_sinif(141.8401 - 0.214590 * L + 1.079812 * S)


def _quita(anahtar: str, bas: list[int]) -> float:
    """QUITA örnek metninin sıklık dağılımından bir göstergeyi hesaplar.

    Bütün göstergeler yalnız sıklık dağılımına bakar, metne değil — bu
    yüzden kılavuzun yayımladığı dağılım girdi olarak yeterlidir.
    """
    import numpy as np

    import turkish_linguistic_features.features.frequency_structure as F
    from turkish_linguistic_features.features.lexical import shannon_entropy

    fr = _quita_spektrum(bas)
    N, V = int(fr.sum()), len(fr)
    h = F.h_point(fr)
    if anahtar == "h_point":
        return h
    if anahtar == "ttr":
        return V / N
    if anahtar == "lambda_pa":
        return F.lambda_pa(F.curve_length(fr)["curve_length"], N)["lambda_pa"]
    if anahtar == "writers_view_alpha":
        return F.writers_view(int(fr[0]), V, h)["writers_view_alpha"]
    if anahtar == "vocab_richness_r1":
        return F.vocab_richness_r1(fr, N, h)["vocab_richness_r1"]
    if anahtar == "vocab_richness_r4":
        return F.vocab_richness_r4(fr, N, V)["vocab_richness_r4"]
    if anahtar == "repeat_rate":
        return F.repeat_rate(fr, N)["repeat_rate"]
    if anahtar == "rr_mcintosh":
        rr = F.repeat_rate(fr, N)["repeat_rate"]
        return F.rr_mcintosh(rr, V)["rr_mcintosh"]
    if anahtar == "hapax_percentage":
        return float(np.sum(fr == 1)) / N
    if anahtar == "gini_coef":
        return F.gini_coef(fr, N, V)["gini_coef"]
    if anahtar == "curve_length":
        return F.curve_length(fr)["curve_length"]
    if anahtar == "curve_length_r":
        return F.curve_length_indicator(fr, h)["curve_length_r"]
    if anahtar == "adjusted_modulus":
        return F.adjusted_modulus(int(fr[0]), V, h, N)["adjusted_modulus"]
    if anahtar == "entropy":
        return shannon_entropy(fr)
    raise KeyError(anahtar)


def _quita_activity(fiil: int, sifat: int) -> float:
    """QUITA §6.2.2 ``Q = V / (V + A)`` — fiil ve sıfat **tip** sayılarından.

    Kılavuz sayıları veriyor (Text 1: 26 fiil / 14 sıfat → 0,65; Text 2:
    35 / 8 → 0,814) ama hangi kelimelerin fiil/sıfat sayıldığını listelemiyor
    ve kendi POS etiketleyicisini (NLTK) kullanıyor. Bu satır **formülü**
    sınıyor, etiketlemeyi değil.
    """
    from turkish_linguistic_features.features.syntactic import activity_ratio
    pos = [("v", "VERB")] * fiil + [("a", "ADJ")] * sifat
    return activity_ratio(pos)["activity_ratio"]


def _cl_bizim() -> float:
    """Aynı metin üretim boru hattından geçince çıkan ``coleman_liau``."""
    from turkish_linguistic_features.features.readability import (
        general_readability_formulas)
    return general_readability_formulas(
        _CL_METIN, _CL_METIN.split(), "en")["coleman_liau"]


# ── Kincaid ve ark. (1975) Ek A — 18 test pasajı ──────────────────────
#
# Ek A (basılı s.23-30) pasajların METNİNİ, Tablo 1 (s.8-9) ve Tablo 2
# (s.12) o pasajlar için kaynağın hesapladığı DEĞERLERİ basıyor. İkisi ayrı
# yerlerde; doğrulamak isteyen tabloya bakmalı, Ek A'ya değil.
#
# Telif: ABD Donanması teknik raporu = ABD hükümet eseri, kamu malı.
# Pasajlar tests/veri/kincaid/ altında; gerekçe o dizinin README'sinde.

_KINCAID_VERI = Path(__file__).resolve().parents[1] / "tests" / "veri" / "kincaid"

# Tablo 1, basılı s.8-9 — ESKİ formüller. (ARI, Flesch sınıf bandı)
_KINCAID_T1_ARI = {
    1: 10.6, 2: 20.3, 3: 13.3, 4: 8.8, 5: 9.5, 6: 12.4, 7: 12.7, 8: 16.4,
    9: 9.7, 10: 13.1, 11: 7.8, 12: 16.7, 13: 13.4, 14: 12.0, 15: 9.7,
    16: 13.5, 17: 10.4, 18: 10.9,
}
_KINCAID_T1_BANT = {
    1: "8-9", 2: "16+", 3: "13-16", 4: "8-9", 5: "8-9", 6: "13-16",
    7: "13-16", 8: "13-16", 9: "7", 10: "13-16", 11: "8-9", 12: "10-12",
    13: "10-12", 14: "13-16", 15: "8-9", 16: "16+", 17: "10-12", 18: None,
}
# Tablo 2, basılı s.12 — YENİ formüller, "Flesch" sütunu = FKGL.
_KINCAID_T2_FKGL = {
    1: 9.7, 2: 16.7, 3: 12.7, 4: 8.2, 5: 7.1, 6: 12.3, 7: 11.7, 8: 14.7,
    9: 8.0, 10: 11.7, 11: 8.1, 12: 11.8, 13: 10.0, 14: 12.5, 15: 8.4,
    16: 13.8, 17: 9.3, 18: 6.6,
}
# Kaynağın kendi bastığı ortalamalar (Tablo 1 ve Tablo 2'nin alt satırı).
_KINCAID_ORT_ARI = 12.3
_KINCAID_ORT_FKGL = 10.7

# Flesch (1948) kendi sınıf tablosu: bant → FRE aralığı.
_FRE_BANDI = {"5": (90, 100), "6": (80, 90), "7": (70, 80), "8-9": (60, 70),
              "10-12": (50, 60), "13-16": (30, 50), "16+": (0, 30)}

_KINCAID_ONBELLEK: dict[int, dict[str, float]] = {}


def _kincaid_oznitelikler() -> dict[int, dict[str, float]]:
    """18 pasajın öznitelikleri; 18 ``analyze()`` çağrısı bir kez yapılır.

    Başlık satırı (``passage_NN.title.txt``) sayıma **dahil edilmiyor**.
    Kaynak bunu söylemiyor; ölçüldü: başlıklı varyant 18 pasajın hepsinde
    daha kötü (ARI ortalama mutlak fark 1,20 vs 0,54).
    """
    if not _KINCAID_ONBELLEK:
        for n in range(1, 19):
            metin = (_KINCAID_VERI / f"passage_{n:02d}.txt").read_text(
                encoding="utf-8").strip()
            oz = tlf.analyze(metin, lang="en")
            _KINCAID_ONBELLEK[n] = {
                "ari": oz["ari"], "fkgl": oz["flesch_kincaid_grade"],
                "fre": oz["flesch_reading_ease"],
                "vurus": float(sum(len(p) for p in metin.split())),
                "kelime": float(len(metin.split())),
            }
    return _KINCAID_ONBELLEK


def _kincaid_ort(alan: str) -> float:
    """18 pasajın ortalaması — kaynağın bastığı ortalamayla kıyaslanır."""
    d = _kincaid_oznitelikler()
    return sum(d[n][alan] for n in d) / len(d)


def _kincaid_en_buyuk_fark(alan: str, yayimlanan: dict[int, float]) -> tuple[int, float]:
    """En büyük mutlak farkı veren pasaj ve farkın büyüklüğü."""
    d = _kincaid_oznitelikler()
    n, f = max(((n, d[n][alan] - yayimlanan[n]) for n in d),
               key=lambda x: abs(x[1]))
    return n, f


_KINCAID_GEREKCE_ARI = (
    "Kaynağın sayıları 1975'te daktiloya takılı mekanik bir sayaçla **elle** "
    "üretildi (Ek B, ARI talimatı). 18 pasajın 17'sinde, kaynağın ARI'sını "
    "verecek vuruş sayısı bizim saydığımızın 0,996-1,041 katı — yani birkaç "
    "karakterlik fark. Pasaj 2 aykırı (oran 1,145) ve kaynağın kendi iki "
    "sayısı orada çelişiyor: Tablo 1'in ARI 20,3'ü vuruş/kelime 6,269 "
    "gerektiriyor, metnin gerçek değeri 5,475; üstelik o ARI'nın ima ettiği "
    "kelime/cümle FKGL'yi 18,69 yapıyor, oysa Tablo 2 16,7 basmış. Bizim "
    "vuruş tanımımız ayrıca sınandı: boşluğu sayıma katmak farkı 0,54'ten "
    "4,24'e çıkarıyor, yani boşluksuz sayım doğru."
)
_KINCAID_GEREKCE_FKGL = (
    "Aynı elle sayım kaynağı. Pasaj başına sapma 18'in 15'inde 0,6'nın "
    "altında; pasaj 12 aykırı (-4,28) ve o pasaj FRE bandını da tutturmuyor, "
    "yani sapma tek bir pasajda yoğunlaşıyor. Ortalamalar arasındaki fark "
    "0,34 sınıf düzeyi — okunabilirlik sınıflandırmasını değiştirmeyecek "
    "kadar küçük."
)


# Anahtar → karşılaştırma listesi. Bir anahtarın birden çok kaynak örneği
# olabilir; hepsi rapora ayrı satır olarak girer.
KARSILASTIRMALAR: dict[str, list[Karsilastirma]] = {
    "atesman": [
        Karsilastirma("Ateşman (1997)", _KM + " · Text 2", 23.094,
                      lambda: _km(2, "atesman")),
        Karsilastirma("Ateşman (1997) p.74", "calibration: easiest text", 100.0,
                      lambda: _atesman(2.2, 4), tur=FORMUL),
        Karsilastirma("Ateşman (1997) p.74", "calibration: hardest text", 0.0,
                      lambda: _atesman(3.0, 30), tur=FORMUL),
    ],
    "cetinkaya_uzun": [
        Karsilastirma("Çetinkaya (2010)", _KM + " · Text 2", 23.084,
                      lambda: _km(2, "cetinkaya_uzun")),
    ],
    "bezirci_yilmaz": [
        Karsilastirma("Bezirci & Yılmaz (2010)", _KM + " · Text 2",
                      math.sqrt(925.5625), lambda: _km(2, "bezirci_yilmaz"),
                      "The paper rounded its H6 intermediate value; the difference is "
                      "0.031 and both values fall in the same readability class (academic, 16+)."),
        # denk. (9) — karekök adımı. E7 makalenin bastığı ara değer.
        Karsilastirma("Bezirci & Yılmaz (2010) Table 5", "E7 3.03 · OKS 7",
                      4.61, lambda: _bezirci_e9(7, 3.03), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Table 5", "E7 8.3 · OKS 10",
                      9.11, lambda: _bezirci_e9(10, 8.3), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Table 5", "E7 18.82 · OKS 14",
                      16.23, lambda: _bezirci_e9(14, 18.82), tur=FORMUL),
        # denk. (7) — hece katsayıları. Ortalama satırı bilinen sapma.
        Karsilastirma("Bezirci & Yılmaz (2010) Table 3", "H values of the easiest text",
                      3.03, lambda: _bezirci_e7(1.36, 0.52, 0.24, 0.01), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Table 3", "H values of the hardest text",
                      18.82, lambda: _bezirci_e7(4.75, 3.21, 1.36, 0.20), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Table 3", "mean H values",
                      8.30, lambda: _bezirci_e7(2.57, 1.52, 0.59, 0.07), tur=FORMUL,
                      gerekce="The paper prints the H6 mean as 0.07, but the value that yields "
                              "8.30 is ~0.0684. The coefficient 26.25 inflates that rounding "
                              "to 0.041; the coefficients themselves are correct."),
    ],
    "arc_len_mean": [
        Karsilastirma("Jing & Liu (2015) p.164", "Figure 3 · 'Mr. Nixon was to…'",
                      7 / 6, lambda: _jing_liu("arc_len_mean"), tur=FORMUL),
        Karsilastirma("Liu (2008) eq. (1)", "'I actually live in Beijing' · 5/4",
                      1.25, _liu_mdd, tur=FORMUL),
    ],
    "parse_depth_mean": [
        Karsilastirma("Jing & Liu (2015) p.164", "Figure 3 · MHD = 12/6",
                      2.0, lambda: _jing_liu("parse_depth_mean"), tur=FORMUL),
    ],
    "mtld": [
        Karsilastirma("McCarthy & Jarvis (2010) p.385",
                      "partial factor · TTR .887 → 40.4%", 0.404,
                      _mtld_kismi_faktor, tur=FORMUL),
    ],
    "ari": [
        # Tablo 1'in kendi bastığı ortalama (X = 12,3). Pasaj bazında
        # ayrıntı raporun sonundaki ek tabloda.
        Karsilastirma("Kincaid et al. (1975) p.8, Table 1",
                      "Appendix A · 18 passages, mean", _KINCAID_ORT_ARI,
                      lambda: _kincaid_ort("ari"), _KINCAID_GEREKCE_ARI),
    ],
    "flesch_kincaid_grade": [
        Karsilastirma("Kincaid et al. (1975) p.12, Table 2",
                      "Appendix A · 18 passages, mean", _KINCAID_ORT_FKGL,
                      lambda: _kincaid_ort("fkgl"), _KINCAID_GEREKCE_FKGL),
    ],
    "activity_ratio": [
        Karsilastirma("QUITA §6.2.2", "Text 1 · 26 verbs / 14 adjectives",
                      0.65, lambda: _quita_activity(26, 14), tur=FORMUL),
        Karsilastirma("QUITA §6.2.2", "Text 2 · 35 verbs / 8 adjectives",
                      0.814, lambda: _quita_activity(35, 8), tur=FORMUL),
    ],
    "coleman_liau": [
        # Makalenin iki denklemi vs bizim birleşik formülümüz, aynı metin.
        Karsilastirma("Coleman & Liau (1975) p.284",
                      "composition of the two equations · 13 words, 2 sentences",
                      _cl_iki_denklem(), _cl_bizim, tur=FORMUL),
        # Tablo 1'in kendi bastığı çift: sınıf 12 ↔ cloze %40,4.
        Karsilastirma("Coleman & Liau (1975) p.284, Table 1",
                      "cloze 40.4% → grade 12", 12.0,
                      lambda: _cl_sinif(40.4), tur=FORMUL),
    ],
}


# ── QUITA kılavuzunun işlenmiş örnekleri ──────────────────────────────
#
# Kılavuz on göstergeyi iki örnek metin üzerinde baştan sona hesaplayıp
# sonucu basıyor. Metinlerin sıklık dağılımı da §15.3'te yayımlı, yani
# karşılaştırma kaynağın kendi verisiyle yapılıyor.
#
# anahtar → (bölüm, Text 1 değeri, Text 2 değeri, örnek açıklaması)
_QUITA_ORNEKLER: dict[str, tuple[str, float, float, str, str]] = {
    # Text 2'de kaynak 0,590 basmış ama kendi verdiği sayılar 121/202 = 0,599
    # veriyor: yayımlanmış değerde basım hatası var, bizimki aritmetik olarak
    # doğru olan. Sapma (+0,009) tolerans içinde kaldığı için satır ✅; neden
    # olduğu açıklama sütununda duruyor (2026-09-24, Efe).
    "ttr": ("§6.1.1", 0.665, 0.59,
            "Text 1 · V/N = 119/179",
            "Text 2 · V/N = 121/202 = 0.599; source printed 0.590 (typo)"),
    "lambda_pa": ("§6.1.7", 1.628, 1.5325,
                  "Text 1 · L·log₁₀N/N, L=129.3559482",
                  "Text 2 · L·log₁₀N/N, L=134.2787065"),
    # Kılavuz kosinüsü basıyor (−0,374487816 / −0,269972586) ve "convert the
    # results of cos a to radians" diyor; beklenen o dönüşümün sonucu.
    "writers_view_alpha": ("§6.2.3", math.acos(-0.374487816),
                           math.acos(-0.269972586),
                           "Text 1 · arccos(−0.374487816)",
                           "Text 2 · arccos(−0.269972586)"),
    "h_point": ("§6.1.2", 5.0, 4.75,
                "Text 1 · rank 5 = frequency 5",
                "Text 2 · interpolation, eq. (6.2)"),
    "vocab_richness_r1": ("§6.1.3", 0.8352, 0.838,
                          "Text 1 · N=179, h=5",
                          "Text 2 · N=202, h=4.75 → ⌊h⌋=4"),
    "repeat_rate": ("§6.1.4", 0.0197, 0.02147,
                    "Text 1 · N=179", "Text 2 · N=202"),
    "rr_mcintosh": ("§6.1.5", 0.946, 0.939,
                    "Text 1 · V=119", "Text 2 · V=121"),
    "hapax_percentage": ("§6.1.6", 0.547, 0.455,
                         "Text 1 · 98/179", "Text 2 · 92/202"),
    "gini_coef": ("§6.1.8", 0.3045, 0.3511,
                  "Text 1 · m₁=41.88268156", "Text 2 · m₁=39.75742574"),
    "vocab_richness_r4": ("§6.1.9", 0.6955, 0.6489,
                          "Text 1 · 1−G", "Text 2 · 1−G"),
    "curve_length": ("§6.1.10", 129.3559, 134.2787,
                     "Text 1 · eq. (6.21)", "Text 2 · eq. (6.21)"),
    "curve_length_r": ("§6.1.11", 0.8895, 0.8657,
                       "Text 1 · Lh=14.29145", "Text 2 · Lh=18.03607"),
    "entropy": ("§6.1.12", 6.438043, 6.395099,
                "Text 1 · eq. (6.26)", "Text 2 · eq. (6.26)"),
    "adjusted_modulus": ("§6.1.13", 10.6594, 11.19973,
                         "Text 1 · M=24.01416249", "Text 2 · M=25.81931678"),
}

for _anahtar, (_bolum, _b1, _b2, _o1, _o2) in _QUITA_ORNEKLER.items():
    KARSILASTIRMALAR.setdefault(_anahtar, []).extend([
        Karsilastirma(f"QUITA {_bolum}", _o1, _b1,
                      (lambda a=_anahtar: _quita(a, _T1)), tur=FORMUL),
        Karsilastirma(
            f"QUITA {_bolum}", _o2, _b2,
            (lambda a=_anahtar: _quita(a, _T2)), tur=FORMUL),
    ])


# ── dizge karşılaştırmaları ───────────────────────────────────────────
#
# Sayı değil bölütleme sınanıyor. Heceleme 8 ``syllable_*`` anahtarını ve üç
# Türkçe okunabilirlik formülünü birden besliyor, yani buradaki bir hata
# yukarı doğru yayılır. Sayı karşılaştırması bunu yakalamaz: yanlış yerden
# bölünmüş bir kelime doğru sayıda hece verebilir.
#
# Kaynak: TDK, "Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi"
# (tdk.gov.tr, 2019) — örnekler kuralın kendi yayımlanmış örnekleri.
TDK_HECELEME: dict[str, str] = {
    "aldı": "al-dı",
    "altlık": "alt-lık",
    "türkçe": "türk-çe",
    "program": "prog-ram",          # Batı kökenli: kural sezgiye aykırı
    "kontrol": "kont-rol",
    "santral": "sant-ral",
    "saat": "sa-at",                # yan yana iki ünlü ayrı hece
    "karaosmanoğlu": "ka-ra-os-ma-noğ-lu",
    "tren": "tren",                 # kelime başı ünsüz kümesi bölünmez
    "strateji": "stra-te-ji",
}


def heceleme_satirlari() -> list[dict[str, object]]:
    """TDK'nın yayımlanmış hecelemeleriyle karşılaştırma."""
    from turkish_linguistic_features.features.phonetic import _syllabify_tr
    return [{"kelime": k, "beklenen": bek, "bizim": "-".join(_syllabify_tr(k)),
             "durum": BIREBIR if "-".join(_syllabify_tr(k)) == bek else UYUSMAZLIK}
            for k, bek in TDK_HECELEME.items()]


def rapor_satirlari(lang: str = "tr") -> list[dict[str, object]]:
    """Taban şemadaki her anahtar için bir satır.

    Kapsam ``analyze()`` çıktısından okunur; registry'ye yeni bir anahtar
    girdiğinde rapor kendiliğinden büyür.
    """
    satirlar: list[dict[str, object]] = []
    for anahtar in tlf.analyze(ORNEK_METIN[lang], lang=lang):
        kunye = tlf.describe_feature(anahtar)["citation"]
        for kars in KARSILASTIRMALAR.get(anahtar, []):
            bizim = kars.hesapla()
            fark = bizim - kars.beklenen
            # ❌ "açıklanmamış fark" demek — legend'ın kendi tanımı bu.
            # Tolerans dışı bir fark, NEDENİ YAZILIYSA 🟡'dir. Gerekçesiz
            # kalan her tolerans aşımı ❌ olur ve yayın kapısını kapatır.
            # (2026-09-24, Efe onayı: Kincaid Ek A karşılaştırması.)
            if abs(fark) <= TOLERANS:
                durum = SAPMA if (abs(fark) > 1e-3 and kars.gerekce) else BIREBIR
            elif kars.gerekce:
                durum = SAPMA
            else:
                durum = UYUSMAZLIK
            satirlar.append({"anahtar": anahtar, "kaynak": kars.kaynak,
                             "ornek": kars.ornek, "beklenen": kars.beklenen,
                             "bizim": bizim, "fark": fark, "durum": durum,
                             "gerekce": kars.gerekce, "tur": kars.tur})
        if anahtar not in KARSILASTIRMALAR:
            if not kunye:
                durum = KAYNAK_YOK
            elif anahtar in TUREV_ANAHTARLARI:
                durum = TUREV
            elif kunye.startswith(SEMA_ONEKLERI):
                durum = SEMA
            else:
                durum = ACIK
            satirlar.append({
                "anahtar": anahtar, "kaynak": kunye or "—", "ornek": "—",
                "beklenen": None, "bizim": None, "fark": None,
                "durum": durum, "gerekce": "", "tur": "—",
            })
    return satirlar


_BASLIK = """<!-- ÜRETİLMİŞ DOSYA — elle düzenlemeyin.
     Kaynak: scripts/dogrulama_raporu.py
     Yeniden üretmek için:
       python scripts/dogrulama_raporu.py -->

# Doğrulama raporu

Bu rapor her özniteliğin ürettiği sayıyı, dayandığı kaynağın **yayımladığı
sayıyla** karşılaştırır. Amaç basit: bir sayıyı çalışmanızda kullanmadan önce
onun literatürdeki değeri tuttuğunu görebilmeniz.

## Durumlar ne anlama geliyor

| | Anlamı |
|---|---|
| ✅ **birebir** | Kaynağın yayımladığı sayıyla tolerans içinde aynı. |
| 🟡 **belgelenmiş sapma** | Fark var ve **nedeni yazılı**. Kaynağın ara değerleri yuvarlaması, ya da kaynağın sayılarının elle üretilmiş olması gibi. Sapmanın sonuca etkisi satırda anlatılır. |
| 🔍 **açık** | Kaynak formülü veriyor ama uygulanmış bir örnek vermiyor. Doğrulanabilir, henüz doğrulanmadı; formül ve sınır durumları kendi test dosyalarında sınanıyor. |
| ❌ **uyuşmazlık** | **Açıklanmamış** fark. **Yayın kapısı:** bir tane bile varsa sürüm çıkmaz. |

Aşağıdaki iki durum **doğrulama adayı değildir** — aranacak bir sayı yoktur:

| | Anlamı |
|---|---|
| ⚪ **kaynak yok** | Adlandırılmış bir literatür ölçüsü değil; saf tanım (`punc_,_ratio`, `char_a`). |
| ⚫ **etiket şeması** | Bir ölçü değil, dış bir şemanın kategorisini sayıyor (`pos_noun` → UD; `case_loc_ratio` → Zeyrek). Şema kategori tanımlar, ölçüm yayımlamaz. |
| 🔧 **türev** | Formül bir kaynaktan, **uygulaması bu kütüphaneden**. `entropy_std` Shannon'ın entropisidir ama parçalar arası standart sapması bizim; `long_sent_ratio`'nun eşiği kendi kalibrasyonumuzdan gelir. Kimse bu ölçüyü yayımlamadı, dolayısıyla karşılaştırılacak sayı da yok. Kendi kalibrasyonumuza karşı sınamak kendi cevabımıza bakmak olurdu. |

Tolerans {tolerans}. Kaynaklar ara değerleri yuvarlayarak bastığı için mutlak
eşitlik beklenmiyor.

**Toleransı aşan fark otomatik olarak ❌ değildir.** Belirleyici olan farkın
büyüklüğü değil, **nedeninin bilinip bilinmediğidir**: nedeni ölçülmüş ve
yazılmışsa satır 🟡, yazılmamışsa ❌ olur. Gerekçe bir mazeret değil, farkın
nereden geldiğinin kanıtıdır — ilgili satırın altında okuyabilirsiniz.

## Kanıtın iki türü

**Uçtan uca** satırlar kaynağın **metnini** boru hattından geçirir — yani
tokenizasyon, heceleme ve cümle bölme de sınanır. Bunlar en güçlü kanıt.

**Formül** satırları fonksiyona girdileri doğrudan verir (örneğin "hece/sözcük
2,2 ve sözcük/cümle 4"). Formülü ve katsayıları doğrular, boru hattını
doğrulamaz. Kaynak bir metin yayımlamamışsa elde olan budur.

Bu rapor **testlerden üretilir** — `tests/test_kaynak_esligi.py` ile aynı
karşılaştırma tablosunu okur, yani ikisi ayrışamaz. Diğer bilinen-değer
testleri (T04B, T05–T07, T10, T13) kendi dosyalarında duruyor.

"""

_BASLIK_EN = """<!-- GENERATED FILE — do not edit by hand.
     Source: scripts/dogrulama_raporu.py
     To regenerate:
       python scripts/dogrulama_raporu.py -->

# Verification report

This report compares the number each feature produces against the number
**published by the source it rests on**. The purpose is plain: before you use
a number in your own work, you should be able to see that it matches the
value in the literature.

## What the statuses mean

| | Meaning |
|---|---|
| ✅ **exact** | Within tolerance of the number the source published. |
| 🟡 **documented deviation** | There is a difference and **the reason is written down** — the source rounded an intermediate value, or the source's own numbers were produced by hand, and so on. The effect of the deviation is explained in the row. |
| 🔍 **open** | The source gives the formula but no applied example. Verifiable, not yet verified; the formula and its edge cases are tested in their own test files. |
| ❌ **mismatch** | An **unexplained** difference. **Release gate:** a single one blocks a release. |

The two statuses below are **not verification candidates** — there is no
number to look for:

| | Meaning |
|---|---|
| ⚪ **no source** | Not a named measure from the literature; a plain definition (`punc_,_ratio`, `char_a`). |
| ⚫ **tag scheme** | Not a measure but a count of an external scheme's categories (`pos_noun` → UD; `case_loc_ratio` → Zeyrek). A scheme defines categories; it does not publish measurements. |
| 🔧 **derivative** | The formula comes from a source, **the application is this library's**. `entropy_std` is Shannon's entropy, but taking its standard deviation across segments is ours; `long_sent_ratio`'s threshold comes from our own calibration. Nobody has published this measure, so there is no number to compare against. Testing it against our own calibration would be reading our own answer sheet. |

Tolerance {tolerans}. Sources print rounded intermediate values, so exact
equality is not expected.

**Exceeding the tolerance does not automatically make a row ❌.** What decides
is not the size of the difference but **whether its cause is known**: if the
cause has been measured and written down the row is 🟡, and if it has not the
row is ❌. A reason is not an excuse — it is evidence of where the difference
came from, and you can read it under the row.

## Two kinds of evidence

**End-to-end** rows push the source's **own text** through the pipeline, so
tokenisation, syllabification and sentence splitting are tested too. This is
the strongest evidence.

**Formula** rows feed the inputs to the function directly (for example
"syllables per word 2.2 and words per sentence 4"). They verify the formula
and its coefficients, not the pipeline. This is what is available when the
source published no text.

This report is **generated from the tests** — it reads the same comparison
table as `tests/test_kaynak_esligi.py`, so the two cannot drift apart. The
other known-value tests (T04B, T05–T07, T10, T13) live in their own files.

"""

_BASLIK_DIL = {"tr": _BASLIK, "en": _BASLIK_EN}

# Durum adlarının okunur karşılıkları — özet tablosunda kullanılır.
_DURUM_ADI = {
    "tr": {BIREBIR: "birebir", SAPMA: "belgelenmiş sapma",
           ACIK: "açık — kaynakta sayısal örnek yok",
           KAYNAK_YOK: "kaynak yok — saf tanım",
           SEMA: "etiket şeması — ölçü değil",
           TUREV: "türev — uygulaması bu kütüphaneye ait",
           UYUSMAZLIK: "uyuşmazlık"},
    "en": {BIREBIR: "exact", SAPMA: "documented deviation",
           ACIK: "open — no worked example in source",
           KAYNAK_YOK: "no source — plain definition",
           SEMA: "tag scheme — not a measure",
           TUREV: "derivative — the application is this library's",
           UYUSMAZLIK: "mismatch"},
}

# Kanıt türü de bizim kendi sözcüğümüz (künye değil), dile göre çevrilir.
_KANIT_ADI = {
    "tr": {UCTAN_UCA: "uçtan uca", FORMUL: "formül"},
    "en": {UCTAN_UCA: UCTAN_UCA, FORMUL: FORMUL},
}

# Bölüm başlıkları ve düz yazı. ``{}`` alanları ``uret()`` dolduruyor.
_METIN = {
    "tr": {
        "dil_adi": {"tr": "Türkçe", "en": "İngilizce"},
        "bolum": "\n## {etiket} — {anahtar} anahtar, {satir} satır\n\n"
                 "Bir anahtarın birden çok kaynak örneği olabilir; her biri "
                 "ayrı satır.\n\n",
        "ozet_basligi": ("Durum", "Satır sayısı"),
        "ozet_aday": "**Doğrulama adayı — {n} satır**\n\n",
        "ozet_disi": "\n\n**Doğrulama adayı olmayan — {n} satır.** "
                     "Bunlarda aranacak bir sayı yoktur; yokluğu bir eksiklik "
                     "değil, tanımın kendisidir.\n\n",
        "olculen_basligi": "\n\n### Sayısal karşılaştırması olanlar\n\n",
        "olculen_sutun": "| Anahtar | Kaynak | Örnek | Kanıt | Beklenen "
                         "| Bizim | Fark | Durum |\n",
        "sapma": "\n**`{anahtar}` sapması:** {gerekce}\n",
        "kalan_basligi": "\n### 🔍 Açık — doğrulanabilir, henüz doğrulanmadı\n\n",
        "kalan_ozet": "{n} anahtar. Kaynak formülü yayımlamış ama o formülün "
                      "uygulandığı bir sayısal örnek vermemiş. Nicel dilbilimde "
                      "bu olağandır: Yule (1944) K'yı tanımlar, bir romanda "
                      "K'nın kaç çıktığını basmaz. Bu satırlar **test "
                      "edilmiyor demek değildir** — formül ve sınır durumları "
                      "kendi test dosyalarında sınanıyor; burada takip edilen "
                      "yalnız *kaynağın sayısıyla* karşılaştırma.\n\n",
        "kalan_sutun": "| Anahtar | Kaynak | Durum |\n|---|---|---|\n",
        "disi_basligi": "\n### Doğrulama adayı olmayanlar\n\n",
        "disi_ozet": "{n} anahtar. ⚪ olanlar saf tanım (`punc_,_ratio`, "
                     "`char_a`) — adlandırılmış bir literatür ölçüsü değil. "
                     "⚫ olanlar bir ölçü değil, dış bir etiket şemasının "
                     "kategorisini sayıyor; şema kategori tanımlar, ölçüm "
                     "yayımlamaz. 🔧 olanların formülü bir kaynaktan gelir ama "
                     "uygulaması bu kütüphaneye aittir. Üçünde de aranacak bir "
                     "sayı yok.\n\n",
        "hece": "\n## Heceleme — {tam}/{top}\n\n"
                "Heceleme sekiz `syllable_*` anahtarını ve üç Türkçe "
                "okunabilirlik formülünü birden besliyor. Aşağıdaki "
                "karşılaştırma **sayıyı değil bölütlemeyi** sınıyor: yanlış "
                "yerden bölünmüş bir kelime doğru sayıda hece verebilir, sayı "
                "karşılaştırması onu yakalamaz.\n\n"
                "Kaynak: TDK, \"Hece Yapısı ve Satır Sonunda Kelimelerin "
                "Bölünmesi\" (tdk.gov.tr, 2019).\n\n"
                "| Kelime | TDK | Bizim | Durum |\n|---|---|---|---|\n",
        "kincaid": "\n## Ek — Kincaid Ek A, pasaj bazında\n\n"
                   "Ana tablodaki iki 🟡 satırın (`ari`, `flesch_kincaid_grade`) "
                   "dayandığı 18 karşılaştırma. Ara değerler (vuruş, kelime) "
                   "burada duruyor ki fark çıktığında hangi girdiden geldiği "
                   "görülebilsin.\n\n"
                   "**FRE bandı** sütunu ayrı bir kontrol: Tablo 1'in Flesch "
                   "sütunu 0-100 puanı değil, Flesch'in kendi sınıf bandını "
                   "basıyor (`8-9` = FRE 60-70 gibi). Bizim FRE'miz bandın "
                   "içine düşüyor mu, ona bakıyor.\n\n"
                   "Pasaj metinleri `tests/veri/kincaid/`, ölçüm "
                   "`scripts/kincaid_olcum.py`.\n\n"
                   "| # | Vuruş | Kelime | ARI kaynak | ARI bizim | Fark "
                   "| FKGL kaynak | FKGL bizim | Fark | FRE bandı |\n"
                   "|---|---|---|---|---|---|---|---|---|---|\n",
        "kincaid_ozet": "\nARI ortalama mutlak fark **{ari_ort:.2f}**, en büyük "
                        "**{ari_max:.2f}** (pasaj {ari_n}). FKGL ortalama mutlak "
                        "fark **{fkgl_ort:.2f}**, en büyük **{fkgl_max:.2f}** "
                        "(pasaj {fkgl_n}). FRE bandının içinde: "
                        "**{bant_ici}/{bant_top}**.\n",
    },
    "en": {
        "dil_adi": {"tr": "Turkish", "en": "English"},
        "bolum": "\n## {etiket} — {anahtar} keys, {satir} rows\n\n"
                 "A key may have more than one worked example in its source; "
                 "each one is its own row.\n\n",
        "ozet_basligi": ("Status", "Rows"),
        "ozet_aday": "**Verification candidates — {n} rows**\n\n",
        "ozet_disi": "\n\n**Not verification candidates — {n} rows.** There is "
                     "no number to look for in these; its absence is not a gap "
                     "but the definition itself.\n\n",
        "olculen_basligi": "\n\n### Keys with a numeric comparison\n\n",
        "olculen_sutun": "| Key | Source | Example | Evidence | Expected "
                         "| Ours | Diff | Status |\n",
        "sapma": "\n**`{anahtar}` deviation:** {gerekce}\n",
        "kalan_basligi": "\n### 🔍 Open — verifiable, not yet verified\n\n",
        "kalan_ozet": "{n} keys. The source published the formula but never "
                      "applied it to anything and printed the result. In "
                      "quantitative linguistics this is ordinary: Yule (1944) "
                      "defines K; he does not print what K comes to for a "
                      "particular novel. These rows are **not untested** — "
                      "their formulas and edge cases are tested in their own "
                      "test files. What is tracked here is only the comparison "
                      "*against the source's number*.\n\n",
        "kalan_sutun": "| Key | Source | Status |\n|---|---|---|\n",
        "disi_basligi": "\n### Not verification candidates\n\n",
        "disi_ozet": "{n} keys. The ⚪ ones are plain definitions "
                     "(`punc_,_ratio`, `char_a`) — not named measures from the "
                     "literature. The ⚫ ones are not measures at all but "
                     "counts of an external tag scheme's categories; a scheme "
                     "defines categories, it does not publish measurements. "
                     "The 🔧 ones take their formula from a source but their "
                     "application is this library's. None of the three has a "
                     "number to look for.\n\n",
        "hece": "\n## Syllabification — {tam}/{top}\n\n"
                "Syllabification feeds eight `syllable_*` keys and all three "
                "Turkish readability formulas at once. The comparison below "
                "tests **the split, not the count**: a word broken in the "
                "wrong place can still yield the right number of syllables, "
                "and a count comparison would not catch it.\n\n"
                "Source: TDK, \"Hece Yapısı ve Satır Sonunda Kelimelerin "
                "Bölünmesi\" (tdk.gov.tr, 2019).\n\n"
                "| Word | TDK | Ours | Status |\n|---|---|---|---|\n",
        "kincaid": "\n## Appendix — Kincaid Appendix A, passage by passage\n\n"
                   "The 18 comparisons behind the two 🟡 rows in the main "
                   "table (`ari`, `flesch_kincaid_grade`). The intermediate "
                   "counts (strokes, words) are here so that when a number "
                   "differs you can see which input it came from.\n\n"
                   "The **FRE band** column is a separate check: Table 1's "
                   "Flesch column prints not a 0-100 score but Flesch's own "
                   "grade band (`8-9` = FRE 60-70, and so on). It asks whether "
                   "our FRE falls inside that band.\n\n"
                   "Passage texts: `tests/veri/kincaid/`. Measurement: "
                   "`scripts/kincaid_olcum.py`.\n\n"
                   "| # | Strokes | Words | ARI source | ARI ours | Diff "
                   "| FKGL source | FKGL ours | Diff | FRE band |\n"
                   "|---|---|---|---|---|---|---|---|---|---|\n",
        "kincaid_ozet": "\nARI mean absolute difference **{ari_ort:.2f}**, "
                        "largest **{ari_max:.2f}** (passage {ari_n}). FKGL mean "
                        "absolute difference **{fkgl_ort:.2f}**, largest "
                        "**{fkgl_max:.2f}** (passage {fkgl_n}). Inside the FRE "
                        "band: **{bant_ici}/{bant_top}**.\n",
    },
}


def kincaid_satirlari() -> list[dict[str, object]]:
    """Ek tablo için pasaj bazında satırlar."""
    d = _kincaid_oznitelikler()
    satirlar = []
    for n in range(1, 19):
        bant = _KINCAID_T1_BANT[n]
        if bant is None:
            durum = "—"
        else:
            lo, hi = _FRE_BANDI[bant]
            ici = lo <= d[n]["fre"] <= hi
            durum = f"{bant} {'✅' if ici else '❌'}"
        satirlar.append({
            "no": n, "vurus": int(d[n]["vurus"]), "kelime": int(d[n]["kelime"]),
            "ari_k": _KINCAID_T1_ARI[n], "ari_b": d[n]["ari"],
            "fkgl_k": _KINCAID_T2_FKGL[n], "fkgl_b": d[n]["fkgl"],
            "bant": durum,
        })
    return satirlar


def _ozet(satirlar: list[dict[str, object]], dil: str = "tr") -> str:
    """İki ayrı tablo: doğrulama adayı olanlar ve olmayanlar.

    Tek tabloda toplamak yanıltıyordu — 69 etiket-şeması ve 67 saf tanım
    satırı, doğrulanabilir 83 satırın yanında "başarısız" gibi okunuyordu.
    """
    from collections import Counter
    sayim = Counter(s["durum"] for s in satirlar)
    m = _METIN[dil]
    a, b = m["ozet_basligi"]
    ad = _DURUM_ADI[dil]

    def tablo(durumlar) -> tuple[str, int]:
        satir = [f"| {a} | {b} |", "|---|---|"]
        top = 0
        for d in durumlar:
            if sayim[d]:
                satir.append(f"| {_SIMGE[d]} {ad[d]} | {sayim[d]} |")
                top += sayim[d]
        return "\n".join(satir), top

    aday, n_aday = tablo(ADAY_DURUMLAR)
    disi, n_disi = tablo(ADAY_OLMAYAN)
    return (m["ozet_aday"].format(n=n_aday) + aday + "\n"
            + m["ozet_disi"].format(n=n_disi) + disi)


def uret(dil: str = "tr") -> str:
    """Raporu ``dil`` ("tr" | "en") ile üretir.

    İki dil aynı ölçümleri gösterir; yalnız düz yazı değişir. Künyeler ve
    kaynak adları registry'den geldiği için zaten İngilizce.
    """
    m = _METIN[dil]
    parcalar = [_BASLIK_DIL[dil].replace("{tolerans}", str(TOLERANS))]
    for lang in ("tr", "en"):
        satirlar = rapor_satirlari(lang)
        n_anahtar = len({s["anahtar"] for s in satirlar})
        parcalar.append(m["bolum"].format(etiket=m["dil_adi"][lang],
                                          anahtar=n_anahtar,
                                          satir=len(satirlar)))
        parcalar.append(_ozet(satirlar, dil))
        parcalar.append(m["olculen_basligi"])
        parcalar.append(m["olculen_sutun"])
        parcalar.append("|---|---|---|---|---|---|---|---|\n")
        olculen = [s for s in satirlar if s["beklenen"] is not None]
        kanit = _KANIT_ADI[dil]
        for s in olculen:
            parcalar.append(
                f"| `{s['anahtar']}` | {s['kaynak']} | {s['ornek']} "
                f"| {kanit.get(s['tur'], s['tur'])} "
                f"| {s['beklenen']:.3f} | {s['bizim']:.3f} | {s['fark']:+.3f} "
                f"| {_SIMGE[s['durum']]} |\n")
        if not olculen:
            parcalar.append("| — | — | — | — | — | — | — | — |\n")
        for s in olculen:
            if s["gerekce"]:
                parcalar.append(m["sapma"].format(anahtar=s["anahtar"],
                                                  gerekce=s["gerekce"]))
        # 🔍 açık ve "aday olmayan" ayrı bölümler — tek listede toplamak
        # aranacak sayısı olanla olmayanı karıştırıyordu.
        acik = [s for s in satirlar if s["durum"] == ACIK]
        disi = [s for s in satirlar if s["durum"] in ADAY_OLMAYAN]
        for baslik, ozet, kume in ((m["kalan_basligi"], m["kalan_ozet"], acik),
                                   (m["disi_basligi"], m["disi_ozet"], disi)):
            parcalar.append(baslik)
            parcalar.append(ozet.format(n=len(kume)))
            parcalar.append(m["kalan_sutun"])
            for s in kume:
                parcalar.append(f"| `{s['anahtar']}` | {s['kaynak']} "
                                f"| {_SIMGE[s['durum']]} |\n")

    # Heceleme ayrı: sayı değil bölütleme sınanıyor.
    hece = heceleme_satirlari()
    tam = sum(1 for s in hece if s["durum"] == BIREBIR)
    parcalar.append(m["hece"].format(tam=tam, top=len(hece)))
    for s in hece:
        parcalar.append(f"| {s['kelime']} | `{s['beklenen']}` | `{s['bizim']}` "
                        f"| {_SIMGE[s['durum']]} |\n")

    # Kincaid Ek A — iki 🟡 satırın dayandığı 18 karşılaştırma.
    parcalar.append(m["kincaid"])
    ks = kincaid_satirlari()
    for s in ks:
        parcalar.append(
            f"| {s['no']} | {s['vurus']} | {s['kelime']} | {s['ari_k']:.1f} "
            f"| {s['ari_b']:.2f} | {s['ari_b'] - s['ari_k']:+.2f} "
            f"| {s['fkgl_k']:.1f} | {s['fkgl_b']:.2f} "
            f"| {s['fkgl_b'] - s['fkgl_k']:+.2f} | {s['bant']} |\n")
    a_n, a_f = _kincaid_en_buyuk_fark("ari", _KINCAID_T1_ARI)
    f_n, f_f = _kincaid_en_buyuk_fark("fkgl", _KINCAID_T2_FKGL)
    bant_top = sum(1 for s in ks if s["bant"] != "—")
    parcalar.append(m["kincaid_ozet"].format(
        ari_ort=sum(abs(s["ari_b"] - s["ari_k"]) for s in ks) / len(ks),
        ari_max=abs(a_f), ari_n=a_n,
        fkgl_ort=sum(abs(s["fkgl_b"] - s["fkgl_k"]) for s in ks) / len(ks),
        fkgl_max=abs(f_f), fkgl_n=f_n,
        bant_ici=sum(1 for s in ks if str(s["bant"]).endswith("✅")),
        bant_top=bant_top))
    return "".join(parcalar)


DOSYA_ADI = {"tr": "dogrulama-raporu.md", "en": "verification-report.md"}

if __name__ == "__main__":
    belgeler = Path(__file__).resolve().parents[1] / "docs"
    belgeler.mkdir(exist_ok=True)
    for _dil, _ad in DOSYA_ADI.items():
        _hedef = belgeler / _ad
        _hedef.write_text(uret(_dil), encoding="utf-8")
        print(f"Yazildi: {_hedef}")
