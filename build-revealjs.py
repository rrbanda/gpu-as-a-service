#!/usr/bin/env python3
"""Build reveal.js agentic deck from spec + speaker notes + images."""

import json, re, os, html

SPEC_PATH = '/Users/raghurambanda/workspace/slide-creator/agentic-deck-spec.json'
NOTES_PATH = '/Users/raghurambanda/workspace/gpu-as-a-service/AGENTIC_SPEAKER_NOTES.md'
OUT_PATH = '/Users/raghurambanda/workspace/gpu-as-a-service/agentic-slides.html'
IMG_DIR = '/Users/raghurambanda/workspace/gpu-as-a-service'

IMG_MAP = {
    '/Users/raghurambanda/workspace/slide-creator/agentic-fig1-blueprint.png': 'agentic-fig1-blueprint.b64',
    '/Users/raghurambanda/workspace/slide-creator/agentic-fig2-workload-vs-service.png': 'agentic-fig2-workload-vs-service.b64',
    '/Users/raghurambanda/workspace/slide-creator/agentic-fig3-routing-tiers.png': 'agentic-fig3-routing-tiers.b64',
    '/Users/raghurambanda/workspace/slide-creator/agentic-fig4-defense-rings.png': 'agentic-fig4-defense-rings.b64',
    '/Users/raghurambanda/workspace/slide-creator/agentic-fig5-supervisor-pattern.png': 'agentic-fig5-supervisor-pattern.b64',
}

def load_b64(path):
    b64_file = os.path.join(IMG_DIR, IMG_MAP.get(path, ''))
    if os.path.exists(b64_file):
        with open(b64_file) as f:
            return f.read().strip()
    return ''

def parse_speaker_notes(path):
    with open(path) as f:
        text = f.read()
    notes = {}
    parts = re.split(r'###\s+Slide\s+(\d+):', text)
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        content = parts[i+1].strip()
        content = re.split(r'\n---\s*$', content, flags=re.MULTILINE)[0].strip()
        notes[num] = content
    return notes

def h(t):
    return html.escape(str(t))

def icon_svg(name, color='#EE0000', size=40):
    icons = {
        'brain': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M12 2a5 5 0 0 0-5 5c0 1.5.5 2.5 1 3.5S7 13 7 14.5C7 17 9 19 12 22c3-3 5-5 5-7.5 0-1.5-.5-2.5-1-3.5S17 8.5 17 7a5 5 0 0 0-5-5z"/><path d="M9 9h6M9 12h6M10 15h4"/></svg>',
        'alert': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M12 2L2 22h20L12 2z"/><path d="M12 10v4M12 18h.01"/></svg>',
        'grid': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
        'layers': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
        'shield': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M12 2l8 4v6c0 5.5-3.8 10.7-8 12-4.2-1.3-8-6.5-8-12V6l8-4z"/></svg>',
        'check': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M20 6L9 17l-5-5"/></svg>',
        'rocket': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>',
        'key': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.78 7.78 5.5 5.5 0 0 1 7.78-7.78zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>',
        'dollar': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M9 9.5a2.5 2.5 0 0 1 3.5-2c1.5.7 1.7 2.5.5 3.5-1 .8-3.5 1.5-3.5 3 0 1.5 1.5 2.5 3.5 2"/></svg>',
        'tool': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
        'clock': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
        'eye': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
        'lock': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        'user': f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    }
    return icons.get(name, icons['grid'])

with open(SPEC_PATH) as f:
    spec = json.load(f)

notes = parse_speaker_notes(NOTES_PATH)
slides = spec['slides']

