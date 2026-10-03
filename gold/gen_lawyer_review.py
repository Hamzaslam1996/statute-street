import json,random,html,glob
OUT='/mnt/user-data/outputs/navigator'
R=json.load(open(f'{OUT}/gold/rules/all.json')); I={r['gold_id']:r for r in R}
rules=[r for r in R if not r['negative_finding']]
# keep the v0.3 row set so the lawyer's pack is stable across versions
weak=['BOS-SCRN-02','MA-SCRN-02','SA-ALG-01','BERK-FEE-01','BOS-JUST-01']; tests=['CA-ALG-01','HOB-ALG-01','JC-ALG-01','NJ-ALG-01','MA-ALG-P1']; others=['MA-RENT-P1','CA-SCRN-01','BERK-RENT-01','LA-JUST-02','MA-FEE-02']
groups=[('A. Weakest confidence at v0.3 (5)',weak),('B. Change-test rules T1–T4 (5)',tests),('C. T5 ballot question + 4 random others (seed 20261004)',others)]
BAD=('failed','blocked','refused','disallowed','500','cookie','not fetched','timed out')
LINKS={'BOS-JUST-01':['https://www.boston.gov/sites/default/files/file/2021/03/Housing%20Stability%20Notification%20Act.pdf','https://codelibrary.amlegal.com/codes/boston/latest/boston_ma/0-0-0-7149']}
def src(r):
    if r['gold_id'] in LINKS: return LINKS[r['gold_id']]
    ok=[v for v in r['verified_against'] if not any(b in v['result'].lower() for b in BAD)]
    for v in ok:
        if any(k in v['result'].lower() for k in ('official','corpus copy','code publisher')): return [v['url']]
    return [(ok or r['verified_against'])[0]['url']]
ver=json.load(open(f'{OUT}/gold/README.md'.replace('README.md','rules/all.json')))  # noop
VER='v0.4'
hdr=['#','Rule (gold_id)','Citation','Key value','Effective date','Status','Official source','Check (✅/❌/❓ + note)']
intro=f'Internal test material for the Hack-Nation Challenge 02 build. Not legal advice. Prepared 2026-10-04 from gold/rules/all.json ({VER}). 15 rows: the 5 weakest-confidence rules at v0.3, the 5 change-test rules (CA AB 325, Hoboken ban, Jersey City ban, NJ FAIR Act, MA S.2983), and the MA ballot question plus 4 random others. Rows marked "verifier: Hamza" reflect the 2026-10-04 lawyer review batches 1–4; re-check only the ❓ items.'
md=[f'# Statute Street — Lawyer review pack (gold key {VER})\n',f'*{intro}*\n','## How to review (4 points per row)\n','For each row, mark ✅ (correct), ❌ (wrong — write the correct value) or ❓ (cannot confirm) and answer:\n','1. **Citation right?** — Is this the operative section of the law named?','2. **Key value right?** — Is the headline number / formula / prohibition stated correctly?','3. **Date right?** — Is the effective date correct (null = long-standing statute with no stated effective date)?','4. **Status right?** — As of **2026-10-01**: in_force / not_yet_effective / pending / failed?\n','Open the official source link before answering. Return the file (or a photo of the printed table) to Hamza; decisions are then logged in `gold/adjudication_log.csv`.\n']
rows=[]; n=0
for title,ids in groups:
    md.append(f'## {title}\n'); md.append('| '+' | '.join(hdr)+' |'); md.append('|'+'---|'*len(hdr))
    for g in ids:
        r=I[g]; n+=1; us=src(r)
        row=[str(n),f"**{g}**<br>{r['title']} (conf {r['confidence']:.2f}; verifier {r['verifier']})",r['citation'],(r['key_value'] or '—'),(r['effective_date'] or 'null'),r['status'],'<br>'.join(f'[{u}]({u})' for u in us),'']
        md.append('| '+' | '.join(c.replace('|','\\|') for c in row)+' |'); rows.append((title,n,r,us))
    md.append('')
md.append('---\nReviewer: ______________________  Date: __________  Signature: ______________________\n')
open(f'{OUT}/gold/LAWYER_REVIEW.md','w').write('\n'.join(md))
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
font='Helvetica'; c=glob.glob('/usr/share/fonts/**/DejaVuSans.ttf',recursive=True)
if c: pdfmetrics.registerFont(TTFont('DejaVu',c[0])); font='DejaVu'
ss=getSampleStyleSheet(); small=ParagraphStyle('s',parent=ss['BodyText'],fontName=font,fontSize=6.6,leading=8); h=ParagraphStyle('h',parent=ss['Heading2'],fontName=font,fontSize=11)
t=ParagraphStyle('t',parent=ss['Title'],fontName=font,fontSize=15); norm=ParagraphStyle('n',parent=ss['BodyText'],fontName=font,fontSize=9,leading=12)
doc=SimpleDocTemplate(f'{OUT}/gold/LAWYER_REVIEW.pdf',pagesize=landscape(A4),leftMargin=10*mm,rightMargin=10*mm,topMargin=10*mm,bottomMargin=10*mm,title=f'Statute Street — Lawyer review pack (gold key {VER})')
E=html.escape
story=[Paragraph(f'Statute Street — Lawyer review pack (gold key {VER})',t),Paragraph(E(intro),norm),Spacer(1,4),
 Paragraph('<b>How to review — 4 points per row.</b> Mark ✓ correct / ✗ wrong (write the correct value) / ? cannot confirm, for each of: <b>1. Citation right?</b> (operative section named)  <b>2. Key value right?</b> (number / formula / prohibition)  <b>3. Date right?</b> (effective date; null = long-standing statute with no stated effective date)  <b>4. Status right?</b> as of 2026-10-01 (in_force / not_yet_effective / pending / failed). Open the official source link before answering.',norm),Spacer(1,6)]
hdr_pdf=hdr[:-1]+['Check (✓/✗/? + note)']; widths=[8*mm,52*mm,42*mm,45*mm,18*mm,18*mm,52*mm,42*mm]
for title,ids in groups:
    story.append(Paragraph(E(title),h)); data=[[Paragraph(f'<b>{E(x)}</b>',small) for x in hdr_pdf]]
    for (gt,num,r,us) in rows:
        if gt!=title: continue
        data.append([Paragraph(str(num),small),Paragraph(f"<b>{E(r['gold_id'])}</b><br/>{E(r['title'])}<br/><i>conf {r['confidence']:.2f}; verifier {E(r['verifier'])}</i>",small),Paragraph(E(r['citation']),small),Paragraph(E(r['key_value'] or '—'),small),Paragraph(E(r['effective_date'] or 'null'),small),Paragraph(E(r['status']),small),Paragraph('<br/>'.join(f'<link href="{E(u)}">{E(u)}</link>' for u in us),small),Paragraph('1 ☐ cite<br/>2 ☐ value<br/>3 ☐ date<br/>4 ☐ status<br/><br/><br/>',small)])
    tb=Table(data,colWidths=widths,repeatRows=1); tb.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.4,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8e8e8')),('VALIGN',(0,0),(-1,-1),'TOP')])); story+=[tb,Spacer(1,8)]
story.append(Paragraph('Reviewer: ______________________    Date: __________    Signature: ______________________',norm))
doc.build(story); print('lawyer review rebuilt', n)
