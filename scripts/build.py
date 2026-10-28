from visual_examples import enhance_visual_document
"""Build a complete, readable public edition from the preserved source DOCX."""
from pathlib import Path
import json, html, re, hashlib, shutil
from prepare_source import read_source

ROOT=Path(__file__).resolve().parents[1]
BASE='https://auraofintelligence.github.io/aura-tourism/'
SOURCE=read_source()
BASELINE=json.loads((ROOT/'content/integrity-baseline.json').read_text(encoding='utf-8'))
if SOURCE['sha256'] != BASELINE['source_sha256']:
    raise SystemExit('Original source differs from its reviewed integrity baseline. Preserve the supplied document.')
if hashlib.sha256((ROOT/'LICENCE.md').read_bytes()).hexdigest() != BASELINE['licence_sha256']:
    raise SystemExit('Licence differs from its reviewed integrity baseline. Review the actual change before rebuilding.')
for filename,digest in BASELINE['font_files'].items():
    if hashlib.sha256((ROOT/'assets/fonts'/filename).read_bytes()).hexdigest() != digest:
        raise SystemExit('Font asset differs from its reviewed integrity baseline: '+filename)
PAGES=json.loads((ROOT/'content/pages.json').read_text(encoding='utf-8'))
PROJECTS=json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
ART={a['key']:a for a in json.loads((ROOT/'content/artwork.json').read_text(encoding='utf-8'))}
CHECKS=json.loads((ROOT/'content/source-checks.json').read_text(encoding='utf-8'))
PUBLIC=[('index','Home')]+[(p['slug'],p['short']) for p in PAGES]+[('sources','Sources and original document'),('projects','Connected projects'),('licence','Licence and rights'),('site-map','Site map')]
esc=lambda x:html.escape(str(x),quote=True)

def external(url,label,**attrs):
    extra=''.join(f' {k}="{esc(v)}"' for k,v in attrs.items())
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer"{extra}>{label}<span class="sr-only"> (opens in a new tab)</span></a>'

def nav(current):
    groups=[('Explore',PUBLIC[:1]+PUBLIC[1:6]),('People and places',PUBLIC[6:9]),('Develop and connect',PUBLIC[9:])]
    menu=''.join('<section><h2>'+title+'</h2><ul>'+''.join(f'<li><a href="{slug}.html"'+(' aria-current="page"' if current==slug else '')+f'>{esc(label)}</a></li>' for slug,label in links)+'</ul></section>' for title,links in groups)
    return f'''<header class="site-header"><div class="wrap header-row"><a class="brand" href="index.html" aria-label="Aura Tourism home"><span class="brand-mark" aria-hidden="true">a</span><span>Aura<span class="brand-sub">tourism</span></span></a><nav class="quick-nav" aria-label="Main navigation"><a href="music-sport-culture-nature.html">Experiences</a><a href="connected-places.html">Places</a><a href="hosts-and-community.html">Take part</a></nav><details class="all-pages"><summary>All pages <span aria-hidden="true">＋</span></summary><nav class="all-pages-panel" aria-label="All pages">{menu}</nav></details></div></header>'''

