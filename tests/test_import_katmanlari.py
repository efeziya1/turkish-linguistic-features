"""Katman sözleşmesi: aşağı yukarıyı görmez, features ⇄ pipeline hiç görüşmez.

Kural yazılı olmadığı sürece ihlal fark edilmiyor; bu dosya onu kodda tutuyor.
"""

import ast
from pathlib import Path

KOK = Path(__file__).parent.parent / "turkish_linguistic_features"

# L0 = paylaşılan çekirdek. Paket içinden hiçbir şey import etmez, yalnız stdlib.
L0 = {"alfabe", "vocab", "params", "exceptions", "_warnings"}


PAKET = KOK.name


def _ic_importlar(dosya: Path) -> list[tuple[int, str]]:
    """Paket içi import'lar: ``(satır, 'features.lexical')`` ikilileri.

    Hem relative (``from ..vocab``) hem mutlak (``from turkish_linguistic_features
    .vocab``, ``import turkish_linguistic_features.vocab``) yazım okunur; hedef
    paket kökünden yazılır. Stdlib ve üçüncü parti import'lar atlanır.
    Kökü hedefleyen ``from .. import vocab`` biçiminde hedef import edilen addır.
    """
    agac = ast.parse(dosya.read_text(encoding="utf-8"))
    paket = dosya.relative_to(KOK).parts[:-1]
    cikti: list[tuple[int, str]] = []

    def ekle(satir: int, parcalar: tuple[str, ...], adlar: list[str]) -> None:
        # Kökün kendisi hedefse (``from .. import x``) asıl hedef x'tir.
        for hedef in ([".".join(parcalar)] if parcalar else adlar):
            cikti.append((satir, hedef))

    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom):
            modul = tuple(dugum.module.split(".")) if dugum.module else ()
            if dugum.level:
                parcalar = (*paket[: len(paket) - (dugum.level - 1)], *modul)
            elif modul[:1] == (PAKET,):
                parcalar = modul[1:]
            else:
                continue
            ekle(dugum.lineno, parcalar, [a.name for a in dugum.names])
        elif isinstance(dugum, ast.Import):
            for ad in dugum.names:
                modul = tuple(ad.name.split("."))
                if modul[0] == PAKET:
                    ekle(dugum.lineno, modul[1:], [""])  # kökün kendisi: L3
    return cikti


def test_L0_paket_icinden_hicbir_sey_import_etmez():
    """L0 en alt katman: bir şey import ederse altında bir katman var demektir."""
    for ad in sorted(L0):
        dosya = KOK / f"{ad}.py"
        if not dosya.exists():
            continue                      # Task 2-4 tamamlanana kadar henüz yok
        ihlal = _ic_importlar(dosya)
        assert not ihlal, f"{ad}.py L0 olmalı ama paket içinden import ediyor: {ihlal}"


def test_features_ile_pipeline_birbirini_gormez():
    """L1/L2 yalnız L0'ı ve kendi paketini import edebilir.

    Hedefin ilk parçası beyaz listede değilse ihlal. Tek kontrol iki kuralı
    birden tutuyor: çapraz bağ (``features`` ⇄ ``pipeline``) ve yukarı bağ
    (L3 → ``_analyze``, ``file_loader``) — ikincisi aynı zamanda gerçek bir
    import döngüsü olurdu. Mutlak yazım da yakalanır: ``from
    turkish_linguistic_features._analyze import ...`` relative karşılığıyla
    aynı hedefi üretir; ``import turkish_linguistic_features`` (kökün kendisi,
    L3) boş hedef üretir ve düşer.
    """
    for paket in ("features", "pipeline"):
        for dosya in sorted((KOK / paket).glob("*.py")):
            for satir, hedef in _ic_importlar(dosya):
                assert hedef.split(".")[0] in L0 | {paket}, (
                    f"{paket}/{dosya.name}:{satir} → {hedef!r} — L1/L2 yalnız L0 ve kendi paketini görebilir"
                )


def test_pipeline_init_bos_kalir():
    """T22: dolu bir __init__ spaCy'yi zeyrek'ten önce yükler, Windows koruması düşer.

    ``from .pipeline.zeyrek_backend import ...`` bile önce paketi çalıştırır;
    __init__ spacy_pipeline'ı çekerse (satır 20'de ``import spacy``) yükleme
    sırası tersine döner ve bozulma sessizdir.
    """
    assert not (KOK / "pipeline" / "__init__.py").read_text(encoding="utf-8").strip()


def test_L0_dosyalari_kokte():
    """Taşıma tamamlandı mı — Task 2, 3 ve 4'ün kapı testi."""
    for ad in sorted(L0):
        assert (KOK / f"{ad}.py").exists(), f"{ad}.py kök seviyede olmalı"
