// var http = require('http');
// var url = require('url');
// var util = require('util');

// http.createServer(function(req, res){
//     res.writeHead(200, {'Content-Type': 'text/plain; charset=utf-8'});
//     res.end(util.inspect(url.parse(req.url, true)));
// }).listen(3000);

// var http = require('http');
// var url = require('url');
// var util = require('util');

// http.createServer(function(req, res){
//     res.writeHead(200, {'Content-Type': 'text/plain'});

//     var params = url.parse(req.url, true).query;
//     res.write("website name: " + params.name);
//     res.write("\n");
//     res.write("web url: "+ params.url);
//     res.end();
// }).listen(3000);

var http = require('http');
var querystring = require('querystring');

var postHTML = 
    '<html><head><meta charset="utf-8"><title>cainiao jiaocheng Node.js instance</title></head>'+
    '<body>' +
    '<form method="post">' +
    '网站名: <input name="name"><br>' + 
    'Website URL: <input name="url"><br>' +
    '<input type="submit">' +
    '</form></body></html>'
;

http.createServer(function(req, res){
    var body = "";
    req.on('data', function (chunk){
        body += chunk;
    });

    req.on('end', function(){
        //
        body = querystring.parse(body);
        res.writeHead(200, {'Content-Type': 'txt/html; charset=utf8'});

        if(body.name && body.url){
            res.write("web name: " + body.name);
            res.write("<br>");
            res.write("web URL: " + body.url);
        }else{
            res.write(postHTML);
        }

        res.end();
    });
}).listen(3000);