def footer(current):
    index=next((i for i,(s,_) in enumerate(PUBLIC) if s==current),0)
    prev=PUBLIC[(index-1)%len(PUBLIC)]; nxt=PUBLIC[(index+1)%len(PUBLIC)]
    return f'''<div class="wrap"><nav class="page-turn" aria-label="Previous and next pages"><a href="{prev[0]}.html"><span class="circle" aria-hidden="true">←</span><span>Previous<br><strong>{esc(prev[1])}</strong></span></a><a href="{nxt[0]}.html"><span>Next<br><strong>{esc(nxt[1])}</strong></span><span class="circle" aria-hidden="true">→</span></a></nav></div><footer class="site-footer"><div class="wrap footer-grid"><div><a class="brand" href="index.html">Aura Tourism</a><p>A personal-intelligence proposal by Luke Nathan Hayes, beginning on Minjerribah / North Stradbroke Island.</p></div><nav aria-label="Project and sources"><a href="sources.html">Sources and original document</a><a href="projects.html">Connected projects</a><a href="site-map.html">Site map</a></nav><nav aria-label="Rights and contact"><a href="licence.html">Strange But True licence</a>{external('https://github.com/auraofintelligence/aura-tourism','Source on GitHub ↗')}{external('https://auraofintelligence.github.io/strange-but-true/contact.html','Talk with Luke ↗')}</nav></div><div class="wrap footer-bottom"><p>© 2026 Luke Nathan Hayes / Strange But True / Aura of Intelligence.</p><p>Public proposal · Source edition 27 October 2026</p></div></footer><a class="to-top" href="#top"><span aria-hidden="true">↑</span><span>Top</span></a>'''

def page(slug,title,intro,body,image='coastal-day',noindex=False):
    canonical=BASE+('' if slug=='index' else slug+'.html')
    robots='<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow">'
    text=f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Aura Tourism</title><meta name="description" content="{esc(intro)}"><meta name="theme-color" content="#592681">{robots}<link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title)} | Aura Tourism"><meta property="og:description" content="{esc(intro)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}{ART[image or 'coastal-day']['file']}"><meta property="og:image:alt" content="{esc(ART[image or 'coastal-day']['alt'])}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/png" href="favicon.png"><link rel="preload" as="font" type="font/ttf" crossorigin href="assets/fonts/font-1.ttf"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script></head><body id="top"><a class="skip" href="#main">Skip to content</a>{nav(slug)}<main id="main">{body}</main>{footer(slug)}</body></html>'''
    if noindex:
        text=text.replace('<head>','<head><base href="'+BASE+'">',1)
    text=enhance_visual_document(slug,text)
    (ROOT/f'{slug}.html').write_text(text,encoding='utf-8')

def figure(key,wide=False,eager=False):
    a=ART[key]
    return f'<figure class="artwork {"wide-art" if wide else ""}"><img src="{a["file"]}" width="{a["width"]}" height="{a["height"]}" alt="{esc(a["alt"])}" '+('fetchpriority="high"' if eager else 'loading="lazy" decoding="async"')+'><figcaption>AI-generated concept artwork · An imagined scene.</figcaption></figure>'

def button(label,href,secondary=False):return f'<a class="button {"secondary" if secondary else ""}" href="{href}">{label}<span aria-hidden="true">↗</span></a>'
def hero(title,intro,kicker='Explore the proposal',number=None):return f'<section class="chapter-heading wrap"><p class="eyebrow">{esc(kicker)}'+(f' · Chapter {number:02d}' if number else '')+f'</p><h1>{title}</h1><p class="intro">{esc(intro)}</p></section>'

def citation_text(text):
    # Keep original visible punctuation and wording while linking each source marker.
    return re.sub(r'\[([PR][\dPR,\s\-–]+)\]',lambda m:'['+re.sub(r'[PR]\d+',lambda a:f'<a class="citation" href="sources.html#{a[0]}">{a[0]}</a>',m[1])+']',esc(text))

def inline(p):
    items=[]
    for r in p['runs']:
        t=esc(r['text']) if r.get('url') else citation_text(r['text'])
        if r.get('url'):t=external(r['url'],t)
        if r.get('bold'):t='<strong>'+t+'</strong>'
        if r.get('italic'):t='<em>'+t+'</em>'
        items.append(t)
    return ''.join(items)

