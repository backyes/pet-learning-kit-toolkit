# Layout: making an article readable

The goal is one continuous piece of prose that a person can read for twenty minutes without noticing the interface.

## The reading-page contract

| Element | Treatment |
|---|---|
| Page | warm paper background, single 690px measure, generous bottom padding |
| Section | heading + paragraphs only. No card, no border, no shadow |
| Section heading | small letterspaced numeral, serif title, muted Chinese subtitle, one small “朗读本节” text link |
| English paragraph | serif, 1.05rem, line-height 1.95, spacing `.5em` |
| Chinese translation | own `<p class="zh">`, 0.85rem, muted, directly under its paragraph, no border, no background |
| Word list | `<details>` collapsed to one line “本节生词 · 16” |
| Audio | one collapsed summary line at top + per-paragraph ghost button + per-section link |
| Controls | sticky toolbar with 中文 / 点读 / A− / A+ only |

## Skeleton

```html
<section class="sec" id="r1">
  <header class="sechead">
    <div class="num">01</div>
    <h2>The Dursleys of Privet Drive</h2>
    <div class="zhtitle">女贞路的德思礼一家</div>
    <div class="secbar">
      <button class="playall" data-sec="1">▶ 朗读本节</button>
      <span class="meta">3 段 · 1:23</span>
    </div>
  </header>

  <div class="prose">
    <p class="para" data-i="1">English paragraph …</p>
    <p class="zh">中文译文…</p>
  </div>

  <details class="vocabbox">
    <summary>本节生词 · 16</summary>
    <div class="chips">
      <button class="chip" data-a="audio/words/001.mp3"><b>perfectly</b><i>完全地</i><span class="mini">🔊</span></button>
    </div>
  </details>
</section>
```

## Core CSS

```css
body{background:#faf7f0;color:#221d17;line-height:1.95}
.wrap{max-width:690px;margin:0 auto;padding:0 22px 90px}

/* 章节标题：不装箱子 */
.sec{padding:34px 0 6px}
.sechead .num{font-size:.72rem;letter-spacing:.3em;color:#b09a72;text-transform:uppercase}
.sechead h2{font-family:Georgia,serif;font-size:1.28rem;margin:0 0 4px;color:#31243f}
.sechead .zhtitle{font-size:.82rem;color:#a2947e}
.secbar{display:flex;gap:12px;align-items:center;margin-top:12px}
.playall{border:0;background:none;color:#5b3a8e;font-size:.8rem;cursor:pointer;
         border-bottom:1px dashed #cbb9e8;padding:0}

/* 正文 */
.prose .para{position:relative;font-family:Georgia,"Iowan Old Style",serif;
             font-size:1.05rem;line-height:1.95;margin:0 0 .5em}
.prose .para b{color:#6f2a86;font-weight:600;
               background:linear-gradient(transparent 72%,#f0e2f7 72%)}
.prose .para.playing{background:#fdf4dd}          /* 高亮只改背景，不产生位移 */

/* 译文＝注脚 */
.prose .zh{font-size:.85rem;line-height:1.85;color:#7d7264;margin:0 0 1.45em;padding:0}
body.hide-zh .prose .zh{display:none}
body.hide-zh .prose .para{margin-bottom:1.15em}   /* 纯英文时补回段距 */

/* 段落按钮在页边 */
.para .pbtn{position:absolute;left:-30px;top:.55em;width:22px;height:22px;border-radius:50%;
            border:1px solid #ded3be;background:#fff;color:#9c8f79;font-size:10px;
            opacity:0;transition:.2s;padding:0}
.para:hover .pbtn{opacity:.85}
.para.playing .pbtn{opacity:1;background:#1f6b53;color:#fff;border-color:#1f6b53}
@media(max-width:700px){ .para .pbtn{display:none} }

/* 生词折叠 */
.vocabbox{margin:14px 0 6px;border-top:1px solid #e6dcc8;padding-top:10px}
.vocabbox summary{font-size:.76rem;color:#a2947e;list-style:none;cursor:pointer}
.vocabbox summary::-webkit-details-marker{display:none}
.vocabbox summary::before{content:"＋ "}
.vocabbox[open] summary::before{content:"− "}
```

## Mobile (≤600px)

- `.wrap` padding 16px; `.prose .para` 1rem / line-height 1.9
- `.zh` 0.82rem
- hide `.pbtn` entirely; provide a **点读** toolbar toggle instead — when on, tapping a paragraph plays it
- 44px minimum tap targets for speed / toolbar buttons
- the audio summary line must stay one line; the player opens only on demand

## Tables

Generated kits contain wide tables (paraphrase lists, glossaries). Never let them force horizontal page scroll.

```js
document.querySelectorAll('.tablewrap').forEach(function(w){
  var tr = w.querySelector('tr'); if(!tr) return;
  var n = tr.children.length; w.dataset.cols = n;
  if(n >= 5){ /* insert a "← 左右滑动查看完整表格 →" hint above */ }
});
```

```css
@media(max-width:600px){
  th,td{padding:7px 8px;font-size:.78rem}
  th{white-space:normal}
  .tablewrap[data-cols="1"] table,.tablewrap[data-cols="2"] table,
  .tablewrap[data-cols="3"] table,.tablewrap[data-cols="4"] table{min-width:0}
  .tablewrap[data-cols="5"] table,.tablewrap[data-cols="6"] table{min-width:520px}
  .tablewrap[data-cols="6"] th:first-child,
  .tablewrap[data-cols="6"] td:first-child{display:none}   /* 去掉序号列 */
}
```

## Print

```css
@media print{
  .hero{background:#fff!important;color:#000!important}
  .toolbar,.secbar,.pbtn,.fullbox,#toTop,.vocabbox,.spell{display:none!important}
  .prose .para{font-size:11.5pt;line-height:1.7}
  .prose .zh{color:#444;font-size:9pt}
}
```

## What breaks reading (all observed)

1. **A control column.** Reserving 30px for buttons shrinks the measure and indents every paragraph. Put controls in the margin with `position:absolute`, or hide them.
2. **Per-paragraph cards.** A border/shadow per paragraph turns an article into a form.
3. **Bordered translation.** A 2px left rule on every translation re-fragments the page. Colour and size are enough.
4. **Always-open vocabulary.** A block of 17 chips after every section reads as a new page section. Collapse it.
5. **A big player at the top.** Audio is secondary; collapse it into one line.
6. **`line-height` below 1.85 for 1rem+ serif text.** It looks cramped on phones.
7. **Highlighting the playing paragraph by changing padding/margin.** Use background only, or text reflows.

## Typography defaults that worked

- English: Georgia / Iowan Old Style / Times New Roman, 1.05rem, 1.95
- Chinese: system sans (PingFang SC), 0.85rem, 1.85, colour `#7d7264`
- Headings: Georgia + 宋体 fallback
- Highlight colour: purple `#6f2a86` with a soft underline gradient, not bold black
- Never italicise Chinese for emphasis
