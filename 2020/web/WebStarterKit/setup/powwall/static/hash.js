function do_pow(pow) {
  let solutions = [];
  return new Promise(resolve => {
    let workers = [];
    for (let i=0; i<navigator.hardwareConcurrency; i++) {
      let w = new Worker('/static/pow_worker.js');
      workers.push(w);
      w.onmessage = function(event) {
        solutions.push(event.data);

        document.getElementById('pow_bar').value = solutions.length;

        if (window.pow_count === solutions.length) {
          for (let w of workers) {
            w.terminate();
          }
          resolve(solutions);
        }
      }
      w.postMessage({pow:pow});
    }
  });
}

let pow_sol = null;

let btn = document.getElementById('do_pow');

btn.onclick = x=>{
  if (pow_sol !== null) {
    document.getElementById('pow_sol').value = pow_sol;
    $('#pow_sol')[0].value = pow_sol;
    window.forms[0].submit();
    return false;
  }

  btn.innerText = 'Calculating POW...';
  btn.disabled = true;
  fetch(window.pow_url,{credentials:'include'})
  .then(x=>x.json())
  .then(x=>do_pow(x.pow))
  .then(res=>{
    pow_sol = res.join(';');
    console.log('POW solution found:',pow_sol);
    btn.innerText = 'Submit POW';
    btn.disabled = false;
  });
  return false;
};
