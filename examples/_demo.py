"""Örneklerin ortak demo korpusu.

Depoda korpus yok. Bir örnek korpus ya da dosya argümanı almadan
çalıştırılırsa bu küçük metinler kullanılır. İçerik bu depo için yazıldı;
telif sorunu yok.

İki etiket, ikişer metin, her biri ~100 sözcük. Gerçek bir korpusun yerini
tutmaz — örneklerin **nasıl çalıştığını** göstermek için var, sayıları
yorumlamak için değil.
"""

from pathlib import Path

DEMO_METINLER = {
    "Anlatı_sabah": (
        "Sabah erken kalktı. Pencereyi açtığında sokak henüz boştu ve uzaktan "
        "bir kamyonun sesi geliyordu. Çayını tazeledi, defterini masaya koydu "
        "ve dün gece yarım bıraktığı cümleyi yeniden okudu. Cümle ona artık "
        "yabancı geliyordu; sanki başka biri yazmıştı. Kalemi eline aldı, "
        "birkaç kelimeyi çizdi, yerine daha kısa olanları yazdı. Dışarıda "
        "yağmur başlamıştı. Camın kenarında biriken damlaları izledi ve "
        "yazmaya devam etti. Öğleye doğru defteri kapattı, paltosunu giydi ve "
        "kapıyı arkasından yavaşça çekti. Merdivenlerde komşusuyla karşılaştı, "
        "selamlaştılar, hava üzerine iki cümle kurdular. Sokağa çıktığında "
        "yağmur dinmiş, kaldırımlar ıslak kalmıştı."
    ),
    "Anlatı_akşam": (
        "Akşam olduğunda ışıkları yakmadı. Karanlık odada oturdu ve caddeden "
        "gelen sesleri dinledi. Bir araba korna çaldı, ardından biri güldü. "
        "Masanın üstünde duran defteri eline aldı ama açmadı. Ne yazacağını "
        "biliyordu, yalnız başlamak istemiyordu. Mutfağa gitti, bir bardak su "
        "içti ve geri döndü. Saat geç olmuştu. Sonunda lambayı yaktı, defteri "
        "açtı ve sabah bıraktığı yerden devam etti. Yazdıkça cümleler "
        "kısalıyordu. Gece yarısına doğru son noktayı koydu, defteri kapattı "
        "ve uyumaya gitti. Ertesi sabah aynı cümleyi bir kez daha okuyacaktı."
    ),
    "Bilgi_tokenizasyon": (
        "Tokenizasyon, bir metni işlenebilir birimlere ayırma işlemidir. "
        "Birimler çoğunlukla kelimelerdir, ancak noktalama işaretleri ve "
        "sayılar da ayrı birim sayılır. Ayırma kuralları dile göre değişir: "
        "Türkçede kesme işareti ekleri ayırırken, İngilizcede kısaltmaların "
        "içinde geçebilir. Bu nedenle dilden bağımsız bir kural kümesi "
        "yeterli olmaz. Ayrıca aynı metnin iki farklı yöntemle sayılması "
        "farklı birim sayıları verir; uzunluğa duyarlı ölçütler bu farktan "
        "doğrudan etkilenir. Ölçümlerin karşılaştırılabilir olması için "
        "tokenizasyon yönteminin baştan sabitlenmesi ve raporlanması gerekir."
    ),
    "Bilgi_parcalama": (
        "Parçalama, uzun bir metni eşit büyüklükte bölümlere ayırma işlemidir. "
        "Sözcüksel zenginlik ölçütlerinin çoğu metin uzunluğuna duyarlıdır, "
        "yani aynı metnin uzun ve kısa bölümleri farklı değerler üretir. "
        "Bu yüzden karşılaştırılacak bölümlerin yakın uzunlukta olması "
        "beklenir. Son bölüm çoğu zaman eksik kalır; eşiğin altındaki artığı "
        "atmak, ölçülen farkın metinden mi yoksa bölüm uzunluğundan mı "
        "geldiği sorusunu ortadan kaldırır. Bölüm boyu seçimi yöntem "
        "bölümünde belirtilmesi gereken bir karardır."
    ),
}


def demo_korpus_yaz(dizin: Path) -> None:
    """Demo korpusu ``Etiket_Başlık.txt`` düzeninde diske yazar."""
    dizin.mkdir(parents=True, exist_ok=True)
    for ad, metin in DEMO_METINLER.items():
        (dizin / f"{ad}.txt").write_text(metin, encoding="utf-8")


def demo_metni() -> str:
    """Dört demo metnini boş satırla ayrılmış tek metin olarak verir (~300 sözcük)."""
    return "\n\n".join(DEMO_METINLER.values())
