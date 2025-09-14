import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
import os


def parse_folder(folder_path, get_full_path=False):
    """получить название файлов и root всех xml файлов в папке"""
    roots =[]
    filenames = []
    for root_dir, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(".xml"):
                file_path = os.path.join(root_dir, filename)
                try:
                    if len(file_path) > 260:
                        file_path = r"\\?\{}".format(file_path)
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    roots.append(root)
                    if get_full_path:
                        filenames.append(file_path)
                    else:
                        filenames.append(filename)
                except Exception as ex:
                    print(ex)
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
                )
            )


def find_ind_code_in_rules(folder_path, get_rule=False, names_find=None, to_file=None):
    """Найти все коды показателей и файлы показателей в файлах правил расчёта показателей"""
    roots, filenames = parse_folder(folder_path, True)
    for num, root in enumerate(roots):
        if not get_rule:
            for entity in root.findall(".//IndicatorCode"):
                code = entity.text
                if not names_find:
                    print(code, filenames[num])
                elif code in names_find:
                    print(code, filenames[num])
        else:
            for entity in root.findall(".//StoredMeasureCalculationRules"):
                codes = entity.findall(".//IndicatorCode")
                
                if not names_find:
                    print_data(entity, to_file=to_file, mode_file='a')
                    print_data(f'{code}')
                else:
                    for code in codes:
                        if code.text in names_find:
                            print_data(f'{code.text}')
                            print_data(entity, to_file=to_file, mode_file='a')
                            break


def find_ind_code_in_inds(folder_path, names_find=None):
    """Найти все коды показателей и файлы показателей в файлах показателей"""
    roots, filenames = parse_folder(folder_path, True)
    for num, root in enumerate(roots):
        for entity in root.findall(".//Indicator"):
            code = entity.get('code')
            if not names_find:
                print(code)
            elif code in names_find:
                print(code, filenames[num])

def find_uniq_ind_mu_in_inds(folder_path):
    """Найти все уникальные коды единиц измерения для показателей в файлах показателей"""
    roots, filenames = parse_folder(folder_path)
    measurements_unit = set()
    for num, root in enumerate(roots):
        for entity in root.findall(".//Indicator"):
            mu = entity.get('measurementUnit')
            measurements_unit.add(mu)
    print(measurements_unit)


def find_queries(folder_path,  names_find=None):
    roots, filenames = parse_folder(folder_path, True)
    for num, root in enumerate(roots):
        for entity in root.findall('.//EntityQuery/Code'):
            code = entity.text
            for name in names_find:
                if code == name:
                    print(code, filenames[num])
                    break


if __name__ == "__main__":
    code_inds = ('LaborInKanban ',)
    # print(len(code_inds))
    # folder = input("Введите путь к папке с XML файлами: ").strip()
    folder = r'C:\Users\a.medvedev\Desktop\git conf\eta_config_configurators_group\JET'
    # folder = r'C:\Users\a.medvedev\Documents\code\sho_conf\Indicators\Indicator'

    find_queries(folder, names_find=code_inds)

