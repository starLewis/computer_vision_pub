var http = require('http')

http.createServer(function (request, response){
    //**send http header */
    //**Http state: 200: ok */
    //**content: text/plain */
    response.writeHead(200, {'Content-Type': 'text/plain'});

    //**send data "Hello World" */
    response.end('Hello World\n');
}).listen(8888);

//**print in terminator */
console.log('Sever running at http://127.0.0.1:8888/');
