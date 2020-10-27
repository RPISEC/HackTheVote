const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  /*
  await page.setRequestInterception(true);
  page.on('request', interceptedRequest=> {
      console.log(interceptedRequest.url());
      interceptedRequest.continue();
  });
  page.on('console', msg => {
    for (let i = 0; i < msg.args().length; ++i)
        console.log(`${i}: ${msg.args()[i]}`);
  });
  page.on("pageerror", function(err) {  
      console.log("Page error: " + err); 
  });
  page.on("error", function (err) {  
      console.log("Error: " + err); 
  });
  //*/
  await page.goto(process.argv[2]);
  await page.waitFor(5000);
  /*
  let c = await page.cookies()
  console.log("Cookies",c);
  */
  await browser.close();
})();
