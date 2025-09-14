import os
import xml.etree.ElementTree as ET
from lxml import etree
import os
from tqdm import tqdm
from pathlib import Path

def parse_folder(folder_path, get_full_path=False):
    """получить название файлов и root всех xml файлов в папке (с прогресс-баром)"""
    roots = []
    filenames = []

    xml_files = []
    for root_dir, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(".xml"):
                xml_files.append(os.path.join(root_dir, filename))

    for file_path in tqdm(xml_files, desc="Парсинг XML", unit="файл"):
        try:
            p = Path(file_path).resolve()
            file_path = "\\\\?\\" + str(p)

            tree = ET.parse(file_path)
            root = tree.getroot()
            roots.append(root)

            if get_full_path:
                filenames.append(file_path)
            else:
                filenames.append(os.path.basename(file_path))

        except Exception as ex:
            print(f"Ошибка: {ex} — {file_path}")

    return roots, filenames

def print_data(data, to_file=None, mode_file='w'):
    if to_file:
        if not os.path.exists(to_file):
            with open(to_file, 'w', encoding='utf-8') as file:
                file.write('')
        if isinstance(data, str):
            with open(to_file, mode_file, encoding='utf-8') as file:
                file.write(data)
        elif isinstance(data, etree._Element):
            tree = etree.ElementTree(data)
            tree.write(
                to_file,
                encoding="utf-8",
                pretty_print=True,
                xml_declaration=False  # ❌ отключает <?xml version="1.0" ?>
            )
    else:
        if isinstance(data, str):
            print(data)
        elif isinstance(data, etree._Element):
            print(
                etree.tostring(
                    data,
                    encoding="unicode",
                    pretty_print=True,
                    xml_declaration=False  # ❌ и тут отключаем
                ))
            

def find_file_by_tag(folder_path, tag, add_filter_tag, names_find=None):
    roots, filenames = parse_folder(folder_path, True)
    for num, root in enumerate(roots):
        for name in names_find:
            if len(root.findall(f".//{add_filter_tag}[@{tag}='{name}']")):
                print_data(name, filenames[num])


def main(folder_find, tag, names, add_filter_tag=''):
    find_file_by_tag(folder_find, tag, add_filter_tag, names)