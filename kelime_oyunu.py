import random
import re
from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr


WORDS = [
    {"turkish": "elma", "english": "apple"},
    {"turkish": "kitap", "english": "book"},
    {"turkish": "masa", "english": "table"},
    {"turkish": "köpek", "english": "dog"},
    {"turkish": "kedi", "english": "cat"},
    {"turkish": "okul", "english": "school"},
    {"turkish": "su", "english": "water"},
    {"turkish": "güneş", "english": "sun"},
    {"turkish": "arkadaş", "english": "friend"},
    {"turkish": "mutlu", "english": "happy"},
    {"turkish": "hızlı", "english": "fast"},
    {"turkish": "kitaplık", "english": "bookshelf"},
    {"turkish": "deneyim", "english": "experience"},
    {"turkish": "başarı", "english": "success"},
    {"turkish": "sorumluluk", "english": "responsibility"},
]

DIFFICULTIES = {
    "1": {"name": "Kolay", "record_seconds": 5, "points": 10},
    "2": {"name": "Orta", "record_seconds": 4, "points": 20},
    "3": {"name": "Zor", "record_seconds": 3, "points": 30},
}


def clean_text(text):
    """Remove punctuation so small pronunciation differences do not break scoring."""
    text = text.lower().strip()
    return re.sub(r"[^a-z ]", "", text)


def choose_difficulty():
    print("\nZorluk seç:")
    print("1 - Kolay: 5 saniye kayıt, doğru cevap 10 puan")
    print("2 - Orta : 4 saniye kayıt, doğru cevap 20 puan")
    print("3 - Zor  : 3 saniye kayıt, doğru cevap 30 puan")

    while True:
        choice = input("Seçimin (1/2/3): ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("Lütfen 1, 2 veya 3 yazın.")


def record_and_recognize(seconds):
    sample_rate = 44100
    audio_file = Path("oyun_kaydi.wav")

    print(f"\n🎙️ Konuşun! Kayıt {seconds} saniye sürecek...")
    recording = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    write(audio_file, sample_rate, recording)

    recognizer = sr.Recognizer()
    with sr.AudioFile(str(audio_file)) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio, language="en-US")
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        raise RuntimeError("Konuşma tanıma servisine ulaşılamadı.")


def show_result(score, correct_answers, total_questions, streak):
    print("\n" + "=" * 45)
    print("🏁 OYUN BİTTİ!")
    print(f"Puanın: {score}")
    print(f"Doğru cevap: {correct_answers}/{total_questions}")
    print(f"En uzun serin: {streak}")
    print("=" * 45)


def play_game():
    print("\n🇹🇷  KELİME SESLENDİRME OYUNU  🇬🇧")
    print("Türkçe kelimeyi görünce İngilizce karşılığını sesli söyleyin.")
    print("Oyun süresizdir. İstediğiniz zaman 'q' ile çıkabilirsiniz.")

    difficulty = choose_difficulty()
    score = 0
    correct_answers = 0
    total_questions = 0
    current_streak = 0
    best_streak = 0
    while True:
        word = random.choice(WORDS)
        total_questions += 1
        expected = word["english"]

        print(f"Türkçe kelime:  👉 {word['turkish'].upper()}")
        command = input("Hazırsanız Enter'a basın, çıkmak için q yazın: ").strip().lower()
        if command == "q":
            break

        try:
            spoken = record_and_recognize(difficulty["record_seconds"])
        except (RuntimeError, OSError) as error:
            print(f"⚠️ {error}")
            print("Bu tur atlandı. Mikrofonu veya internet bağlantısını kontrol edin.")
            continue

        if not spoken:
            current_streak = 0
            print("🤔 Konuşma anlaşılamadı. Daha yüksek sesle tekrar deneyebilirsin.")
            continue

        print(f"Senin cevabın: {spoken}")
        if clean_text(spoken) == clean_text(expected):
            correct_answers += 1
            current_streak += 1
            best_streak = max(best_streak, current_streak)
            bonus = 5 if current_streak % 3 == 0 else 0
            score += difficulty["points"] + bonus
            print(f"✅ Doğru! +{difficulty['points'] + bonus} puan")
            if bonus:
                print("🔥 3 cevaplık seri bonusu: +5 puan!")
        else:
            current_streak = 0
            print(f"❌ Yanlış. Doğru cevap: {expected}")

    show_result(score, correct_answers, total_questions, best_streak)


if __name__ == "__main__":
    try:
        play_game()
    except KeyboardInterrupt:
        print("\nOyun kapatıldı. Görüşürüz!")