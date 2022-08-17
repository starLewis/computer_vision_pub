// exports.world = function(){
//     console.log('Hello World!');
// }

function Hello(){
    var name;
    this.setName = function(thyname){
            name = thyname;
    };

    this.sayHello = function(){
        console.log('Hello ' + name);
    };
};

module.exports = Hello;