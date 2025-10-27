import os
from lxml import etree

def find_xml_with_query(root_folder: str, search_text: str = "eav_projection_data"):
    """
    Рекурсивно обходит папку, ищет XML-файлы и проверяет,
    содержит ли тег <QuerySQL> указанное слово.
    Если содержит — выводит путь к файлу.
    """
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(".xml"):
                file_path = os.path.join(dirpath, filename)
                try:
                    # Потоковый парсер, чтобы не грузить весь XML в память
                    for _, elem in etree.iterparse(file_path, events=("end",), tag="QuerySQL", recover=True):
                        if elem.text and search_text in elem.text:
                            print(file_path)
                            break  # Дальше можно не проверять этот файл
                        elem.clear()
                except Exception as e:
                    print(f"⚠️ Ошибка при чтении {file_path}: {e}")

def main(folder: str):
    find_xml_with_query(folder)
# if __name__ == "__main__":
#     folder = input("Введите путь к папке: ").strip()
#     find_xml_with_query(folder)
