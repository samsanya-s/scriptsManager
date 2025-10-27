from lxml import etree


def processing_big_xml(file_path: str, tag_name: list):
    """
    Потоково читает большой XML файл и возвращает элементы с заданным тегом.
    
    :param file_path: путь к XML файлу
    :param tag_name: имя тега, который нужно обрабатывать
    :yield: элемент etree.Element
    """
    context = etree.iterparse(file_path, events=("end",), tag=tag_name, recover=True, huge_tree=True)
    
    for event, elem in context:
        yield elem
        
        # ⚙️ Очищаем элемент из памяти (важно для больших файлов!)
        elem.clear()
        
        # ⚙️ Удаляем обработанные ссылки на родителей, чтобы не накапливать дерево
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    del context  # очистить парсер


def transform_xml(input_file: str, output_file: str, codes: list=None):
    # parser = etree.XMLParser(recover=True, encoding="utf-8")
    # tree = etree.parse(input_file, parser)
    # root = tree.getroot()

    new_root = etree.Element("Data")

    for indicator in processing_big_xml(input_file, "Indicator"):
        code = indicator.findtext("Code") or ""

        if codes is not None and code not in codes:
            continue
        description = indicator.findtext("Description") or ""
        name = indicator.findtext("Name")  or ""
        mu_code = indicator.findtext("MUCode")  or ""
        type_val = indicator.findtext("Type") or "0"
        is_integer = indicator.findtext("IsInteger") == "1"
        is_system = indicator.findtext("IsSystem") == "1"
        allow_edit = indicator.findtext("AllowEditValues") == "1"

        type_map = {"0": "CALCULATED", "2": "LAST_DATE", "1": "PROGRESSIVE"}
        type_attr = type_map[type_val]

        new_indicator = etree.Element("Indicator", {
            "code": code ,
            "description": description,
            "isEditable": str(allow_edit).lower(),
            "isInteger": str(is_integer).lower(),
            "isSystem": str(is_system).lower(),
            "measurementUnit": mu_code,
            "name": name,
            "type": type_attr
        })

        new_root.append(new_indicator)
    # print(codes)

    new_tree = etree.ElementTree(new_root)
    new_tree.write(output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)


def main(input_xml: str, output_xml: str, codes: list=None):
    transform_xml(input_xml, output_xml, codes)

