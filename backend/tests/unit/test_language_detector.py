from app.multilingual.language_detector import detect_language


def test_detect_english():
    result = detect_language(
        "Machine learning is a method of artificial intelligence."
    )

    assert result == "en"


def test_detect_bengali():
    result = detect_language(
        "মেশিন লার্নিং কৃত্রিম বুদ্ধিমত্তার একটি পদ্ধতি।"
    )

    assert result == "bn"


def test_detect_hindi():
    result = detect_language(
        "मशीन लर्निंग कृत्रिम बुद्धिमत्ता की एक विधि है।"
    )

    assert result == "hi"