def source_block(b,source_page=False):
    if b['type']=='table':
        rows=[]
        for i,row in enumerate(b['rows']):
            tag='th' if i==0 else 'td'
            rows.append('<tr>'+''.join(f'<{tag}'+(' scope="col"' if i==0 else '')+'>'+''.join('<p>'+inline(p)+'</p>' for p in cell)+f'</{tag}>' for cell in row)+'</tr>')
        return f'<div class="table-scroll" tabindex="0" role="region" aria-label="Source table {b["id"]}"><table data-source-table="{b["id"]}"><caption>Source table {b["id"]} · {esc(b["rows"][0][0][0]["text"])}</caption><thead>{rows[0]}</thead><tbody>'+''.join(rows[1:])+'</tbody></table></div>'
    if not b['text'].strip():return ''
    pid=b['id'];style=b['style'];source_ref=re.match(r'^([PR]\d+)\s',b['text'])
    tag='h2' if style in ('Heading1','Title') else 'h3' if style=='Heading2' else 'p'
    if source_page and source_ref:tag='h3'
    anchor=source_ref[1] if source_page and source_ref else f'p{pid}'
    return f'<{tag} id="{anchor}" data-source-p="{pid}">'+inline(b)+f'</{tag}>'

def blocks_for(start,end):return [b for b in SOURCE['blocks'] if (b['type']=='paragraph' and start<=b['id']<=end) or (b['type']=='table' and start<=b['after_paragraph']<=end)]

def source_reading(p):
    blocks=blocks_for(p['start'],p['end'])
    heads=[b for b in blocks if b['type']=='paragraph' and b['style']=='Heading1']
    if not heads:heads=[b for b in blocks if b['type']=='paragraph' and b['style']=='Heading2']
    toc='<aside class="contents"><details open><summary>In this chapter</summary><nav aria-label="Chapter contents">'+''.join(f'<a href="#p{b["id"]}">{esc(b["text"])}</a>' for b in heads)+'</nav></details><a href="sources.html#original">Download the original</a></aside>'
    reading=''.join(source_block(b) for b in blocks)
    return f'<section class="wrap reading-layout" id="reading">{toc}<article class="reading"><p class="reading-label">The original reading · Luke Nathan Hayes · 27 October 2026</p>{reading}</article></section>'

def chapter_cards(pages):return ''.join(f'<a class="chapter-card" href="{p["slug"]}.html" data-chapter-card data-theme="{p["theme"]}"><span class="eyebrow">{esc(p["theme"])}</span><h3>{esc(p["short"])}</h3><p>{esc(p["intro"])}</p><span class="text-link">Read the chapter <span aria-hidden="true">↗</span></span></a>' for p in pages)

