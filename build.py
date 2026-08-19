# -*- coding: utf-8 -*-
import json, html, re
d = json.load(open('data.json', encoding='utf-8'))
C, S, INV = d['course'], d['slots'], d['invitees']

CSS = """
*{box-sizing:border-box}
body{margin:0;padding:0;background:#f7f6f3;color:#1c1917;
  font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;line-height:1.6}
.wrap{max-width:940px;margin:0 auto;padding:32px 20px 72px}
header{margin-bottom:26px}
.eyebrow{font-size:12px;letter-spacing:.18em;color:#a8a29e;text-transform:uppercase;margin-bottom:8px}
h1{font-size:26px;margin:0 0 10px;letter-spacing:.01em;font-weight:600}
.facts{display:flex;flex-wrap:wrap;gap:6px 20px;font-size:13.5px;color:#57534e;margin:0 0 6px;padding:0;list-style:none}
.facts li{white-space:nowrap}
.facts b{font-weight:600;color:#1c1917}
.updated{font-size:12px;color:#a8a29e;margin-top:10px}
.lede{background:#fff;border:1px solid #e7e3dd;border-left:3px solid #c9c2b6;border-radius:0 10px 10px 0;
  padding:15px 18px;font-size:14px;color:#44403c;margin:22px 0 28px}
.card{background:#fff;border:1px solid #e7e3dd;border-radius:12px;overflow:hidden;margin-bottom:26px}
.card h2{font-size:13px;margin:0;padding:14px 18px;border-bottom:1px solid #e7e3dd;background:#fbfaf8;
  font-weight:600;letter-spacing:.06em;color:#57534e}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:11px 16px;text-align:left;border-bottom:1px solid #efece7;vertical-align:top}
th{font-size:11px;font-weight:600;color:#a8a29e;letter-spacing:.08em;background:#fcfbf9;
  text-transform:uppercase;white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td.date{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:600;font-size:14.5px}
td.wk{color:#a8a29e;font-size:12px;white-space:nowrap}
.tbd{color:#c4bfb8}
.fixedcell{color:#57534e}
.who{font-weight:600}
.field{display:block;font-size:12px;color:#8b8681;margin-top:3px;font-weight:400;line-height:1.5}
.tag{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:99px;border:1px solid #e7e3dd;
  color:#8b8681;background:#fbfaf8;margin-left:7px;vertical-align:1px;white-space:nowrap}
tr.exam td{background:#faf8f5;color:#a8a29e;font-size:13px}
.pill{display:inline-block;font-size:11px;padding:2px 9px;border-radius:99px;border:1px solid;white-space:nowrap}
.p-confirmed{color:#2f6b46;border-color:#c2ddcc;background:#f2f8f4}
.p-sent{color:#8a6a1c;border-color:#e8daae;background:#fcf8ec}
.p-draft{color:#5b6478;border-color:#d6dbe4;background:#f5f7fa}
.p-todo{color:#a8a29e;border-color:#e7e3dd;background:#fbfaf8}
.mail{font-size:12px;color:#8b8681;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.memo{font-size:12px;color:#8b8681}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 24px}
.stat{background:#fff;border:1px solid #e7e3dd;border-radius:10px;padding:12px 16px;min-width:100px;flex:1 1 auto}
.stat .n{font-size:22px;font-weight:600;line-height:1.15}
.stat .l{font-size:11.5px;color:#a8a29e;margin-top:3px}
.notes{font-size:12.5px;color:#8b8681;line-height:1.9;margin:0;padding-left:1.1em}
footer{margin-top:34px;padding-top:18px;border-top:1px solid #e7e3dd;font-size:12px;color:#a8a29e}
@media (max-width:640px){
  .wrap{padding:22px 13px 56px} h1{font-size:21px}
  th,td{padding:9px 11px;font-size:13px} .facts{gap:4px 14px;font-size:12.5px}
  .mail{word-break:break-all}
}
"""

def head(title):
    return ('<!DOCTYPE html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{html.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n<div class="wrap">\n')

def header_block(sub=None):
    o = ['<header>',
         f'<div class="eyebrow">國立臺灣海洋大學　食品科學系</div>',
         f'<h1>{C["term"]}　{C["title"]}</h1>',
         '<ul class="facts">',
         f'<li>課號　<b>{C["code"]}</b></li>',
         f'<li>開課班級　<b>{C["class"]}</b></li>',
         f'<li>時間　<b>{C["time"]}</b></li>',
         f'<li>地點　<b>{C["venue"]}</b></li>',
         f'<li>每場　<b>{C["length"]}</b></li>',
         f'<li>授課教師　<b>{C["teachers"]}</b></li>',
         '</ul>']
    if sub:
        o.append(f'<div class="updated">{sub}</div>')
    o.append('</header>')
    return '\n'.join(o)

def cell(x, show_field):
    if not x:
        return '<span class="tbd">待安排</span>'
    t = x.get('type')
    if t == 'fixed':
        return f'<span class="fixedcell">{x["name"]}</span>'
    s = f'<span class="who">{x["name"]}　{x.get("rank","")}</span>'
    if x.get('note'):
        s += f'<span class="tag">{x["note"]}</span>'
    if show_field and x.get('field'):
        s += f'<span class="field">{x["field"]}</span>'
    return s