# -- Build sections --
sections = []
for idx, slide in enumerate(slides):
    slide_num = idx + 1
    stype = slide.get('type', 'content')
    title = slide.get('title', '')
    section_label = slide.get('sectionLabel', '')
    note_text = notes.get(slide_num, '')
    note_html = f'<aside class="notes">{h(note_text)}</aside>' if note_text else ''

    label_html = f'<div class="section-label">{h(section_label)}</div>' if section_label else ''

    if stype == 'title':
        s = f'''<section data-background="#0a0c12">
  <div class="title-slide">
    <div class="rh-logo-mark"></div>
    <h1>{h(title)}</h1>
    <p class="subtitle">{h(slide.get("subtitle", ""))}</p>
    <p class="presenter">{h(spec.get("presenter", ""))}</p>
  </div>
  {note_html}
</section>'''

    elif stype == 'icon-row':
        items_html = ''
        for item in slide.get('items', []):
            icon = icon_svg(item.get('icon', 'grid'), '#EE0000', 36)
            items_html += f'''<div class="agenda-card fragment fade-up">
  {icon}
  <h4>{h(item["label"])}</h4>
  <p>{h(item["desc"])}</p>
</div>\n'''
        cols = len(slide.get('items', []))
        grid_class = 'agenda-grid' if cols <= 7 else 'agenda-grid-wide'
        s = f'''<section>
  {label_html}
  <h2>{h(title)}</h2>
  <div class="{grid_class}">{items_html}</div>
  {note_html}
</section>'''

    elif stype == 'content':
        bullets = ''
        for pt in slide.get('points', []):
            bullets += f'  <li class="fragment">{h(pt)}</li>\n'
        s = f'''<section>
  {label_html}
  <h2>{h(title)}</h2>
  <div class="glass-card">
    <ul class="content-list">{bullets}</ul>
  </div>
  {note_html}
</section>'''

    elif stype == 'diagram':
        dfn = slide.get('diagramFn', '')
        did = slide.get('diagramId', '')
        s = f'''<section data-diagram-fn="{dfn}">
  {label_html}
  <h2>{h(title)}</h2>
  <div class="glass-card diagram-card">
    <div id="{did}" class="diagram-container"></div>
  </div>
  {note_html}
</section>'''

    elif stype == 'image':
        img_path = slide.get('image', '')
        b64 = load_b64(img_path)
        caption = slide.get('caption', '')
        full_bleed = slide.get('imageFullBleed', False)
        img_class = 'image-full-bleed' if full_bleed else 'image-standard'
        caption_html = f'<p class="image-caption">{h(caption)}</p>' if caption else ''
        if b64:
            img_tag = f'<img src="data:image/png;base64,{b64}" alt="{h(title)}" class="slide-image">'
        else:
            img_tag = f'<p class="image-missing">[Image: {h(os.path.basename(img_path))}]</p>'
        s = f'''<section>
  {label_html}
  <h2>{h(title)}</h2>
  <div class="glass-card {img_class}">
    {img_tag}
    {caption_html}
  </div>
  {note_html}
</section>'''

    elif stype == 'two-column':
        left = slide.get('left', {})
        right = slide.get('right', {})
        left_bullets = ''.join(f'    <li class="fragment">{h(p)}</li>\n' for p in left.get('points', []))
        right_bullets = ''.join(f'    <li class="fragment">{h(p)}</li>\n' for p in right.get('points', []))
        s = f'''<section>
  {label_html}
  <h2>{h(title)}</h2>
  <div class="two-col">
    <div class="glass-card col-card">
      <h3>{h(left.get("heading", ""))}</h3>
      <ul class="content-list">{left_bullets}</ul>
    </div>
    <div class="glass-card col-card">
      <h3>{h(right.get("heading", ""))}</h3>
      <ul class="content-list">{right_bullets}</ul>
    </div>
  </div>
  {note_html}
</section>'''

    elif stype == 'table':
        cols = slide.get('columns', [])
        rows = slide.get('rows', [])
        thead = ''.join(f'<th>{h(c)}</th>' for c in cols)
        tbody = ''
        for row in rows:
            cells = ''.join(f'<td>{h(c)}</td>' for c in row)
            tbody += f'  <tr class="fragment">{cells}</tr>\n'
        s = f'''<section>
  {label_html}
  <h2>{h(title)}</h2>
  <div class="glass-card table-card">
    <table>
      <thead><tr>{thead}</tr></thead>
      <tbody>{tbody}</tbody>
    </table>
  </div>
  {note_html}
</section>'''

    elif stype == 'quote':
        quote_text = slide.get('quote', '')
        attribution = slide.get('attribution', '')
        s = f'''<section data-background="linear-gradient(135deg, #1a0000 0%, #330000 50%, #0d0f14 100%)">
  <div class="quote-slide">
    <blockquote>&ldquo;{h(quote_text)}&rdquo;</blockquote>
    <p class="attribution">&mdash; {h(attribution)}</p>
  </div>
  {note_html}
</section>'''

    elif stype == 'closing':
        bullets_html = ''.join(f'<li class="fragment">{h(b)}</li>\n' for b in slide.get('bullets', []))
        s = f'''<section data-background="#0a0c12">
  <div class="closing-slide">
    <h2>{h(title)}</h2>
    <ul class="closing-list">{bullets_html}</ul>
    <div class="rh-logo-mark closing-logo"></div>
  </div>
  {note_html}
</section>'''

    else:
        s = f'''<section>
  <h2>{h(title)}</h2>
  <p>Slide type: {h(stype)}</p>
  {note_html}
</section>'''

    sections.append(s)

