from app.services.normalization.arabic import normalize_arabic


def test_normalize_arabic_basic():
    text = "إثبــات الهُويّة ١٢٣"
    assert normalize_arabic(text) == "اثبات الهويه 123"