home=hero('Explore the world.<br><em>Grow your own capability.</em>','Engage with AI on your own terms. Through music, sport, culture and nature, this proposed personal Aura connects enjoyable experiences with reflection, judgement and the life you choose.','A fair go in the age of superintelligence')
home+='<div class="wrap home-actions">'+button('Explore the experiences','music-sport-culture-nature.html')+button('Meet a personal Aura','personal-aura.html',True)+'</div>'
home+='<div class="wrap">'+figure('coastal-day',True,True)+'</div>'
home+='''<section class="section wrap"><div class="section-intro"><p class="eyebrow">The qualified self · A Protopian direction</p><h2>Raise the bar for<br>a life worth living.</h2><p>Luke Nathan Hayes’s proposal asks how growing intelligence could give people a fair go: more understanding, practical agency and opportunity to shape their own lives. Tourism supplies real encounters through which a person and their Aura could learn together.</p><p>Ethical engagement starts with a purpose you choose. You decide what may be observed and shared, question an interpretation, and correct what it misses. Steps, recordings and other measurements add context to your own explanations, values and experience. A useful result should carry into a later encounter and remain open to review.</p></div><ol class="journey"><li><span>01</span><h3>Begin with you</h3><p>Your words, circumstances, interests and boundaries form a starting account.</p></li><li><span>02</span><h3>Engage with the world</h3><p>Choose a real encounter, use suitable assistance and question what the technology contributes.</p></li><li><span>03</span><h3>Direct what comes next</h3><p>Keep useful learning, correct the interpretation and choose your next step, including rest.</p></li></ol><a class="text-link" href="reflection-and-memory.html">Explore reflection and memory ↗</a></section>'''
home+='''<section class="section sea-panel"><div class="wrap story-split"><div><p class="eyebrow">Find your scene</p><h2>A song. A game.<br>A conversation.<br>A quiet afternoon.</h2><p>Enjoyment and ambition belong in the same life. Make music, learn a sport, meet a host, explore a place or take a break. The proposed Aura supports a richer account of what you discover and the capability you want to develop.</p>'''+button('Find an experience','music-sport-culture-nature.html')+'</div>'+figure('music-evening')+'</div></section>'
home+='''<section class="section wrap" id="pace"><div class="section-intro"><p class="eyebrow">A small beginning</p><h2>What kind of day<br>would you choose?</h2><p>Try a reflection prompt for an imagined encounter. These prompts are examples; your choice stays in this page and no personal record is collected.</p></div><div class="pace-buttons" role="group" aria-label="Choose an example"><button type="button" data-pace="music" aria-pressed="true">Music and company</button><button type="button" data-pace="nature" aria-pressed="false">Nature and rest</button><button type="button" data-pace="learning" aria-pressed="false">Have a go</button></div><div class="prompt-card" data-pace-output aria-live="polite"><h3>Find what makes the music yours</h3><p>Before: what kind of company, sound and setting would you enjoy?</p><p>After: what mattered most — the music, the people, the place or the chance to take part?</p><a href="music-sport-culture-nature.html#p104">Read the music encounter ↗</a></div><noscript><p>Consider a quiet walk, a new sport or a music evening. What would you want from it, and what would you learn about yourself afterwards?</p></noscript></section>'''
home+='''<section class="section sand-panel"><div class="wrap story-split">'''+figure('nature-reflection')+'''<div><p class="eyebrow">A place to begin</p><h2>Straddie.<br>Then a wider horizon.</h2><p>Luke Nathan Hayes’s proposal begins on Minjerribah / North Stradbroke Island, widening through Redlands, Brisbane and Australia. A bounded first trial would test whether reviewed personal context helps in a later encounter.</p><p>Brisbane 2032 is a development horizon. The programme, pilots and connections described here remain proposals.</p>'''+button('Follow the places','connected-places.html')+'</div></div></section>'
home+='<section class="section wrap" id="chapters"><div class="section-intro"><p class="eyebrow">Take the longer journey</p><h2>Choose your way into the proposal</h2><p>Eleven chapters keep the complete original narrative and tables, with a source library alongside them.</p></div><div class="filters" data-filters hidden><span>Show chapters:</span>'+''.join(f'<button type="button" data-filter="{x}" aria-pressed="{str(x=="All").lower()}">{x}</button>' for x in ['All','Begin','Experience','Host','Place','Develop'])+'</div><p class="filter-count" data-filter-count aria-live="polite" hidden></p><div class="chapter-grid">'+chapter_cards(PAGES)+'</div></section>'
home+='''<section class="section sea-panel"><div class="wrap"><p class="eyebrow">Visitors, hosts and public agencies</p><h2>Bring a purpose.<br>Help shape the first experience.</h2><div class="invitation-grid"><article><h3>Visitors and residents</h3><p>Choose an enjoyable encounter, decide what it may observe and review what the account means to you.</p><a href="travel-stories.html">Follow two example visits ↗</a></article><article><h3>Operators and communities</h3><p>Define the offer, support access and distinguish paid roles from freely given contribution.</p><a href="hosts-and-community.html">Explore hosting and C-Hours ↗</a></article><article><h3>Tourism bodies and agencies</h3><p>Consider a defined stage, its responsibilities, resources and evidence of lasting benefit.</p><a href="public-programme.html">Read the discussion questions ↗</a></article></div></div></section>'''
home+='<section class="section wrap"><div class="closing"><h2>Read the proposal.<br>Follow its sources.</h2><p>Aura Tourism is a public proposal, not a booking service or a claim of an operating tourism programme. The original document and its source labels remain available for review.</p>'+button('Open the source library','sources.html')+button('See connected projects','projects.html',True)+'</div></section>'
page('index','Tourism, personal intelligence and a fair go','A fair go in the age of superintelligence: ethical personal AI, enjoyable travel, human agency and the qualified self, beginning on Straddie.',home)

