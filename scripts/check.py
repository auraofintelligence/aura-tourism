"""Validate actual page links, source fidelity, discovery and asset provenance."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json, hashlib, re, sys
from prepare_source import read_source

ROOT=Path(__file__).resolve().parents[1]
BASE='https://auraofintelligence.github.io/aura-tourism/'
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
errors=[]
def require(value,message):
    if not value:errors.append(message)
def normal(text):return re.sub(r'\s+',' ',text).strip()

class Page(HTMLParser):
    def __init__(self,path):
        super().__init__(convert_charrefs=True)
        self.path=path;self.ids=set();self.links=[];self.stack=[];self.ignore=[];self.source_paragraphs={};self.tables={};self.paragraph=None;self.cell=None;self.table=None;self.menus=[];self.in_allpages=False;self.canonical=None;self.has_skip=False;self.noindex=False;self.h1=0;self.source_order=[];self.base=None
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if tag not in VOID:self.stack.append(tag)
        if a.get('class')=='sr-only':self.ignore.append(len(self.stack))
        if 'id' in a:
            require(a['id'] not in self.ids,f'{self.path.name}: duplicate ID {a["id"]}')
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='base':self.base=a.get('href')
        if tag=='nav' and a.get('aria-label')=='All pages':self.in_allpages=True
        if tag=='a':
            self.links.append(('href',a.get('href',''),a))
            if self.in_allpages:self.menus.append(a.get('href'))
            if a.get('href')=='#main':self.has_skip=True
        if tag in ['img','script']:self.links.append(('src',a.get('src',''),a))
        if tag=='img':require(a.get('alt') and a.get('width') and a.get('height'),f'{self.path.name}: image lacks alt or intrinsic dimensions')
        if tag=='link':
            if a.get('rel')=='canonical':self.canonical=a.get('href')
            elif a.get('href'):self.links.append(('href',a['href'],a))
        if tag=='meta' and a.get('name')=='robots' and 'noindex' in a.get('content',''):self.noindex=True
        if 'data-source-p' in a:
            self.paragraph=[int(a['data-source-p']),len(self.stack),[]]
            self.source_order.append(('paragraph',int(a['data-source-p'])))
        if 'data-source-table' in a:
            self.table=[int(a['data-source-table']),len(self.stack),[]]
            self.source_order.append(('table',int(a['data-source-table'])))
        if self.table and tag in ['th','td']:self.cell=[len(self.stack),[]]
        if tag=='p' and self.cell:self.cell[1].append(' ')
    def handle_endtag(self,tag):
        depth=len(self.stack)
        if self.paragraph and depth==self.paragraph[1]:
            pid,_,parts=self.paragraph
            require(pid not in self.source_paragraphs,f'{self.path.name}: repeated source paragraph {pid}')
            self.source_paragraphs[pid]=normal(''.join(parts));self.paragraph=None
        if self.cell and depth==self.cell[0]:
            self.table[2].append(normal(''.join(self.cell[1])));self.cell=None
        if self.table and depth==self.table[1]:
            self.tables[self.table[0]]=self.table[2];self.table=None
        if self.ignore and depth==self.ignore[-1]:self.ignore.pop()
        if tag=='nav':self.in_allpages=False
        if self.stack and self.stack[-1]==tag:self.stack.pop()
        else:require(False,f'{self.path.name}: mismatched HTML end tag {tag}')
    def handle_data(self,data):
        if self.ignore:return
        if self.paragraph:self.paragraph[2].append(data)
        if self.cell:self.cell[1].append(data)

routes=json.loads((ROOT/'content/routes.json').read_text(encoding='utf-8'))
pages={p.name:Page(p) for p in ROOT.glob('*.html')}
all_routes={r['slug']+'.html' for r in routes}
require(len(all_routes)==16,'Expected home, eleven chapters and four utility pages')
for filename,p in pages.items():
    require(p.h1==1,f'{filename}: expected one document h1, found {p.h1}')
    require(p.has_skip,f'{filename}: missing skip link')
    require(set(p.menus)==all_routes,f'{filename}: full all-pages navigation does not match public routes')
    require(p.canonical==BASE+('' if filename=='index.html' else filename),f'{filename}: incorrect canonical')
    for kind,url,a in p.links:
        require(bool(url),f'{filename}: empty {kind}')
        parsed=urlsplit(url)
        if parsed.scheme in ['http','https']:
            if a.get('href') and a.get('target'):
                require(a.get('target')=='_blank' and {'noopener','noreferrer'}<=set(a.get('rel','').split()),f'{filename}: unsafe external rel {url}')
            if kind=='href' and a.get('target') is None and a.get('rel')!='canonical':require(False,f'{filename}: external link must open a new tab: {url}')
            continue
        if parsed.scheme:continue
        dest=(p.path.parent/unquote(parsed.path)).resolve() if parsed.path else p.path
        require(dest.is_relative_to(ROOT),f'{filename}: link escapes project: {url}')
        require(dest.exists(),f'{filename}: missing local destination {url}')
        if parsed.fragment and dest.suffix=='.html' and dest.exists():
            target=pages.get(dest.name)
            require(target is not None and unquote(parsed.fragment) in target.ids,f'{filename}: missing fragment {url}')

source=read_source();register=json.loads((ROOT/'content/source-register.json').read_text(encoding='utf-8'))
baseline=json.loads((ROOT/'content/integrity-baseline.json').read_text(encoding='utf-8'))
require(source['sha256']==baseline['source_sha256'],'Original source differs from reviewed baseline')
require(register['licence_sha256']==baseline['licence_sha256'],'Licence register differs from reviewed baseline')
require(source['sha256']==register['sha256'],'Original source checksum changed')
require(hashlib.sha256((ROOT/'LICENCE.md').read_bytes()).hexdigest()==register['licence_sha256'],'Licence checksum changed')
original={b['id']:normal(b['text']) for b in source['blocks'] if b['type']=='paragraph' and b['text'].strip()}
rendered={};tables={}
for filename,p in pages.items():
    for pid,text in p.source_paragraphs.items():
        require(pid not in rendered,f'Source paragraph {pid} appears on more than one route')
        rendered[pid]=text
    for tid,cells in p.tables.items():
        require(tid not in tables,f'Source table {tid} appears on more than one route')
        tables[tid]=cells
require(set(original)==set(rendered),f'Source paragraph coverage differs: missing {set(original)-set(rendered)}, extra {set(rendered)-set(original)}')
for pid,text in original.items():require(rendered.get(pid)==text,f'Source paragraph {pid} changed: expected {text[:90]!r}; got {rendered.get(pid,"")[:90]!r}')
for b in source['blocks']:
    if b['type']=='table':
        expected=[normal(' '.join(p['text'] for p in cell)) for row in b['rows'] for cell in row]
        require(tables.get(b['id'])==expected,f'Source table {b["id"]}: cell content or order changed')
expected_order=[(b['type'],b['id']) for b in source['blocks'] if b['type']=='table' or b['text'].strip()]
actual_order=[]
for route in routes:actual_order.extend(pages[route['slug']+'.html'].source_order)
require(actual_order==expected_order,'Source body sequence changed, including original table positions')
urls={h['url'] for h in source['hyperlinks']}
rendered_urls={url for p in pages.values() for kind,url,a in p.links if kind=='href'}
require(len(urls)==42,'Expected 42 distinct original source destinations')
require(urls<=rendered_urls,'Missing original source hyperlink destinations')
for key,digest in register['font_files'].items():require(hashlib.sha256((ROOT/'assets/fonts'/key).read_bytes()).hexdigest()==digest,f'Font asset changed: {key}')
for a in json.loads((ROOT/'content/artwork.json').read_text(encoding='utf-8')):
    path=ROOT/a['file'];require(path.exists(),f'Missing artwork {a["key"]}')
    require(hashlib.sha256(path.read_bytes()).hexdigest()==a['sha256'],f'Artwork hash mismatch {a["key"]}')
    require(a['prompt'] and a['alt'] and a['tool']=='built-in imagegen',f'Incomplete provenance {a["key"]}')
require(pages['404.html'].noindex,'404 must be noindex')
require(pages['404.html'].base==BASE,'404 recovery and assets need an absolute project base for nested missing paths')
sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
for route in routes:require('<loc>'+route['url']+'</loc>' in sitemap,f'Sitemap missing {route["slug"]}')
require('404.html' not in sitemap,'404 should not be indexed in XML sitemap')
robots=(ROOT/'robots.txt').read_text(encoding='utf-8')
for name in ['GPTBot','ClaudeBot','Google-Extended','OAI-SearchBot','Claude-SearchBot']:require('User-agent: '+name in robots,f'Missing crawler policy {name}')
require('.github/robots-root-snippet.txt' in robots,'Project robots must explain origin-root deployment')
for route in routes:require((ROOT/'public'/(route['slug']+'.html')).read_bytes()==(ROOT/(route['slug']+'.html')).read_bytes(),f'Public package differs for {route["slug"]}')
js=(ROOT/'assets/site.js').read_text(encoding='utf-8')
require(not re.search(r'\b(fetch|XMLHttpRequest|localStorage|sessionStorage|sendBeacon)\b',js),'Public script unexpectedly sends or retains data')
report={'status':'passed' if not errors else 'failed','public_routes':len(routes),'html_files':len(pages),'source_nonempty_paragraphs':len(original),'source_tables':len(tables),'unique_source_urls':len(urls),'artworks':3,'checks':['local href and src destinations','all fragments','one h1 per page','full native all-pages menu','external tab and rel policy','all source paragraph wording and coverage','all source table cells and order','original source/font/licence/artwork checksums','canonical URLs and sitemaps','404 noindex','crawler-policy presence','public package equality','no browser storage or network capture'],'errors':errors}
(ROOT/'docs/check-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
