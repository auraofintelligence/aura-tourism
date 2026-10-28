"""Read the unchanged source document in body order, including all eight tables."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources/originals/Aura_of_Intelligence_Tourism_and_Domestic_Travel.docx'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def read_source():
    with ZipFile(SOURCE) as archive:
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(archive.read('word/_rels/document.xml.rels'))}
        body = ET.fromstring(archive.read('word/document.xml')).find(W+'body')
        blocks, links, paragraph_id, table_id = [], [], 0, 0
        def paragraph(p):
            runs = []
            def visit(node, url=None):
                if node.tag == W+'hyperlink':
                    url = rels.get(node.attrib.get(R+'id'))
                if node.tag == W+'r':
                    text = ''.join((c.text or '') if c.tag == W+'t' else '\n' if c.tag == W+'br' else '\t' if c.tag == W+'tab' else '' for c in node)
                    if text:
                        prop = node.find(W+'rPr')
                        item = {'text':text}
                        if url: item['url'] = url
                        if prop is not None:
                            if prop.find(W+'b') is not None: item['bold'] = True
                            if prop.find(W+'i') is not None: item['italic'] = True
                        runs.append(item)
                else:
                    for child in node: visit(child, url)
            visit(p)
            style = p.find(W+'pPr/'+W+'pStyle')
            return {'text':''.join(r['text'] for r in runs), 'style':style.attrib.get(W+'val','body') if style is not None else 'body', 'runs':runs}
        for child in body:
            if child.tag == W+'p':
                paragraph_id += 1
                p = paragraph(child)
                p.update(type='paragraph', id=paragraph_id)
                blocks.append(p)
                for run in p['runs']:
                    if run.get('url'): links.append({'paragraph':paragraph_id, 'label':run['text'], 'url':run['url']})
            elif child.tag == W+'tbl':
                table_id += 1
                rows = [[[paragraph(p) for p in cell.findall(W+'p')] for cell in row.findall(W+'tc')] for row in child.findall(W+'tr')]
                blocks.append({'type':'table','id':table_id,'after_paragraph':paragraph_id,'rows':rows})
        return {'title':'Aura of Intelligence for Tourism and Domestic Travel','author':'Luke Nathan Hayes','source_date':'2026-10-27','source_path':str(SOURCE.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'paragraph_count':paragraph_id,'table_count':table_id,'hyperlinks':links,'blocks':blocks}

if __name__ == '__main__':
    content = ROOT / 'content'
    content.mkdir(exist_ok=True)
    data = read_source()
    (content/'source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Preserved {data['paragraph_count']} paragraphs, {data['table_count']} tables and {len(data['hyperlinks'])} hyperlinks in original body order.")