def schedule_table(show_field=True, show_exam=True):
    o = ['<div class="card"><h2>演講排程</h2><table>',
         '<thead><tr><th>日期（週二）</th><th>週次</th><th>15:10 – 16:00</th><th>16:05 – 16:55</th></tr></thead><tbody>']
    for r in S:
        if 'exam' in r:
            if not show_exam:
                continue
            o.append(f'<tr class="exam"><td class="date">{r["date"]}</td>'
                     f'<td class="wk">第 {r["wk"]} 週</td>'
                     f'<td colspan="2">{r["exam"]}－ 不排演講</td></tr>')
        else:
            o.append(f'<tr><td class="date">{r["date"]}</td><td class="wk">第 {r["wk"]} 週</td>'
                     f'<td>{cell(r.get("a"), show_field)}</td><td>{cell(r.get("b"), show_field)}</td></tr>')
    o.append('</tbody></table></div>')
    return '\n'.join(o)

LABEL = {'confirmed':('已回覆確認','p-confirmed'),'sent':('已寄出　待回覆','p-sent'),
         'draft':('草稿已備　待寄','p-draft'),'todo':('待建草稿','p-todo')}

def build_full(public=False):
    cnt = {k: sum(1 for i in INV if i['status'] == k) for k in LABEL}
    o = [head('115-1 專題演講排程表（完整版）'), header_block(f'最後更新　{C["updated"]}　｜　完整版（授課教師內部使用）' + ('　·　公開連結請勿外傳' if public else '') + ''),
         f'<div class="lede">{d["intro"]}</div>',
         '<div class="stats">',
         f'<div class="stat"><div class="n">{cnt["confirmed"]}</div><div class="l">已確認</div></div>',
         f'<div class="stat"><div class="n">{cnt["sent"]}</div><div class="l">已寄出待覆</div></div>',
         f'<div class="stat"><div class="n">{cnt["draft"]+cnt["todo"]}</div><div class="l">尚未寄出</div></div>',
         f'<div class="stat"><div class="n">{len(INV)}</div><div class="l">邀請對象</div></div>',
         '<div class="stat"><div class="n">26</div><div class="l">可排時段</div></div>',
         '</div>',
         schedule_table(show_field=True)]
    for b in ['第一批', '第二批']:
        rows = [i for i in INV if i['batch'] == b]
        thead = ('<thead><tr><th>老師</th><th>職稱</th><th>狀態</th><th>已排時段</th><th>備註</th></tr></thead><tbody>'
                 if public else
                 '<thead><tr><th>老師</th><th>職稱</th><th>聯絡信箱</th><th>狀態</th><th>已排時段</th><th>備註</th></tr></thead><tbody>')
        o.append(f'<div class="card"><h2>邀請狀態　·　{b}（{len(rows)} 位）</h2><table>' + thead)
        for i in rows:
            lab, cls = LABEL[i['status']]
            mailcell = '' if public else f'<td class="mail">{i["e"]}</td>'
            memo = i["memo"]
            if public:
                memo = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+', '另一信箱', memo)
            o.append(f'<tr><td class="who">{i["n"]}</td><td class="memo">{i["r"]}</td>'
                     f'{mailcell}'
                     f'<td><span class="pill {cls}">{lab}</span></td>'
                     f'<td>{i["slot"] or "<span class=tbd>—</span>"}</td>'
                     f'<td class="memo">{memo}</td></tr>')
        o.append('</tbody></table></div>')
    o.append('<div class="card"><h2>作業備註</h2><div style="padding:14px 18px"><ul class="notes">'
             + ''.join(f'<li>{n}</li>' for n in d['notes']) + '</ul></div></div>')
    o.append(f'<footer>國立臺灣海洋大學 食品科學系　{C["title"]}（{C["code"]}）　完整版．授課教師內部使用</footer>')
    o.append('</div>\n</body>\n</html>')
    return '\n'.join(o)

def build_student():
    o = [head('115-1 專題演講　課程資訊與排程'), header_block(f'最後更新　{C["updated"]}'),
         f'<div class="lede">{d["intro"]}</div>',
         schedule_table(show_field=True),
         '<div class="card"><h2>修課提醒</h2><div style="padding:14px 18px"><ul class="notes">'
         '<li>每週二第八、九節於系演講廳（MFS001）上課，請準時入座。</li>'
         '<li>排程仍在陸續確認中，講者確定後會更新於本頁，請不定期回來查看。</li>'
         '<li>10/27（期中考試週）與 12/22（期末考試週）不排演講。</li>'
         '<li>對哪一間實驗室有興趣，歡迎於演講後直接與該位老師聯繫。</li>'
         '</ul></div></div>',
         f'<footer>國立臺灣海洋大學 食品科學系　{C["title"]}（{C["code"]}）　授課教師：{C["teachers"]}</footer>',
         '</div>\n</body>\n</html>']
    return '\n'.join(o)

# --- 輸出 ---------------------------------------------------------------
# index.html          學生版（公開）
# t-f37b3eb9d27c.html   完整版（公開，無信箱）
# _internal_full.html 完整版（含信箱，不上傳；要寄給陳建利老師時用這份）
SLUG = 't-f37b3eb9d27c'
import os, re as _re
open('index.html', 'w', encoding='utf-8').write(build_student())
open(SLUG + '.html', 'w', encoding='utf-8').write(build_full(public=True))
open('_internal_full.html', 'w', encoding='utf-8').write(build_full(public=False))

leak = [m for m in _re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+', open(SLUG+'.html',encoding='utf-8').read()) if not m.startswith('@')]
assert not leak, f'公開版仍含 email：{leak}'
print('OK  index.html / ' + SLUG + '.html / _internal_full.html　已產生，公開版無 email')
