// const buf = Buffer.from('runoob', 'ascii');

// // console.log(buf);

// console.log(buf.toString('hex'));

// console.log(buf.toString('base64'));

// build a buffer with length 10 filled with 0
const buf1 = Buffer.alloc(10);

console.log(buf1);

// build a buffer with length 10 filled with 0x1
const buf2 = Buffer.alloc(10, 1);

console.log(buf2);

//
const buf3 = Buffer.allocUnsafe(10);

// build a buffer with [0x1, 0x2, 0x3]
const buf4 = Buffer.from([1, 2, 3]);

// build a buffer with a UTF-8 string
const buf5 = Buffer.from('test');

// build a buffer with a Latin-1 string
const buf6 = Buffer.from('test', 'latin1');
console.log(buf6);

const buf7 = Buffer.alloc(256);
len = buf7.write("www.runoob.com");

console.log("write type size: " + len);

//
const buf8 = Buffer.alloc(26);
for(var i = 0; i < 26; i++){
    buf8[i] = i + 97;
}

console.log(buf8.toString('ascii'));
console.log(buf8.toString('ascii', 0 , 5));
console.log(buf8.toString('utf8', 0, 5));
console.log(buf8.toString(undefined, 0, 5));

//
const buf9 = Buffer.from([0x1, 0x2, 0x3, 0x4, 0x5]);
const json = JSON.stringify(buf9);

console.log(json);

//
const copy = JSON.parse(json, (key, value)=>{
    return value && value.type === 'Buffer'?
        Buffer.from(value.data):value;
});

console.log(copy);

//
var buffer1 = Buffer.from(('菜鸟教程: '));
var buffer2 = Buffer.from(('www.runoob.com'));
var buffer3 = Buffer.concat([buffer1, buffer2]);
console.log("buffer3 content. " + buffer3.toString());

//
var buffer4 = Buffer.from('ABC');
var buffer5 = Buffer.from('ABCD');
var result = buffer4.compare(buffer5);

if(result < 0){
    console.log(buffer4 + "is in the front of " + buffer5);
}else if(result == 0){
    console.log(buffer4 + "is equal to " + buffer5);
}else{
    console.log(buffer4 + "is in the back of " + buffer5);
}

var buffer6 = Buffer.from('abcdefghijkl');
var buffer7 = Buffer.from('RUNOOB');
buffer7.copy(buffer6, 2);

console.log(buffer6.toString());

//
var buffer8 = Buffer.from('runoob');

var buffer9 = buffer8.slice(0, 2);
console.log("buffer2 content: " + buffer9.toString());

//
var buffer10 = Buffer.from('www.runoob.com');
console.log("buffer10 length: " + buffer10.length);

//
var buffer_origin = Buffer.from('runoob');
var buffer_slice = buffer_origin.slice(0, 2);
console.log("buffer slice content: " + buffer_slice.toString());
console.log("buffer origin content: " + buffer_origin.toString());
buffer_slice.write('write');

//
console.log("buffer slice content: " + buffer_slice.toString());
console.log("buffer origin content: " + buffer_origin.toString());