for i,p in enumerate(PAGES,1):
    body=hero(esc(p['title']),p['intro'],p['theme'],i)
    if p['image']:body+='<div class="wrap chapter-art">'+figure(p['image'])+'</div>'
    body+='<div class="wrap"><div class="chapter-question"><span class="eyebrow">A question to carry with you</span><p>'+esc(p['question'])+'</p><a class="text-link" href="#reading">Read the full chapter ↓</a></div></div>'
    if p['slug']=='connected-places':
        body+='<section class="wrap practical-links"><h2>Check the actual journey</h2><p>Follow the current operator and public-information pages for a chosen trip. This proposal publishes no live timetable, fare or condition feed.</p><div class="link-row">'+''.join(external(url,label+' ↗') for label,url in [('Ferry timetables','https://www.sealink.com.au/north-stradbroke-island/ferry-information/timetable/'),('Island buses','https://www.stradbrokebus.com.au/'),('Weather','https://www.bom.gov.au/'),('Queensland traffic','https://qldtraffic.qld.gov.au/'),('Beachsafe','https://beachsafe.org.au/')])+'</div></section>'
    body+=source_reading(p)
    related=[]
    if p['slug'] in ['hosts-and-community','develop-together']:related=[('https://auraofintelligence.github.io/C-Hour-introduction/community-hours.html','How non-monetary C-Hours work'),('https://auraofintelligence.github.io/mutual-futures/travel.html','Mutual Futures: travel and chosen rest')]
    if p['slug']=='hosts-and-community':related+=[('https://auraofintelligence.github.io/mutual-futures/workforce.html','Mutual Futures: work and learning'),('https://auraofintelligence.github.io/mutual-futures/succession.html','Mutual Futures: generational handover')]
    if related:body+='<section class="wrap chapter-connections"><h2>Follow a connected idea</h2><div class="link-row">'+''.join(external(u,l+' ↗') for u,l in related)+'</div></section>'
    page(p['slug'],p['title'],p['intro'],body,p['image'])

# Source readings retain every reference's exact original label and destination.
body=hero('Sources, with their context intact','Read the original proposal, follow its project and public references, and distinguish the 27 October source edition from selected checks made for this website.','Evidence and original material')
body+='<section class="wrap source-original" id="original"><div><h2>The original document</h2><p>Aura of Intelligence for Tourism and Domestic Travel<br>Luke Nathan Hayes · 27 October 2026</p><p>The unchanged Word document is preserved alongside this readable web edition. All eight tables stay in their original narrative positions. The reference library contains 42 distinct linked destinations and retains their exact labels.</p><a class="button" href="'+SOURCE['source_path']+'" download>Download the original DOCX <span aria-hidden="true">↓</span></a></div><div class="hash-box"><h3>Source integrity</h3><p>SHA-256</p><code>'+SOURCE['sha256']+'</code><p>463 body paragraphs · 8 tables<br>43 hyperlink occurrences · 42 distinct destinations</p><a href="content/source-register.json">Read the source register</a></div></section>'
body+='<section class="wrap source-review"><h2>Selected checks on 28 October 2026</h2><p>'+esc(CHECKS['scope'])+'</p><details><summary>View the check notes</summary><ul>'+''.join(f'<li><a href="#{c["id"]}">{c["id"]}</a> · {esc(c["result"])}</li>' for c in CHECKS['checks'])+'</ul></details></section>'
body+='<section class="wrap sources-reading"><h2>Original reference library</h2><div class="source-search" hidden data-source-search><label for="source-query">Find a source by name, number or subject</label><input id="source-query" type="search" placeholder="Try privacy, Straddie, R22 or music" autocomplete="off"><p data-source-count aria-live="polite"></p></div><article class="reading source-list">'
entry_open=False
for b in blocks_for(375,463):
    if b['type']=='paragraph':
        is_ref=bool(re.match(r'^[PR]\d+\s',b['text']))
        if b['style']=='Heading1' or is_ref:
            if entry_open:body+='</section>';entry_open=False
        if is_ref:body+='<section class="reference-entry" data-source-entry>';entry_open=True
    body+=source_block(b,True)
