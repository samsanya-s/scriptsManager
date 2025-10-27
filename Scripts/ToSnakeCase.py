import re
import pyperclip
from langdetect import detect
from deep_translator import GoogleTranslator
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
 
# Инициализируем модель один раз
kw_model = KeyBERT(model=SentenceTransformer('all-MiniLM-L6-v2'))
 
# Английские и русские стоп-слова
EN_STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'as', 'with', 'without',
    'to', 'from', 'by', 'in', 'on', 'at', 'for', 'of', 'into', 'over', 'under',
    'through', 'during', 'before', 'after', 'between', 'about', 'around',
}
 
RU_STOP_WORDS = {
    'и', 'в', 'на', 'по', 'с', 'со', 'без', 'из', 'от', 'до', 'у', 'за', 'о',
    'об', 'про', 'для', 'между', 'при', 'над', 'под', 'через', 'во', 'как', 'но', 'а'
}
 
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'  # по умолчанию
 
def translate_if_needed(text):
    word_count = len(text.strip().split())
 
    try:
        lang = detect(text)
    except:
        lang = 'unknown'
 
    # Если мало слов или язык не определён — форсируем перевод
    if lang == 'ru' or lang == 'unknown' or word_count <= 4:
        try:
            return GoogleTranslator(source='ru', target='en').translate(text)
        except:
            pass  # Если не удалось перевести — вернём как есть
 
    return text
 
def clean_keywords(keywords, stop_words, min_len=3):
    # Фильтруем ключевые слова
    result = []
    for word, _ in keywords:
        word = re.sub(r'[^\w]', '', word.lower())
        if word and len(word) >= min_len and word not in stop_words:
            result.append(word)
    return result
 
def smart_snake_case(text, max_words=5):
    keywords = kw_model.extract_keywords(text, top_n=15, stop_words='english')
    stop_words = EN_STOP_WORDS  # поскольку текст уже переведён
    cleaned = clean_keywords(keywords, stop_words)
    return '_'.join(cleaned[:max_words])
 
def main():
    print("💡 Введите строку (Ctrl+C для выхода):")
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            translated = translate_if_needed(user_input)
            result = smart_snake_case(translated)
            pyperclip.copy(result)
            print(f"✅ Скопировано в буфер обмена: {result}\n")
        except KeyboardInterrupt:
            print("\n🚪 Выход из программы.")
            break
        except Exception as e:
            print(f"⚠️ Ошибка: {e}\n")

def api_function(user_input):
    try:
        if not user_input:
            return 
        translated = translate_if_needed(user_input)
        result = smart_snake_case(translated)
        return result
    except Exception as e:
        return f"⚠️ Ошибка: {e}\n"
    

 
if __name__ == "__main__":
    main()