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


def api_function(user_input):
    # return user_input
    try:
        if not user_input:
            return 
        translated = translate_if_needed(user_input)
        result = smart_snake_case(translated)
        return result
    except Exception as e:
        return f"⚠️ Ошибка: {e}\n"

import xml.etree.ElementTree as ET


def print_xml_tree_detailed(element, indent=0, path=""):
    """Печатает XML-дерево с путями и подробной информацией"""
    current_path = f"{path}/{element.tag}" if path else element.tag
    
    # Открывающий тег с атрибутами
    tag_line = ' ' * indent + f"<{element.tag}"
    for attr, value in element.attrib.items():
        tag_line += f' {attr}="{value}"'
    
    if len(element) == 0 and not element.text:
        print(tag_line + " />")
    else:
        print(tag_line + ">")
        
        # Текст элемента
        if element.text and element.text.strip():
            print(' ' * (indent + 2) + f"TEXT: {element.text.strip()}")
        
        # Дочерние элементы
        for i, child in enumerate(element):
            child_path = f"{current_path}[{i+1}]"
            print_xml_tree_detailed(child, indent + 2, current_path)
        
        print(' ' * indent + f"</{element.tag}>")


def create_section(name):
    code_section = api_function(name)
    print(f'create section: {code_section}')
    return ET.Element("TabSection", {'code': code_section, 'name': name})


def create_tab(name, sections):
    code_tab = api_function(name)
    print(f'create tab: {code_tab}')
    attrs_tab = {
        'code': code_tab, 
        'icon': 'menu_new',
        'name': name,
        'type': 'CUSTOM'
    }
    tab = ET.Element("FormTab", attrs_tab)
    for el in sections:
        tab.append(create_section(el))
    # print_xml_tree_detailed(tab)
    return tab


def main(input_file, output_file):
    structure = {}

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            structure[line.split(',')[0].strip()] = list(map(lambda x: x.strip(), line.split(',')[1:]))
    
    root = ET.parse(output_file).getroot()
    dn_form = root.find(".//DynamicForm")

    for item in structure.items():
        dn_form.append(create_tab(*item))
    
    # print_xml_tree_detailed(dn_form)

    new_tree = ET.ElementTree(root)
    new_tree.write(output_file, encoding="utf-8", xml_declaration=True)

