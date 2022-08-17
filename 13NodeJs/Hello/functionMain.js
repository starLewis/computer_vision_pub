// function say(word){
//     console.log(word);
// }

// function execute(someFunction, value){
//     someFunction(value);
// }

// execute(say, "Hello");


//
// function execute(someFunction, value){
//     someFunction(value);
// }

// execute(function(world){console.log(world);}, "Hello");


var http = require("http");

function onRequest(request, response){
    response.writeHead(200, {"Content-Type": "text/plain"});
    response.write("Hello World");
    response.end();
}

http.createServer(onRequest).listen(8888);