import xml.etree.ElementTree as ET

def convert_dictionary_to_user_dict(dictionary):
    user_dict = ET.Element('UserDictionary', {
        'code': dictionary.attrib['Code'],
        'description': dictionary.attrib['Name'],
        'lineStartSearching': 'false',
        'name': dictionary.attrib['Name'],
        'sortField': 'orderIndex'
    })

    for value in dictionary.findall('Value'):
        code = value.attrib['Code']
        name = value.attrib['Name']
        if code == "5":
            continue  # Пропустить значение с Code="5"
        ET.SubElement(user_dict, 'Item', {'code': code, 'name': name})

    return user_dict

def append_to_existing_file(existing_file, new_user_dicts):
    try:
        tree = ET.parse(existing_file)
        root = tree.getroot()
        if root.tag != 'Data':
            print("Ошибка: корневой тег в целевом файле должен быть <Data>")
            return

        for user_dict in new_user_dicts:
            root.append(user_dict)

        tree.write(existing_file, encoding="utf-8", xml_declaration=True)
        print(f"XML успешно обновлён: {existing_file}")

    except Exception as e:
        print(f"Ошибка при обновлении файла: {e}")

def main(input_file, output_file, dictionary_code):
    # while 1:
        # dictionary_code = input("Введите код: ")
        # input_file = "C:\\Users\\a.medvedev\\Documents\\code\\dictionary.xml"

    try:
        input_tree = ET.parse(input_file)
        input_root = input_tree.getroot()

        dictionaries = input_root.findall(f'.//DictionaryTypeDTO[@Code="{dictionary_code}"]')
        if not dictionaries:
            print("Не найдено ни одного DictionaryTypeDTO.")
            return

        new_user_dicts = [convert_dictionary_to_user_dict(d) for d in dictionaries]

        # Укажи путь к существующему XML-файлу (с тегом <Data>)
        # output_file = "C:\\Users\\a.medvedev\\Documents\\scripts\\migrateConfEt2to3\\test_migr_ok\\dicts\\userDictionary\\userDictionary.xml"
        append_to_existing_file(output_file, new_user_dicts)

    except ET.ParseError as e:
        print(f"Ошибка разбора XML: {e}")

# if __name__ == "__main__":
#     main()