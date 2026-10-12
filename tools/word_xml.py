"""Small OpenXML helpers shared by the current editable Word exporter."""
import xml.etree.ElementTree as ET

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


def node(parent, tag, text=None, **attrs):
    prefix, name = tag.split(':')
    element = ET.SubElement(parent, '{' + NS[prefix] + '}' + name)
    for key, value in attrs.items():
        element.set('{' + NS[prefix] + '}' + key, str(value))
    if text is not None:
        element.text = text
    return element


def serialize(element):
    return ET.tostring(element, encoding='utf-8', xml_declaration=True)
