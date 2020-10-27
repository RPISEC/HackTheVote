function getAllTextnodes(el){
  let n, a=[], walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null,false);
  while(n=walk.nextNode()) a.push(n);
  return a;
}

function getCaretPosition(el){
  let caretOffset = 0, sel;
  try {
      if (typeof window.getSelection !== "undefined") {
        let range = window.getSelection().getRangeAt(0);
        let selected = range.toString().length;
        let preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(el);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        caretOffset = preCaretRange.toString().length - selected;
      }
  } catch(e) {}
  return caretOffset;
}

function getCaretData(el, position){
  let nodes = getAllTextnodes(el);
  let out = {};
  for(let n=0; n<nodes.length; n++) {
    out.node = nodes[n];
    if (position > nodes[n].nodeValue.length && nodes[n+1]) {
      // remove amount from the position, go to next node
      position -= nodes[n].nodeValue.length;
      out.position = nodes[n].nodeValue.length;
    } else {
      out.position = position;
      break;
    }
  }
  return out;
}

function setCaretPosition(d){
  if (d.node === undefined) return;
  let sel = window.getSelection(),
  range = document.createRange();
  range.setStart(d.node, d.position);
  range.collapse(true);
  sel.removeAllRanges();
  sel.addRange(range);
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }


 $('#text').keydown(function(e) {
     if (e.keyCode === 13) {
         // Check if we are at the end of the pre
         if (this.innerText.length === getCaretPosition(this))
             document.execCommand('insertHTML', false, '\n\n');
         else
             document.execCommand('insertHTML', false, '\n');
         return false;
    }
 });

 let e = function(s, ...k) {
     let o = '';
     for (let i=0; i<s.length; i++) {
         o += s[i];
         if (k[i])
             o += escapeHtml(k[i]);
     }
     return o;
 }

let highlight = function() {
    let el = $('#text');
    let off = getCaretPosition(el[0]);

    let text = el.text();

    text = text.replace(/^.*$/gm,function(x) {
        let m;
        if (m=x.match(/^\s*#.*$/)) {
            return (e`<span class="comment">${m[0]}</span>`)
        }
        if (m=x.match(/^(\s*(?:alias\s+|export\s+)?\w+)(=.*)$/)) {
            return (e`<span class="var">${m[1]}</span>${m[2]}`)
        }
        if (m=x.match(/^(\s*(?:el)?if\s+\[\s+(?:-\w\s+)?)(.*)(\]\s*;\s*(?:then)?\s*)$/)) {
            return e(`<span class="con">${m[1]}</span>${m[2]}<span class="con">${m[3]}</span>`)
        }
        if (m=x.match(/^\s*(fi|else|esac)\s*$/)) {
            return (e`<span class="con">${m[0]}</span>`)
        }
        if (m=x.match(/^(\s*case)(.*)(in\s*)$/)) {
            return e`<span class="con">${m[1]}</span>${m[2]}<span class="con">${m[3]}</span>`
        }
        return escapeHtml(x);
    });
    el.html(text);
    setCaretPosition(getCaretData(el[0], off));
}

let hl_to;
$('#text').on('input propertychange', function(e) {
    if (hl_to) clearTimeout(hl_to);
    hl_to = setTimeout(highlight, 500);
});

$('#save').click(function(e) {
    let name = $('#title').text();
    if (name === 'New Dotfile') name = '';
    $('#nameprompt')[0].value = name
    $('#modal').addClass('is-active');
    $('#textbody')[0].value = $('#text').text();
    $('#nameprompt')[0].focus();
});

$('.close-modal').click(function(e) {
    $('#modal').removeClass('is-active');
    return false;
});

/*
fetch('/get/skel/.bashrc').then(x=>x.text()).then(x=>{
    console.log(x);
    $('#text').text(x);
    highlight();
});
*/
highlight();
