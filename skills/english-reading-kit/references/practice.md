# Practice: spelling test and wrong-answer notebook

Two interlocking features. The test produces the errors; the notebook consumes them.

## Spelling test with 60% masking

Goal: the learner sees a partial word plus its Chinese gloss, types the whole word, and gets positional feedback.

### Masking algorithm

Keep ~40% of the letters, always including the first and the last. Distribute the remaining visible letters evenly across the word.

```js
function pattern(w){
  var pos=[]; for(var i=0;i<w.length;i++) if(/[A-Za-z]/.test(w[i])) pos.push(i);
  var n=pos.length;
  var vis=Math.max(2, Math.round(n*0.4));
  if(vis > n-1) vis=Math.max(1, n-1);
  var show={}; show[pos[0]]=1; if(n>1) show[pos[n-1]]=1;
  var rem=vis-Object.keys(show).length;
  for(var k=1;k<=rem;k++) show[pos[Math.min(n-1,Math.round(k*n/(rem+1)))]]=1;
  var out='';
  for(var j=0;j<w.length;j++){
    var c=w[j];
    if(/[A-Za-z]/.test(c)) out += show[j] ? '<b>'+c+'</b>' : '<i>_</i>';
    else if(c===' ') out += '&nbsp;&nbsp;';
    else out += '<b>'+c+'</b>';          // hyphens, apostrophes stay visible
  }
  return out;
}
```

Observed blank ratios: `firm` 50%, `perfectly` 56%, `mysterious` 60%, `nephew` 67%, `exasperated` 64%. Small words cannot hit exactly 60% — say “约 60%” in the UI, not “60%”.

### Error feedback

```js
var a = letters(v), b = letters(t);   // letters only, lowercased
if (a === b) → “字母都对，但顺序或连字符不对”
else {
  if (a.length !== b.length) “长度不对：答案 N 个字母，你写了 M 个”
  for (k …) if (a[k] !== b[k]) “第 k+1 个字母应为 b[k]，你写的是 a[k]”   // max 3
}
```

Rules:
- compare **letters only**, so a wrong hyphen is reported as an ordering problem, not as “第 1 个字母错”;
- cap at 3 messages;
- Enter submits;
- on success lock the input, turn it green, keep the value visible.

### Item grouping

Group by level: PET core (B1 + 熟词僻义) / B2 / C1 / all. Default to the exam-relevant group. Show `已答对 / 当前组` and keep per-item state when switching groups.

## Wrong-answer notebook

### Data model

One `localStorage` key shared by every page on the same origin:

```
hp1.wrong.v1 = {
  "mysterious": { w:"mysterious", m:"神秘的", lv:"b2",
                  a:"audio/words/002.mp3", n:2, t:1699999999999 }
}
```

`n` = remaining correct answers needed (not “times wrong”). Count **down**:

- wrong answer → `n = min(5, n+1)`
- correct answer → `n = n-1`; delete the entry at 0

This gives “答对一次消一格” and naturally keeps a word around for two or three passes.

### Practice loop

One card at a time, not a list.

```
queue = shuffle(keys of storage)
show queue[0]
  correct → n--  ; if n>0 push key to the end of the queue, else delete
            toast “✓ 答对，还差 N 次 / 已移除” + 撤销
  wrong   → n++  ; stay on the same card, let the user retry
  reveal  → n++  ; after ~1.2 s move to the end
  skip    → rotate queue, no score change
queue empty → if storage still has words: “本轮过完了，还有 N 个”；else “清空了”
```

Do **not** mutate the queue on a wrong answer while the card is still displayed — the next `shift()` would remove a different word. Only rotate on correct / skip / reveal.

### Robustness

`localStorage` throws on some `file://` contexts (notably Safari). Wrap everything:

```js
var LS_OK=(function(){ try{ localStorage.setItem('__t','1'); localStorage.removeItem('__t'); return true; }catch(e){ return false; } })();
```

- if unavailable: keep an in-memory object, show a warning banner, and rely on export/import;
- provide **导出** (JSON into a textarea + copy) and **导入** (parse + merge) so records survive device changes;
- listen to the `storage` event so two open tabs stay in sync.

### UI details that matter

- level chip + “还差 N 次” on the card;
- 🔊 button on every card (reuse the word clips);
- a **听写** mode that hides the letter pattern entirely — same engine, no pattern;
- an “全部错题” collapsible list with per-row delete;
- undo toast for both “removed on correct” and “manually deleted”.

## Wiring the test to the notebook

The test page needs a tiny module:

```js
var WB=(function(){
  var KEY='hp1.wrong.v1';
  return {
    add:function(w,m,lv,audio){ var o=all(), r=o[w]||{w:w,m:m,lv:lv,a:audio,n:0};
      r.n=Math.min(5,(r.n||0)+1); r.t=Date.now(); o[w]=r; save(o); badge(); },
    ok:function(w){ var o=all(), r=o[w]; if(!r) return; r.n--; r.n<=0 ? delete o[w] : o[w]=r;
      save(o); badge(); }
  };
})();
```

Call `WB.add` on wrong answer **and** on “看答案”, `WB.ok` on a correct answer. Show the count as a badge on the “📕 错题本” link.
