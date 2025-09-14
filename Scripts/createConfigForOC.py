import xml.etree.ElementTree as ET
CONFIG_TEMPLATE_NESTED = '''<DirectoryConfigItem {last} id="nestedEntityType{num}">
  <Directory>/{type}/nestedEntityType</Directory>
  <Export>
    <Type name="NestedEntityType">
      <ExportData filterBlocksJoinPolicy="OR">
        <Filters>
          <CompareDataFilter id="nestedEntityTypeFilter" joinPolicy="OR" name="NestedEntityTypeCode">
            <StringFilterValue>{type}</StringFilterValue>
          </CompareDataFilter>
        </Filters>
        <FilterBlocks>
          <FilterBlock joinPolicy="OR">
            <ClassNames>
              <ClassName>NestedEntityType</ClassName>
            </ClassNames>
            <Filter>nestedEntityTypeFilter</Filter>
          </FilterBlock>
        </FilterBlocks>
      </ExportData>
    </Type>
  </Export>
</DirectoryConfigItem>==next==
<DirectoryConfigItem dependsOn="nestedEntityType{num}" id="metaEntitySchema{num}">
  <Directory>/{type}/metaEntitySchema</Directory>
  <Export>
    <Type name="MetaEntitySchema">
      <ExportData filterBlocksJoinPolicy="OR">
        <Filters>
          <CompareDataFilter id="nestedEntityTypeFilter" joinPolicy="OR" name="NestedEntityTypeCode">
            <StringFilterValue>{type}</StringFilterValue>
          </CompareDataFilter>
        </Filters>
        <FilterBlocks>
          <FilterBlock joinPolicy="OR">
            <ClassNames>
              <ClassName>MetaEntity</ClassName>
            </ClassNames>
            <Filter>nestedEntityTypeFilter</Filter>
          </FilterBlock>
        </FilterBlocks>
      </ExportData>
    </Type>
  </Export>
</DirectoryConfigItem>==next==
<DirectoryConfigItem dependsOn="metaEntitySchema{num}" id="nestedEntityTypeData{num}">
  <Directory>/{type}/nestedEntityTypeData</Directory>
  <Export>
    <Type name="NestedEntityTypeData">
      <ExportData filterBlocksJoinPolicy="OR">
        <Filters>
          <CompareDataFilter id="nestedEntityTypeFilter" joinPolicy="OR" name="NestedEntityTypeCode">
            <StringFilterValue>{type}</StringFilterValue>
          </CompareDataFilter>
        </Filters>
        <FilterBlocks>
          <FilterBlock joinPolicy="OR">
            <ClassNames>
              <ClassName>NestedEntityType</ClassName>
            </ClassNames>
            <Filter>nestedEntityTypeFilter</Filter>
          </FilterBlock>
        </FilterBlocks>
      </ExportData>
    </Type>
  </Export>
</DirectoryConfigItem>==next==
<DirectoryConfigItem dependsOn="nestedEntityTypeData{num}" id="dynamicForm{num}">
  <Directory>/{type}/dynamicForm</Directory>
  <Export>
    <Type name="DynamicForm">
      <ExportData filterBlocksJoinPolicy="OR">
        <Filters>
          <CompareDataFilter id="nestedEntityTypeFilter" joinPolicy="OR" name="NestedEntityTypeCode">
            <StringFilterValue>{type}</StringFilterValue>
          </CompareDataFilter>
        </Filters>
        <FilterBlocks>
          <FilterBlock joinPolicy="OR">
            <ClassNames>
              <ClassName>FormDefinition</ClassName>
            </ClassNames>
            <Filter>nestedEntityTypeFilter</Filter>
          </FilterBlock>
        </FilterBlocks>
      </ExportData>
    </Type>
  </Export>
</DirectoryConfigItem>'''

