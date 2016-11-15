var system = require('system');
if (system.args.length < 3) {
        console.log("Please include session id!");
        phantom.exit();
}
var page = require('webpage').create();
page.userName = "TestName";
page.password = "CoolPass";
page.userAgent = "NiceMeme";
var win = false;
var done = false;
//page.settings.javascriptEnabled = false;
var doPexit = function() {
    page.open("https://voteforme.DOMAIN/comment?session="+system.args[1]+"&done",function(){});
        setTimeout(function() {
                phantom.exit();
        },1000);
}

page.onUrlChanged = function(targetUrl) {
  console.log('New URL: ' + targetUrl);
  };
page.onAlert = function(msg) {
            console.log("ALERT:" + msg);
                    win = true;
}
//Do fake login here yo


console.log(system.args[2]);

var doTLDLogin = function() {
page.userAgent = "NiceMeme";
    var url1 = "https://MAIN_DOMAIN/login?npctoken="+system.args[2];
    page.open(url1,function(status) {
        if(status === "success") {
            console.log(page.plainText);
        }
        setTimeout(function() {
            doCommentPage();
        },2000);
    });
}

var doCommentPage = function() {
    var url2 = "https://voteforme.DOMAIN/comment?session="+system.args[1];
    //var url2 = "http://itszn.com:1339/comment?session="+system.args[1];
    page.open(url2,function(status) {
        if(status === "success") {
            console.log(page.plainText);
        }
        setTimeout(function() {
            doPexit();
        },5000);
    });
}


var doSiteLogin = function() {
    //var url3 = "https://0000e000c52.chal.itszn.com:8000/";
    var url3 = "https://"+system.args[2]+"/";
    //page.settings.userName="name";
    //page.settings.password="Test";
    //page.settiuserName="target";
    //page.settings.password="#p<T?p8DH*]^@fZ9e.5=M&s%Be[qnq=J";
    page.customHeaders={'Authorization': 'Basic '+btoa('trump:#p<T?p8DH*]^@fZ9e.5=M&s%Be[qnq=J')};
    page.open(url3,function(status) {
        if(status === "success") {
            console.log(page.plainText);
            setTimeout(function() {
                page.settings.userName="";
                page.settings.password="";
                doTLDLogin();
            },2000);
        } else {
            console.log(status);
            doPexit();
        }
    });
}

doSiteLogin();

setTimeout(function() {
        doPexit();
},10000);