# -- D3 diagram JS (from server.js, with fixed COLORS) --
D3_JS = r'''
var COLORS={red:'#EE0000',cyan:'#00BCD4',pink:'#E91E63',teal:'#009596',blue:'#0066CC',blueLight:'#4394e5',green:'#4CAF50',purple:'#9C27B0',orange:'#FFB300',amber:'#FFB300',bg:'#0d0f14',bgLight:'#161a24',surface:'rgba(255,255,255,0.06)',raised:'rgba(255,255,255,0.1)',border:'rgba(255,255,255,0.15)',text:'#ffffff',textDim:'rgba(255,255,255,0.7)',textMuted:'rgba(255,255,255,0.4)',textSecondary:'rgba(255,255,255,0.7)'};

function createSvg(container,w,h){var el=document.querySelector(container);if(!el)return null;el.querySelectorAll('svg').forEach(function(s){s.remove()});var svg=d3.select(container).append('svg').attr('viewBox','0 0 '+w+' '+h).attr('width','100%').attr('height','100%').attr('preserveAspectRatio','xMidYMid meet');
var defs=svg.append('defs');
['cyan','pink','amber','red','green','purple','teal','blue'].forEach(function(c){var col=COLORS[c];defs.append('filter').attr('id','glow-'+c).append('feDropShadow').attr('dx',0).attr('dy',0).attr('stdDeviation',6).attr('flood-color',col).attr('flood-opacity',0.35)});
defs.append('linearGradient').attr('id','grad-surface').attr('x1',0).attr('y1',0).attr('x2',0).attr('y2',1).html('<stop offset="0%" stop-color="rgba(255,255,255,0.08)"/><stop offset="100%" stop-color="rgba(255,255,255,0.02)"/>');
return svg}

function drawBox(svg,x,y,w,h,label,color,opts){opts=opts||{};var g=svg.append('g').style('opacity',0);g.transition().delay(opts.delay||0).duration(450).ease(d3.easeCubicOut).style('opacity',1);g.append('rect').attr('x',x).attr('y',y).attr('width',w).attr('height',h).attr('rx',opts.rx||8).attr('fill',opts.fill||'none').attr('stroke',color).attr('stroke-width',opts.strokeWidth||1).attr('opacity',opts.opacity||1);if(label){var lines=label.split('\\n');var textY=y+h/2-(lines.length-1)*(opts.fontSize||12)*0.6;lines.forEach(function(line,i){g.append('text').attr('x',x+w/2).attr('y',textY+i*((opts.fontSize||12)*1.3)).attr('text-anchor','middle').attr('dominant-baseline','middle').attr('fill',opts.textColor||COLORS.text).attr('font-family',"'Red Hat Display',sans-serif").attr('font-size',opts.fontSize||12).attr('font-weight',opts.bold?700:400).text(line)})}return g}

function drawArrow(svg,x1,y1,x2,y2,color,opts){opts=opts||{};var id='ah-'+Math.random().toString(36).substr(2,6);svg.append('defs').append('marker').attr('id',id).attr('viewBox','0 0 10 8').attr('refX',9).attr('refY',4).attr('markerWidth',8).attr('markerHeight',6).attr('orient','auto').append('path').attr('d','M0,0 L10,4 L0,8 Z').attr('fill',color);var line=svg.append('line').attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color).attr('stroke-width',opts.width||1.5).attr('marker-end','url(#'+id+')').style('opacity',0);line.transition().delay(opts.delay||400).duration(400).style('opacity',opts.dashed?0.6:0.8);if(opts.dashed)line.attr('stroke-dasharray','6,4');return line}

function drawLabel(svg,x,y,text,opts){opts=opts||{};var lines=String(text).split('\\n');var fs=opts.fontSize||11;var lh=fs*1.3;if(lines.length===1){var el=svg.append('text').attr('x',x).attr('y',y).attr('text-anchor',opts.anchor||'middle').attr('dominant-baseline',opts.baseline||'middle').attr('fill',opts.color||COLORS.textMuted).attr('font-family',"'Red Hat Display',sans-serif").attr('font-size',fs).attr('font-weight',opts.bold?700:400).text(text).style('opacity',0);el.transition().delay(opts.delay||600).duration(400).style('opacity',1);if(opts.transform)el.attr('transform',opts.transform);return el}var g=svg.append('g').style('opacity',0);g.transition().delay(opts.delay||600).duration(400).style('opacity',1);if(opts.transform)g.attr('transform',opts.transform);lines.forEach(function(line,i){g.append('text').attr('x',x).attr('y',y+i*lh).attr('text-anchor',opts.anchor||'middle').attr('dominant-baseline',opts.baseline||'middle').attr('fill',opts.color||COLORS.textMuted).attr('font-family',"'Red Hat Display',sans-serif").attr('font-size',fs).attr('font-weight',opts.bold?700:400).text(line)});return g}

function renderThreeComponents(){var svg=createSvg('#d-three-components',900,340);if(!svg)return;
var cW=240,cH=260,gap=45,startX=(900-3*cW-2*gap)/2;
var components=[
{name:'Model',color:COLORS.cyan,icon:'M 0,-18 L 14,10 L -14,10 Z',items:['Stateless inference','OpenAI-compatible API','Any: Llama, Nemotron,\nDeepSeek, Qwen, Mistral'],lifecycle:'Version & swap independently'},
{name:'Harness',color:COLORS.pink,icon:'M -14,-14 L 14,-14 L 14,14 L -14,14 Z',items:['Owns the loop','Memory & context window','Tool-call orchestration'],lifecycle:'OpenClaw \u00b7 LangGraph \u00b7 Custom'},
{name:'Sandbox',color:COLORS.amber,icon:'M 0,-16 A 16,16 0 1,1 -0.01,-16 Z',items:['Files, binaries, endpoints','Kernel-level isolation','Egress & syscall policy'],lifecycle:'OpenShell \u00b7 Kata \u00b7 agent-sandbox'}
];
components.forEach(function(c,i){
var x=startX+i*(cW+gap),y=30;
var g=svg.append('g').attr('transform','translate('+x+','+y+')').style('opacity',0);
g.transition().delay(200+i*250).duration(500).ease(d3.easeCubicOut).style('opacity',1);
g.append('rect').attr('width',cW).attr('height',cH).attr('rx',12).attr('fill','url(#grad-surface)').attr('stroke',c.color).attr('stroke-width',1.5);
g.append('rect').attr('width',cW).attr('height',3).attr('rx',1.5).attr('fill',c.color);
g.append('path').attr('d',c.icon).attr('transform','translate('+(cW/2)+',40)').attr('fill',c.color).attr('filter','url(#glow-'+(c.color===COLORS.cyan?'cyan':c.color===COLORS.pink?'pink':'amber')+')');
drawLabel(g,cW/2,70,c.name,{bold:true,fontSize:15,color:c.color,delay:0});
c.items.forEach(function(t,j){drawLabel(g,cW/2,105+j*30,t,{fontSize:10,color:COLORS.textDim,delay:0});});
g.append('rect').attr('x',14).attr('y',cH-42).attr('width',cW-28).attr('height',28).attr('rx',14).attr('fill',c.color).attr('fill-opacity',0.15);
drawLabel(g,cW/2,cH-24,c.lifecycle,{fontSize:9,color:c.color,delay:0,bold:true});
});
if(components.length>1){for(var i=0;i<components.length-1;i++){
var x1=startX+(i+1)*(cW+gap)-gap+5,x2=startX+(i+1)*(cW+gap)-5,cy=30+cH/2;
drawArrow(svg,x1,cy,x2,cy,COLORS.textMuted,{delay:900+i*200,dashed:true});
}}
drawLabel(svg,450,cH+55,'Separate lifecycles \u2192 separate scaling \u2192 separate security',{bold:true,fontSize:11,color:COLORS.text,delay:1200});
}

function renderAgentAssumptions(){var svg=createSvg('#d-agent-assumptions',900,310);if(!svg)return;
drawLabel(svg,450,12,'YOUR INFRASTRUCTURE ASSUMES\u2026',{bold:true,fontSize:11,color:COLORS.textMuted,delay:0});
drawLabel(svg,450,28,'AGENTS VIOLATE ALL FIVE',{bold:true,fontSize:11,color:COLORS.red,delay:200});
var items=[
{assumption:'Requests are short-lived',micro:'Milliseconds to seconds, stateless',agent:'Minutes to days, stateful across steps',color:COLORS.orange},
{assumption:'Workload does what you coded',micro:'Deterministic code paths, auditable at build',agent:'Model decides next step, auditable only at runtime',color:COLORS.purple},
{assumption:'Network policy = security boundary',micro:'Known callers/callees, service mesh',agent:'Agent chooses its own tools and destinations',color:COLORS.blue},
{assumption:'Credentials are static secrets',micro:'Vault-injected, rotated quarterly',agent:'Workspace attackable via prompt injection',color:COLORS.red},
{assumption:'One model, one endpoint',micro:'Fixed dependency graph, one SLA',agent:'3 routing decisions per inference call',color:COLORS.teal}
];
var rowH=50,startY=42,colX=[30,330,620];
drawBox(svg,colX[0],startY,280,28,'Assumption',COLORS.textMuted,{fill:COLORS.textMuted+'08',delay:50,fontSize:11,bold:true});
drawBox(svg,colX[1],startY,270,28,'Microservice',COLORS.textMuted,{fill:COLORS.textMuted+'08',delay:80,fontSize:11,bold:true});
drawBox(svg,colX[2],startY,270,28,'Agent',COLORS.red,{fill:COLORS.red+'08',delay:110,fontSize:11,bold:true});
items.forEach(function(it,i){var y=startY+32+i*rowH;
drawBox(svg,colX[0],y,280,44,it.assumption,it.color,{fill:it.color+'10',delay:150+i*80,fontSize:11,bold:true});
drawBox(svg,colX[1],y,270,44,it.micro,COLORS.textMuted,{fill:'transparent',delay:180+i*80,fontSize:10});
drawBox(svg,colX[2],y,270,44,it.agent,COLORS.red,{fill:COLORS.red+'06',delay:210+i*80,fontSize:10,bold:true})
})}

function renderFiveDecisions(){var svg=createSvg('#d-five-decisions',900,320);if(!svg)return;
var decisions=[
{num:'1',title:'Isolate the Agent',sub:'Sandbox \u00b7 supervisor \u00b7 defense rings',color:COLORS.red,techs:['OpenShell','Kata','seccomp','Landlock']},
{num:'2',title:'Govern Tool Access',sub:'MCP Gateway \u00b7 claims-based auth',color:COLORS.teal,techs:['MCP Gateway','Envoy','Kuadrant','Authorino']},
{num:'3',title:'Route Inference',sub:'Three tiers \u00b7 security \u00b7 cost \u00b7 efficiency',color:COLORS.purple,techs:['Egress Router','Semantic Router','llm-d EPP','AI Gateway']},
{num:'4',title:'Prove Identity',sub:'SPIFFE \u00b7 JWT-SVID \u00b7 zero static keys',color:COLORS.cyan,techs:['SPIFFE','SPIRE','JWT-SVID','Keycloak']},
{num:'5',title:'Place the Loop',sub:'Workload vs Service \u00b7 OGX',color:COLORS.amber,techs:['OGX','OpenClaw','LangGraph','Responses API']}
];
var cardW=166,cardH=264,gap=10,startX=18;
decisions.forEach(function(d,i){var cx=startX+i*(cardW+gap),cy=12;
var g=svg.append('g').style('opacity',0).attr('transform','translate(0,20)');
g.transition().delay(i*120).duration(500).ease(d3.easeCubicOut).style('opacity',1).attr('transform','translate(0,0)');
g.append('rect').attr('x',cx).attr('y',cy).attr('width',cardW).attr('height',cardH).attr('rx',10).attr('fill','url(#grad-surface)').attr('stroke',d.color).attr('stroke-width',1);
g.append('rect').attr('x',cx).attr('y',cy).attr('width',3).attr('height',cardH).attr('rx',1.5).attr('fill',d.color);
g.append('circle').attr('cx',cx+cardW/2).attr('cy',cy+32).attr('r',18).attr('fill',d.color+'20').attr('stroke',d.color).attr('stroke-width',1.5).attr('filter','url(#glow-'+(d.color===COLORS.red?'red':d.color===COLORS.teal?'teal':d.color===COLORS.purple?'purple':d.color===COLORS.cyan?'cyan':'amber')+')');
drawLabel(g,cx+cardW/2,cy+36,d.num,{bold:true,fontSize:16,color:d.color,delay:0});
drawLabel(g,cx+cardW/2,cy+66,d.title,{bold:true,fontSize:10,color:COLORS.text,delay:0});
drawLabel(g,cx+cardW/2,cy+88,d.sub,{fontSize:8,color:COLORS.textMuted,delay:0});
d.techs.forEach(function(t,ti){
var pillG=g.append('g').style('opacity',0);
pillG.transition().delay(i*120+250+ti*50).duration(350).style('opacity',1);
pillG.append('rect').attr('x',cx+8).attr('y',cy+110+ti*30).attr('width',cardW-16).attr('height',24).attr('rx',12).attr('fill',d.color+'12').attr('stroke',d.color).attr('stroke-width',0.5);
pillG.append('text').attr('x',cx+cardW/2).attr('y',cy+124+ti*30).attr('text-anchor','middle').attr('dominant-baseline','middle').attr('fill',COLORS.text).attr('font-family',"'Red Hat Display',sans-serif").attr('font-size',9).text(t)
})});
drawLabel(svg,450,300,'Open interfaces: OpenAI-compatible \u00b7 MCP \u00b7 agent-sandbox API \u00b7 SPIFFE',{fontSize:10,color:COLORS.textMuted,delay:800})}

function renderAgentPodAnatomy(){var svg=createSvg('#d-agent-pod',900,310);if(!svg)return;
var podX=180,podY=10,podW=540,podH=200;
drawBox(svg,podX,podY,podW,podH,'',COLORS.blue,{fill:'url(#grad-surface)',delay:0,rx:10,strokeWidth:1.5});
drawLabel(svg,podX+podW/2,podY+16,'AGENT POD',{bold:true,fontSize:12,color:COLORS.blue,delay:50});
var supX=podX+20,supY=podY+30,supW=podW-40,supH=70;
drawBox(svg,supX,supY,supW,supH,'',COLORS.teal,{fill:COLORS.teal+'08',delay:100,rx:8});
drawLabel(svg,supX+supW/2,supY+14,'Supervisor (PID 1)',{bold:true,fontSize:11,color:COLORS.teal,delay:150});
var supItems=['seccomp','Landlock','Network NS','Binary allowlist','Egress proxy'];
supItems.forEach(function(s,i){var bx=supX+10+i*(supW/5);drawBox(svg,bx,supY+28,supW/5-8,34,s,COLORS.teal,{fill:COLORS.teal+'12',delay:200+i*40,fontSize:9,rx:6})});
var agentX=podX+60,agentY=supY+supH+12,agentW=200,agentH=70;
drawBox(svg,agentX,agentY,agentW,agentH,'',COLORS.purple,{fill:COLORS.purple+'08',delay:350,rx:8});
drawLabel(svg,agentX+agentW/2,agentY+16,'Agent Harness',{bold:true,fontSize:11,color:COLORS.purple,delay:400});
drawLabel(svg,agentX+agentW/2,agentY+36,'Loop \u00b7 Memory \u00b7 Context',{fontSize:9,color:COLORS.textMuted,delay:430});
drawLabel(svg,agentX+agentW/2,agentY+52,'OpenClaw / LangGraph',{fontSize:9,color:COLORS.purple,delay:460});
var authX=podX+300,authY=agentY,authW=200,authH=70;
drawBox(svg,authX,authY,authW,authH,'',COLORS.red,{fill:COLORS.red+'08',delay:350,rx:8});
drawLabel(svg,authX+authW/2,authY+16,'Auth Sidecar',{bold:true,fontSize:11,color:COLORS.red,delay:400});
drawLabel(svg,authX+authW/2,authY+36,'SPIFFE SVID \u2192 Token',{fontSize:9,color:COLORS.textMuted,delay:430});
drawLabel(svg,authX+authW/2,authY+52,'5-min short-lived claims',{fontSize:9,color:COLORS.red,delay:460});
var ringY=podY+podH+20;
var rings=[{label:'Ring 1: Process',detail:'seccomp, Landlock, binary allowlist',color:COLORS.teal},{label:'Ring 2: Pod',detail:'Pod Security, SELinux, NetworkPolicy',color:COLORS.blue},{label:'Ring 3: Hardware/VM',detail:'Kata Containers, Confidential Containers',color:COLORS.purple}];
rings.forEach(function(r,i){var rx=podX+i*180;
drawBox(svg,rx,ringY,170,60,r.label,r.color,{fill:r.color+'08',delay:500+i*80,fontSize:11,bold:true,rx:8});
drawLabel(svg,rx+85,ringY+40,r.detail,{fontSize:8,color:COLORS.textMuted,delay:550+i*80});
if(i<rings.length-1)drawArrow(svg,rx+170,ringY+30,rx+180,ringY+30,COLORS.textMuted,{delay:600+i*80})});
drawLabel(svg,podX+podW/2,ringY+72,'Each ring assumes the ring inside it has already failed',{fontSize:10,bold:true,color:COLORS.text,delay:800})}

function renderMcpGateway(){var svg=createSvg('#d-mcp-gateway',900,310);if(!svg)return;
var agentX=30,agentY=80,agentW=130;
drawBox(svg,agentX,agentY,agentW,50,'Agent Pod',COLORS.blue,{fill:COLORS.blue+'08',delay:0,bold:true,fontSize:12,rx:8});
drawLabel(svg,agentX+agentW/2,agentY+38,'Bearer token attached',{fontSize:8,color:COLORS.textMuted,delay:50});
drawArrow(svg,agentX+agentW,agentY+25,230,agentY+25,COLORS.teal,{delay:100});
var gwX=230,gwY=40,gwW=200,gwH=120;
drawBox(svg,gwX,gwY,gwW,gwH,'',COLORS.teal,{fill:'url(#grad-surface)',delay:150,rx:10,strokeWidth:1.5});
drawLabel(svg,gwX+gwW/2,gwY+18,'MCP Gateway',{bold:true,fontSize:13,color:COLORS.teal,delay:200});
drawLabel(svg,gwX+gwW/2,gwY+36,'Envoy + Kuadrant/Authorino',{fontSize:9,color:COLORS.textMuted,delay:230});
drawBox(svg,gwX+20,gwY+50,gwW-40,26,'Validate token claims',COLORS.teal,{fill:COLORS.teal+'12',delay:280,fontSize:10,rx:6});
drawBox(svg,gwX+20,gwY+82,gwW-40,26,'Check tool \u2208 allowed set',COLORS.teal,{fill:COLORS.teal+'12',delay:320,fontSize:10,rx:6});
var toolX=510,toolGap=48;
var tools=[{label:'CUDA-X Service',color:COLORS.purple},{label:'OR-Tools API',color:COLORS.blue},{label:'RAG Service',color:COLORS.orange},{label:'SaaS Endpoint',color:COLORS.red}];
tools.forEach(function(t,i){var ty=20+i*toolGap;
drawArrow(svg,gwX+gwW,gwY+gwH/2,toolX,ty+18,COLORS.textMuted,{delay:400+i*40});
drawBox(svg,toolX,ty,160,36,t.label,t.color,{fill:t.color+'08',delay:400+i*60,fontSize:11,rx:8})});
var flowY=200;
drawLabel(svg,450,flowY,'PROMPT INJECTION DEFENSE',{bold:true,fontSize:11,color:COLORS.red,delay:600});
var steps=[{label:'1. Injected prompt forces\nunauthorized tool call',color:COLORS.red},{label:'2. Gateway checks token\nclaims, not prompt',color:COLORS.teal},{label:'3. Tool not in allowed set\n\u2192 Request DENIED',color:COLORS.green}];
steps.forEach(function(s,i){var sx=80+i*270;
drawBox(svg,sx,flowY+14,240,60,s.label,s.color,{fill:s.color+'06',delay:650+i*100,fontSize:10,rx:8})});
drawLabel(svg,450,flowY+88,'Authorization is not the model\u2019s decision to make',{fontSize:10,bold:true,color:COLORS.text,delay:950})}

function renderSpiffeFlow(){var svg=createSvg('#d-spiffe-flow',900,310);if(!svg)return;
drawLabel(svg,450,12,'ZERO STATIC KEYS \u2014 SPIFFE IDENTITY FLOW',{bold:true,fontSize:12,color:COLORS.red,delay:0});
var steps=[
{num:'1',title:'SPIFFE SVID Issued',detail:'SPIRE issues JWT-SVID to agent pod\nspiffe://cluster/ns/agents/sa/field-optimizer\nAuto-rotated, short-lived',color:COLORS.red},
{num:'2',title:'Auth Sidecar Exchanges',detail:'Sidecar presents SVID to Keycloak\nRFC 8693 (token exchange)\nReturns scoped access token',color:COLORS.cyan},
{num:'3',title:'Token Carries Claims',detail:'sub: field-optimizer\ntools: [cuopt, rag]\nmodels: [tier2], exp: 300s',color:COLORS.teal},
{num:'4',title:'Every Call Authorized',detail:'MCP Gateway validates claims\nAI Gateway validates claims\nNo static key anywhere',color:COLORS.green}
];
var stepW=200,stepH=160,gap=12,startX=22,startY=30;
steps.forEach(function(s,i){var cx=startX+i*(stepW+gap);
drawBox(svg,cx,startY,stepW,stepH,'',s.color,{fill:'url(#grad-surface)',delay:i*120,rx:10});
svg.append('circle').attr('cx',cx+stepW/2).attr('cy',startY+24).attr('r',14).attr('fill',s.color+'20').attr('stroke',s.color).attr('stroke-width',1.5).attr('filter','url(#glow-'+(s.color===COLORS.red?'red':s.color===COLORS.cyan?'cyan':s.color===COLORS.teal?'teal':'green')+')').style('opacity',0).transition().delay(i*120+50).duration(400).style('opacity',1);
drawLabel(svg,cx+stepW/2,startY+28,s.num,{bold:true,fontSize:13,color:s.color,delay:i*120+80});
drawLabel(svg,cx+stepW/2,startY+50,s.title,{bold:true,fontSize:11,color:COLORS.text,delay:i*120+100});
drawLabel(svg,cx+stepW/2,startY+82,s.detail,{fontSize:9,color:COLORS.textMuted,delay:i*120+150});
if(i<steps.length-1)drawArrow(svg,cx+stepW,startY+stepH/2,cx+stepW+gap,startY+stepH/2,COLORS.textMuted,{delay:i*120+200})
});
var compY=startY+stepH+16;
drawBox(svg,40,compY,380,50,'BEFORE: Static API keys, rotated quarterly,\none key = full access, leaked prompt = game over',COLORS.red,{fill:COLORS.red+'06',delay:600,fontSize:10,rx:8});
drawBox(svg,440,compY,400,50,'AFTER: Per-agent crypto identity, auto-rotated,\nper-tool entitlements, leaked workspace = nothing durable',COLORS.green,{fill:COLORS.green+'06',delay:700,fontSize:10,rx:8});
drawLabel(svg,450,compY+64,'Containment economics: revoke one identity = one targeted operation',{fontSize:10,bold:true,color:COLORS.text,delay:850})}

function renderAgentBenchmark(){var svg=createSvg('#d-agent-benchmark',900,310);if(!svg)return;
drawLabel(svg,450,10,'SAME IMAGE \u00b7 SAME AGENT \u00b7 SAME MODEL \u00b7 THREE PROTECTION LAYERS',{bold:true,fontSize:11,color:COLORS.text,delay:0});
var pods=[{label:'Pod 1: Kata Only',tech:'Kata micro-VM, no OpenShell',color:COLORS.purple},{label:'Pod 2: OpenShell Only',tech:'OpenShell + egress proxy, runc',color:COLORS.teal},{label:'Pod 3: Both (Dual)',tech:'OpenShell inside Kata micro-VM',color:COLORS.green}];
var podW=270,podH=44,startY=26;
pods.forEach(function(p,i){var px=30+i*(podW+14);
drawBox(svg,px,startY,podW,podH,p.label,p.color,{fill:p.color+'08',delay:50+i*80,fontSize:12,bold:true,rx:8});
drawLabel(svg,px+podW/2,startY+podH-8,p.tech,{fontSize:9,color:COLORS.textMuted,delay:100+i*80})});
var atkY=86;
drawLabel(svg,450,atkY,'ATTACK 1: Prompt Injection Exfiltration',{bold:true,fontSize:11,color:COLORS.red,delay:300});
var atk1=[{result:'DATA LEAKED',color:COLORS.red,detail:'curl succeeded, env dumped'},{result:'BLOCKED',color:COLORS.green,detail:'Egress proxy denied'},{result:'BLOCKED',color:COLORS.green,detail:'Egress proxy denied'}];
atk1.forEach(function(a,i){var ax=30+i*(podW+14),ay=atkY+14;
drawBox(svg,ax,ay,podW,50,'',a.color,{fill:a.color+'06',delay:350+i*60,rx:8});
drawLabel(svg,ax+podW/2,ay+20,a.result,{bold:true,fontSize:14,color:a.color,delay:400+i*60});
drawLabel(svg,ax+podW/2,ay+38,a.detail,{fontSize:9,color:COLORS.textMuted,delay:430+i*60})});
var atk2Y=atkY+76;
drawLabel(svg,450,atk2Y,'ATTACK 2: CVE-2026-31431 Container Escape',{bold:true,fontSize:11,color:COLORS.red,delay:550});
var atk2=[{result:'CONTAINED',color:COLORS.green,detail:'virtiofs blocks page cache'},{result:'HOST COMPROMISED',color:COLORS.red,detail:'Page-cache corruption escaped'},{result:'CONTAINED',color:COLORS.green,detail:'VM boundary prevented exploit'}];
atk2.forEach(function(a,i){var ax=30+i*(podW+14),ay=atk2Y+14;
drawBox(svg,ax,ay,podW,50,'',a.color,{fill:a.color+'06',delay:600+i*60,rx:8});
drawLabel(svg,ax+podW/2,ay+20,a.result,{bold:true,fontSize:14,color:a.color,delay:650+i*60});
drawLabel(svg,ax+podW/2,ay+38,a.detail,{fontSize:9,color:COLORS.textMuted,delay:680+i*60})});
var matY=atk2Y+76;
drawLabel(svg,450,matY,'RESULTS MATRIX',{bold:true,fontSize:11,color:COLORS.text,delay:800});
var headers=['','Kata Only','OpenShell Only','Both'];
headers.forEach(function(h,i){var hx=i===0?30:30+i*220;
drawBox(svg,hx,matY+12,i===0?210:podW,24,h,COLORS.textMuted,{fill:COLORS.textMuted+'08',delay:820+i*30,fontSize:10,bold:true,rx:4})});
var attacks=['Prompt Injection','Container Escape'];
var results=[['red','green','green'],['green','red','green']];
var texts=[['LEAKED','BLOCKED','BLOCKED'],['BLOCKED','COMPROMISED','BLOCKED']];
attacks.forEach(function(atk,ri){var ry=matY+40+ri*28;
drawBox(svg,30,ry,210,24,atk,COLORS.text,{fill:'transparent',delay:850+ri*40,fontSize:10,bold:true,rx:4});
results[ri].forEach(function(c,ci){var cx=240+ci*220,col=c==='red'?COLORS.red:COLORS.green;
drawBox(svg,cx,ry,podW,24,texts[ri][ci],col,{fill:col+'12',delay:870+ri*40+ci*30,fontSize:10,bold:true,rx:4})})});
drawLabel(svg,450,matY+100,'Each technology addresses a different threat class \u2014 dual protection stops both',{fontSize:10,bold:true,color:COLORS.text,delay:1000})}

var renderedDiagrams={};
Reveal.on('slidechanged',function(event){
  var fn=event.currentSlide.dataset.diagramFn;
  if(!fn||renderedDiagrams[fn])return;
  renderedDiagrams[fn]=true;
  var renderFn=window[fn];
  if(renderFn)setTimeout(renderFn,100);
});
Reveal.on('ready',function(event){
  var fn=event.currentSlide.dataset.diagramFn;
  if(fn&&!renderedDiagrams[fn]){renderedDiagrams[fn]=true;var renderFn=window[fn];if(renderFn)setTimeout(renderFn,100);}
});
'''

