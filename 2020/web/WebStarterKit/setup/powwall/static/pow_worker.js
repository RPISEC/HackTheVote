self.importScripts('/static/sha256.min.js');

function random_str(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

function do_pow(pow) {
  let data = random_str(32);
  let len = pow.length;
  while (1) {
    next = sha256(data);
    if (next.slice(0,len) === pow) 
      return data;
    data = next;
  }
}

self.addEventListener("message", function(event) {
  let pow = event.data.pow;
  while(1) {
    let res = do_pow(pow);
    self.postMessage(res);
  }
});