CONFIG_TEMPLATE_OBJECT = '''<DirectoryConfigItem {last} id="controlObjectType{num}">
      <Directory>/{type}/controlObjectType</Directory>
      <Export>
        <Type name="ControlObjectType">
          <ExportData filterBlocksJoinPolicy="OR">
            <Filters>
              <CompareDataFilter id="controlObjectTypeFilter" joinPolicy="OR" name="ControlObjectTypeCode">
                <StringFilterValue>{type}</StringFilterValue>
              </CompareDataFilter>
            </Filters>
            <FilterBlocks>
              <FilterBlock joinPolicy="OR">
                <ClassNames>
                  <ClassName>ControlObjectType</ClassName>
                </ClassNames>
                <Filter>controlObjectTypeFilter</Filter>
              </FilterBlock>
            </FilterBlocks>
          </ExportData>
        </Type>
      </Export>
    </DirectoryConfigItem>==next==
    <DirectoryConfigItem dependsOn="controlObjectType{num}" id="metaEntitySchema{num}">
      <Directory>/{type}/metaEntitySchema</Directory>
      <Export>
        <Type name="MetaEntitySchema">
          <ExportData filterBlocksJoinPolicy="OR">
            <Filters>
              <CompareDataFilter id="controlObjectTypeFilter" joinPolicy="OR" name="ControlObjectTypeCode">
                <StringFilterValue>{type}</StringFilterValue>
              </CompareDataFilter>
            </Filters>
            <FilterBlocks>
              <FilterBlock joinPolicy="OR">
                <ClassNames>
                  <ClassName>MetaEntity</ClassName>
                </ClassNames>
                <Filter>controlObjectTypeFilter</Filter>
              </FilterBlock>
            </FilterBlocks>
          </ExportData>
        </Type>
      </Export>
    </DirectoryConfigItem>==next==
    <DirectoryConfigItem dependsOn="metaEntitySchema{num}" id="controlObjectTypeData{num}">
      <Directory>/{type}/controlObjectTypeData</Directory>
      <Export>
        <Type name="ControlObjectTypeData">
          <ExportData filterBlocksJoinPolicy="OR">
            <Filters>
              <CompareDataFilter id="controlObjectTypeFilter" joinPolicy="OR" name="ControlObjectTypeCode">
                <StringFilterValue>{type}</StringFilterValue>
              </CompareDataFilter>
            </Filters>
            <FilterBlocks>
              <FilterBlock joinPolicy="OR">
                <ClassNames>
                  <ClassName>ControlObjectType</ClassName>
                </ClassNames>
                <Filter>controlObjectTypeFilter</Filter>
              </FilterBlock>
            </FilterBlocks>
          </ExportData>
        </Type>
      </Export>
    </DirectoryConfigItem>==next==
    <DirectoryConfigItem dependsOn="controlObjectTypeData{num}" id="dynamicForm{num}">
      <Directory>/{type}/dynamicForm</Directory>
      <Export>
        <Type name="DynamicForm">
          <ExportData filterBlocksJoinPolicy="OR">
            <Filters>
              <CompareDataFilter id="controlObjectTypeFilter" joinPolicy="OR" name="ControlObjectTypeCode">
                <StringFilterValue>{type}</StringFilterValue>
              </CompareDataFilter>
            </Filters>
            <FilterBlocks>
              <FilterBlock joinPolicy="OR">
                <ClassNames>
                  <ClassName>FormDefinition</ClassName>
                </ClassNames>
                <Filter>controlObjectTypeFilter</Filter>
              </FilterBlock>
            </FilterBlocks>
          </ExportData>
        </Type>
      </Export>
    </DirectoryConfigItem>'''

CONFIG_DICTIONARY = '''<FileConfigItem id="userDictionary">
      <FileName>dicts/userDictionary/userDictionary.xml</FileName>
      <Export>
        <Type name="UserDictionary">
          <ExportData filterBlocksJoinPolicy="OR">
            <Filters>
              <CompareDataFilter id="DictionaryFilter" joinPolicy="OR" name="DictionaryTypeCode">
              </CompareDataFilter>
            </Filters>
            <FilterBlocks>
              <FilterBlock joinPolicy="OR">
                <ClassNames>
                  <ClassName>DictionaryType</ClassName>
                </ClassNames>
                <Filter>DictionaryFilter</Filter>
              </FilterBlock>
            </FilterBlocks>
          </ExportData>
        </Type>
      </Export>
    </FileConfigItem>'''


def main(INPUT_DIR, OUTPUT_FILE):
  # INPUT_DIR = r'C:\Users\a.medvedev\Documents\ПолныйОКПроектПортфеля\ПолныйОКПроектПортфеля\Event'
  META_FILE = INPUT_DIR + r'\metaEntitySchema\metaEntitySchema.xml'
  FORM_FILE = INPUT_DIR + r'\dynamicForm\dynamicForm.xml'
  # OUTPUT_FILE = r'C:\Users\a.medvedev\Documents\temp\config-manifest.xml'
  tree = ET.parse(META_FILE)
  root = tree.getroot()
  main_root = ET.Element('ConfigurationManifest')
  items = ET.Element('ConfigItems')
  main_root.append(items)
  dictionary_root = ET.fromstring(CONFIG_DICTIONARY)
  items.append(dictionary_root)
  last = 'userDictionary'
  num = 1
  root_obj = ET.parse(FORM_FILE).getroot()
  obj_type = root_obj.find('DynamicForm').get('name')

  for attr in root.findall('.//TypeParameter'):
      if attr.get('typeName') in ('ResourceLinkListDDT', 'ResourceLinkDDT'):
          if attr.get('resourceName').startswith('dictionary-'):
              new_filter = ET.Element('StringFilterValue')
              new_filter.text = attr.get('resourceName').replace('dictionary-', '')
              dictionary_root.find('.//CompareDataFilter').append(new_filter)
              print(f'add dict: {attr.get('resourceName').replace('dictionary-', '')}')
          elif attr.get('resourceName') == 'nested-entity-object':
              for nest_el in CONFIG_TEMPLATE_NESTED.split('==next=='):
                  add_nested = ET.fromstring(nest_el.replace('{last}', f'dependsOn="{last}"').replace('{num}', f'{obj_type}{num}').replace('{type}', attr.get('dynamicObjectType')))
                  items.append(add_nested)
              last = f'dynamicForm{num}'
              num += 1
              print(f'add nest: {attr.get('dynamicObjectType')}')
          else:
              print(f'can not add: {attr.attrib}')

  for  obj_el in CONFIG_TEMPLATE_OBJECT.split('==next=='):
      obj_item = ET.fromstring(obj_el.replace('{last}', f'dependsOn="{last}"').replace('{num}', f'{obj_type}').replace('{type}', obj_type))
      items.append(obj_item)

  new_tree = ET.ElementTree(main_root)
  new_tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
  print('finish!')