# -- Assemble full HTML --
sections_html = '\n\n'.join(sections)

full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Running AI Agents Safely at Scale</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/reveal.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/theme/black.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
:root {{
  --rh-red: #EE0000;
  --rh-red-dark: #A30000;
  --bg-dark: #0d0f14;
  --surface: rgba(255,255,255,0.06);
  --border: rgba(255,255,255,0.1);
  --text: #ffffff;
  --text-dim: rgba(255,255,255,0.7);
  --text-muted: rgba(255,255,255,0.4);
}}
.reveal-viewport {{
  background: var(--bg-dark);
  background-image: radial-gradient(rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 30px 30px;
}}
.reveal {{
  font-family: 'Red Hat Display', Arial, sans-serif;
  font-size: 22px;
  color: var(--text);
}}
.reveal .slides section {{
  text-align: left;
  padding: 30px 50px;
  height: 100%;
  display: flex;
  flex-direction: column;
}}
.reveal h1 {{
  font-size: 2.2em;
  font-weight: 900;
  line-height: 1.15;
  margin-bottom: 0.3em;
}}
.reveal h2 {{
  font-size: 1.15em;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 0.5em;
  color: var(--text);
  text-transform: none;
  letter-spacing: 0;
}}
.reveal h3 {{
  font-size: 0.95em;
  font-weight: 700;
  color: var(--rh-red);
  margin-bottom: 0.4em;
  text-transform: none;
  letter-spacing: 0;
}}
.reveal h2::after {{
  content: '';
  display: block;
  width: 48px;
  height: 3px;
  background: var(--rh-red);
  margin-top: 8px;
  border-radius: 2px;
}}
.section-label {{
  font-size: 0.55em;
  font-weight: 700;
  color: var(--rh-red);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 4px;
  padding: 3px 10px;
  background: rgba(238,0,0,0.08);
  border: 1px solid rgba(238,0,0,0.2);
  border-radius: 3px;
  display: inline-block;
}}
.glass-card {{
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.4em 1.6em;
  flex: 1;
  overflow: auto;
}}
.glass-card.diagram-card {{
  padding: 0.6em;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.diagram-container {{
  width: 100%;
  max-height: 100%;
}}
.diagram-container svg {{
  max-width: 100%;
  max-height: 420px;
}}
.content-list {{
  list-style: none;
  padding: 0;
  margin: 0;
}}
.content-list li {{
  padding: 0.35em 0 0.35em 1.2em;
  position: relative;
  font-size: 0.82em;
  line-height: 1.5;
  color: var(--text-dim);
}}
.content-list li::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 0.7em;
  width: 6px;
  height: 6px;
  background: var(--rh-red);
  border-radius: 50%;
}}
.two-col {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  flex: 1;
}}
.col-card {{
  display: flex;
  flex-direction: column;
}}
.table-card {{
  overflow: auto;
}}
.table-card table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75em;
}}
.table-card th {{
  background: rgba(238,0,0,0.1);
  color: var(--rh-red);
  padding: 8px 12px;
  text-align: left;
  font-weight: 700;
  border-bottom: 2px solid rgba(238,0,0,0.3);
}}
.table-card td {{
  padding: 7px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-dim);
}}
.table-card tr:nth-child(even) td {{
  background: rgba(255,255,255,0.02);
}}
.title-slide {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
}}
.title-slide h1 {{
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.title-slide .subtitle {{
  font-size: 1em;
  color: var(--text-dim);
  margin-top: 0.5em;
}}
.title-slide .presenter {{
  font-size: 0.75em;
  color: var(--text-muted);
  margin-top: 1.5em;
}}
.rh-logo-mark {{
  width: 50px;
  height: 50px;
  margin-bottom: 1.5em;
  background: var(--rh-red);
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 613 145'%3E%3Cpath d='M127.47 83.49c12.51 0 30.61-2.58 30.61-17.46a14 14 0 00-.31-3.42l-7.45-32.36c-1.72-7.12-3.23-10.35-15.73-16.6C124.89 8.69 103.76.5 97.51.5 91.69.5 90 8 83.06 8c-6.68 0-11.64-5.6-17.89-5.6-6 0-9.91 4.09-12.93 12.5 0 0-8.41 23.72-9.49 27.16A6.43 6.43 0 0042.53 44c0 9.22 36.3 39.45 84.94 39.45M160 72.07c1.73 8.19 1.73 9.05 1.73 10.13 0 14-15.74 21.77-36.43 21.77C78.54 104 37.58 76.6 37.58 58.49a18.45 18.45 0 011.51-7.33C22.27 52 .5 55 .5 74.22c0 31.48 74.59 70.28 133.65 70.28 45.28 0 56.7-20.48 56.7-36.65 0-12.72-11-27.16-30.83-35.78'/%3E%3C/svg%3E") no-repeat center;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 613 145'%3E%3Cpath d='M127.47 83.49c12.51 0 30.61-2.58 30.61-17.46a14 14 0 00-.31-3.42l-7.45-32.36c-1.72-7.12-3.23-10.35-15.73-16.6C124.89 8.69 103.76.5 97.51.5 91.69.5 90 8 83.06 8c-6.68 0-11.64-5.6-17.89-5.6-6 0-9.91 4.09-12.93 12.5 0 0-8.41 23.72-9.49 27.16A6.43 6.43 0 0042.53 44c0 9.22 36.3 39.45 84.94 39.45M160 72.07c1.73 8.19 1.73 9.05 1.73 10.13 0 14-15.74 21.77-36.43 21.77C78.54 104 37.58 76.6 37.58 58.49a18.45 18.45 0 011.51-7.33C22.27 52 .5 55 .5 74.22c0 31.48 74.59 70.28 133.65 70.28 45.28 0 56.7-20.48 56.7-36.65 0-12.72-11-27.16-30.83-35.78'/%3E%3C/svg%3E") no-repeat center;
}}
.closing-slide {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
}}
.closing-slide h2::after {{
  margin-left: auto;
  margin-right: auto;
}}
.closing-list {{
  list-style: none;
  padding: 0;
  margin-top: 1em;
  text-align: left;
}}
.closing-list li {{
  font-size: 0.9em;
  padding: 0.3em 0;
  color: var(--text-dim);
}}
.closing-logo {{
  margin-top: 2em;
}}
.quote-slide {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 100%;
  padding: 2em;
}}
.quote-slide blockquote {{
  font-size: 1.1em;
  font-weight: 500;
  font-style: italic;
  line-height: 1.6;
  color: #fff;
  border: none;
  background: none;
  box-shadow: none;
  max-width: 800px;
}}
.quote-slide .attribution {{
  font-size: 0.65em;
  color: var(--text-muted);
  margin-top: 1.5em;
}}
.agenda-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
  flex: 1;
  align-content: start;
}}
.agenda-card {{
  background: var(--surface);
  backdrop-filter: blur(8px);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1em;
  text-align: center;
}}
.agenda-card svg {{
  margin-bottom: 8px;
  opacity: 0.9;
}}
.agenda-card h4 {{
  font-size: 0.7em;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: var(--text);
  text-transform: none;
  letter-spacing: 0;
}}
.agenda-card p {{
  font-size: 0.55em;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.4;
}}
.image-full-bleed {{
  padding: 0.6em;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}}