if entry_open:body+='</section>'
body+='</article><p class="source-empty" data-source-empty hidden>No matching source. Try a name, source number or a broader subject.</p></section>'
page('sources','Sources and original document','The original Aura Tourism proposal, all 42 distinct source links, eight tables, source dates, verification notes and preserved document checksum.',body)

body=hero('Ideas that meet along the way','Follow each project for its own purpose, evidence and development status. These links describe a connected body of work; they do not establish an operating partnership.','The wider Aura family')
body+='<section class="wrap section project-grid">'+''.join('<article class="project-card"><h2>'+esc(p['title'])+'</h2><p>'+esc(p['text'])+'</p>'+external(p['url'],'Explore the project ↗')+'</article>' for p in PROJECTS)+'</section>'
page('projects','Connected projects','Aura, C-Hour, Mutual Futures, UNGA81 and place-based projects connected to the tourism proposal.',body)

licence=(ROOT/'LICENCE.md').read_text(encoding='utf-8-sig')
def markdown(text):
    out=[];list_open=False
    for line in text.splitlines():
        if not line.strip():
            if list_open:out.append('</ul>');list_open=False
            continue
        if line.startswith('- '):
            if not list_open:out.append('<ul>');list_open=True
            out.append('<li>'+esc(line[2:])+'</li>')
        else:
            if list_open:out.append('</ul>');list_open=False
            if line.startswith('# '):out.append('<h2>'+esc(line[2:])+'</h2>')
            elif line.startswith('## '):out.append('<h3>'+esc(line[3:])+'</h3>')
            else:out.append('<p>'+re.sub(r'https://[^\s<]+',lambda m:external(m[0],m[0]),esc(line))+'</p>')
    if list_open:out.append('</ul>')
    return ''.join(out)
body=hero('Licence and source rights','The Strange But True Public Source Licence governs original project material. Source documents, fonts and other third-party material retain their own rights.','Ownership and attribution')
body+='<section class="wrap reading utility-reading"><p><a href="LICENCE.md">Read the plain-text licence</a> · <a href="RIGHTS.md">Read the asset and source rights register</a></p>'+markdown(licence)+'<h2>Fonts and original concept artwork</h2><p>DM Sans and Manrope are bundled under the SIL Open Font License. Original AI-generated concept images are labelled as imagined scenes; they do not document a real event, host, partner or operational service.</p><div class="link-row"><a href="assets/fonts/DM-Sans-OFL.txt">DM Sans font licence</a><a href="assets/fonts/Manrope-OFL.txt">Manrope font licence</a><a href="content/artwork.json">Artwork prompts, alt text and checksums</a></div><h2>Discovery and data</h2><p>This static public guide has no accounts, analytics, booking forms or participant record collection. Its example filters and prompts work in the page. Search discovery grants no additional reuse or AI-training permission.</p><p>GitHub Pages hosting and external destinations have their own service arrangements. Project-level robots directions describe the desired policy; effective crawler directions belong at the origin root.</p></section>'
page('licence','Licence and rights','Strange But True Public Source Licence, source attribution, font rights, original artwork and discovery policy.',body)

