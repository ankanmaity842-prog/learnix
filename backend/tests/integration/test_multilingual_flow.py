from app.multilingual.language_detector import detect_language


def test_multilingual_learning_flow():
    queries = {
        "en": "Introduction to machine learning",
        "bn": "মেশিন লার্নিং এর পরিচিতি",
        "hi": "मशीन लर्निंग का परिचय",
    }

    for expected_language, query in queries.items():
        detected = detect_language(query)

        assert detected == expected_language


def test_english_detection():
    assert detect_language(
        "How does a neural network work?"
    ) == "en"


def test_bengali_detection():
    assert detect_language(
        "নিউরাল নেটওয়ার্ক কীভাবে কাজ করে?"
    ) == "bn"


def test_hindi_detection():
    assert detect_language(
        "न्यूरल नेटवर्क कैसे काम करता है?"
    ) == "hi"