.image-standard {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}}
.slide-image {{
  max-width: 100%;
  max-height: 380px;
  object-fit: contain;
  border-radius: 8px;
}}
.image-caption {{
  font-size: 0.6em;
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
  margin-top: 8px;
  line-height: 1.4;
  max-width: 90%;
}}
.image-missing {{
  color: var(--text-muted);
  font-style: italic;
}}
.reveal .progress {{
  color: var(--rh-red);
}}
.reveal .controls button {{
  color: var(--rh-red);
}}
.reveal .slide-number {{
  color: var(--text-muted);
  font-size: 12px;
  font-family: 'Red Hat Display', sans-serif;
}}
</style>
</head>
<body>
<div class="reveal">
<div class="slides">

{sections_html}

</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/reveal.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.1.0/plugin/notes/notes.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
Reveal.initialize({{
  hash: true,
  controls: true,
  progress: true,
  center: false,
  transition: 'slide',
  backgroundTransition: 'fade',
  width: 1280,
  height: 720,
  margin: 0.04,
  slideNumber: true,
  plugins: [RevealNotes]
}});

{D3_JS}
</script>
</body>
</html>'''

with open(OUT_PATH, 'w') as f:
    f.write(full_html)

print(f'Written {len(full_html):,} bytes to {OUT_PATH}')
print(f'{len(sections)} slides generated')