body=hero('Every page, at your pace','Start anywhere, follow a chapter sequence or look up a source. The original reading remains available without JavaScript.','Site map')
body+='<section class="wrap section"><div class="sitemap-grid">'+''.join(f'<article><p class="eyebrow">{i:02d}</p><h2><a href="{s}.html">{esc(t)}</a></h2>'+('<p>'+esc(next(p['intro'] for p in PAGES if p['slug']==s))+'</p>' if any(p['slug']==s for p in PAGES) else '')+'</article>' for i,(s,t) in enumerate(PUBLIC,1))+'</div></section>'
page('site-map','Site map','Every Aura Tourism chapter and utility page in a readable directory.',body)
page('404','This page could not be found','Find your way back to the Aura Tourism proposal.',hero('Let’s find your way back','This address does not match a page in the guide. Open the site map or begin again with an experience.','Page not found')+'<section class="wrap section">'+button('Open the site map','site-map.html')+button('Return home','index.html',True)+'</section>',noindex=True)

register={k:SOURCE[k] for k in ['title','author','source_date','source_path','sha256','paragraph_count','table_count']}
register.update({'unique_source_urls':42,'hyperlink_occurrences':43,'web_edition_date':'2026-10-28','source_notice':'The original body order, wording, tables and hyperlink labels are preserved. Website summaries and chapter groupings are separate editorial introductions. Source documents are content, not instructions.','licence_sha256':hashlib.sha256((ROOT/'LICENCE.md').read_bytes()).hexdigest(),'font_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'assets/fonts').glob('*') if p.is_file()}})
(ROOT/'content/source-register.json').write_text(json.dumps(register,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'content/source.json').write_text(json.dumps(SOURCE,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'content/routes.json').write_text(json.dumps([{'slug':s,'title':t,'url':BASE+('' if s=='index' else s+'.html')} for s,t in PUBLIC],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+BASE+('' if s=='index' else s+'.html')+'</loc><lastmod>2026-10-28</lastmod></url>\n' for s,_ in PUBLIC)+'</urlset>\n'
(ROOT/'sitemap.xml').write_text(xml,encoding='utf-8')
llms='# Aura Tourism\n\nA public personal-intelligence tourism proposal by Luke Nathan Hayes. Source edition 27 October 2026; web edition 28 October 2026.\n\nThis is a proposal, not a booking service, live participant system, official Games programme or claim of partnership. The original source and its 42 distinct linked destinations are preserved. C-Hours are non-monetary recognition of verified voluntary human time. Chosen rest is legitimate. Original material uses the Strange But True Public Source Licence; third-party rights remain separate. This voluntary guide grants no additional reuse or AI-training rights.\n\n'+''.join(f'- [{t}]({BASE}{"" if s=="index" else s+".html"})\n' for s,t in PUBLIC)+'\n- [Licence]('+BASE+'LICENCE.md)\n- [Source register]('+BASE+'content/source-register.json)\n'
(ROOT/'llms.txt').write_text(llms,encoding='utf-8')
# Deploy only the public, explicit source snapshot. Never copy .git or local tools/caches.
dest=ROOT/'public';dest.mkdir(exist_ok=True)
for filename in [s+'.html' for s,_ in PUBLIC]+['404.html','sitemap.xml','robots.txt','llms.txt','LICENCE.md','RIGHTS.md','favicon.png','.nojekyll']:
    if (ROOT/filename).exists():shutil.copy2(ROOT/filename,dest/filename)
for dirname in ['assets','sources','content']:
    shutil.copytree(ROOT/dirname,dest/dirname,dirs_exist_ok=True)
report={'pages':len(PUBLIC),'not_found_pages':1,'chapters':len(PAGES),'source_paragraphs':463,'source_nonempty_paragraphs':sum(1 for b in SOURCE['blocks'] if b['type']=='paragraph' and b['text'].strip()),'tables':8,'distinct_source_destinations':42,'source_sha256':SOURCE['sha256'],'public_files':sum(1 for p in dest.rglob('*') if p.is_file())}
(ROOT/'docs/build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
