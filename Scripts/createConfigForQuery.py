import xml.etree.ElementTree as ET
CONFIG_TEMPLATE_QUERY = '''<?xml version="1.0" encoding="UTF-8"?>
<ConfigurationManifest>
<ExportData filterBlocksJoinPolicy="OR">
    <Filters>
      <CompareDataFilter id="queryEntityFilter" name="ConfigurableQueryCode" joinPolicy="OR">
      </CompareDataFilter>
    </Filters>
   <FilterBlocks>
      <FilterBlock joinPolicy="OR">
        <ClassNames>
          <ClassName>QueryEntity</ClassName>
        </ClassNames>
        <Filter>queryEntityFilter</Filter>
      </FilterBlock>
    </FilterBlocks>
  </ExportData>

  <ConfigItems type="User">
    <DirectoryConfigItem id="ConfigurableQuery">
      <Directory>/queries</Directory>
      <Import>
        <Type name="EntityQuery" importMode="UPDATE"/>
      </Import>
      <Export>
        <Type name="EntityQuery" exportPolicy="OneFile"/>
      </Export>
    </DirectoryConfigItem>
  </ConfigItems>

</ConfigurationManifest>'''


def main(INPUT_FILE, OUTPUT_FILE):
# INPUT_FILE = r'C:\Users\a.medvedev\Documents\code\sho_conf\queryLaborInKanban\queries\entityQuery.xml'
# OUTPUT_FILE = r'C:\Users\a.medvedev\Documents\temp\config-manifest.xml'
  tree = ET.parse(INPUT_FILE)
  root = tree.getroot()
  main_root = ET.fromstring(CONFIG_TEMPLATE_QUERY)
  export_data = main_root.find('.//CompareDataFilter')


  for attr in root.findall('.//EntityProvider'):
    new_filter = ET.Element('StringFilterValue')
    new_filter.text = attr.text
    export_data.append(new_filter)

  new_tree = ET.ElementTree(main_root)
  new_tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
  print(OUTPUT_FILE)
  print('finish!')