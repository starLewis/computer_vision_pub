#include <stdio.h>
#include <python2.7/Python.h>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <numpy/arrayobject.h>

void printDict(PyObject* obj){
    if(!PyDict_Check(obj))
        return;
    PyObject *k, *keys;
    keys = PyDict_Keys(obj);
    for(int i = 0; i < PyList_GET_SIZE(keys); i++){
        k = PyList_GET_ITEM(keys, i);
        char* c_name = PyString_AsString(k);
        printf("%s\n", c_name);
    }
}

void testCCallPythonNoArgs(){
    Py_Initialize();
    if(!Py_IsInitialized()){
        std::cout<<"Py Initialize failed!"<<std::endl;
        return;
    }

    PyObject* pModule = NULL;
    PyObject* pDict = NULL;
    PyObject* pFunc = NULL;
    PyObject* pValue = NULL;
    PyObject* pArgs = NULL;

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('/home/lewisliu/Clobotics/Codes/CVTestCodes/14CCallPython')");

    pModule = PyImport_ImportModule("hello");
    if(!pModule){
        std::cout<<"cannot find module hello.py!"<<std::endl;
        return;
    }

    pDict = PyModule_GetDict(pModule);
    printDict(pDict);
    pFunc = PyDict_GetItemString(pDict, (char*)"print_arr");
    if(!pFunc || !PyCallable_Check(pFunc)){
        std::cout<<"cannot find function [print_arr]!"<<std::endl;
        return;
    }

    pArgs = PyTuple_New(0);
    pValue = PyObject_CallObject(pFunc, pArgs);
    std::cout<<PyLong_AsLong(pValue)<<std::endl;

    Py_Finalize();

    return;

}

//** test c call python with one argument
void testCCallPython1Arg(){
    Py_Initialize();
    if(!Py_IsInitialized()){
        std::cout<<"Py Initialize failed!"<<std::endl;
        return;
    }

    PyObject* pModule = NULL;
    PyObject* pDict = NULL;
    PyObject* pFunc = NULL;
    PyObject* pValue = NULL;
    PyObject* pArgs = NULL;

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('/home/lewisliu/Clobotics/Codes/CVTestCodes/14CCallPython')");

    pModule = PyImport_ImportModule("hello");
    if(!pModule){
        std::cout<<"cannot find module hello.py!"<<std::endl;
        return;
    }

    pDict = PyModule_GetDict(pModule);
    printDict(pDict);
    pFunc = PyDict_GetItemString(pDict, (char*)"doStuff");
    if(!pFunc || !PyCallable_Check(pFunc)){
        std::cout<<"cannot find function [doStuff]!"<<std::endl;
        return;
    }

    pArgs = PyTuple_New(1);
    PyTuple_SetItem(pArgs, 0, Py_BuildValue("i", 1));
    pValue = PyObject_CallObject(pFunc, pArgs);
    std::cout<<PyLong_AsLong(pValue)<<std::endl;

    Py_Finalize();
    return;
}

//** test c call python with an array
void testCCallPythonWithArray(){
    Py_Initialize();
    if(!Py_IsInitialized()){
        std::cout<<"Py Initialize failed!"<<std::endl;
        return;
    }

    PyObject* pModule = NULL;
    PyObject* pDict = NULL;
    PyObject* pFunc = NULL;
    PyObject* pValue = NULL;
    PyObject* pArgs = NULL;

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('/home/lewisliu/Clobotics/Codes/CVTestCodes/14CCallPython')");

    pModule = PyImport_ImportModule("hello");
    if(!pModule){
        std::cout<<"cannot find module hello.py!"<<std::endl;
        return;
    }

    pDict = PyModule_GetDict(pModule);
    printDict(pDict);
    pFunc = PyDict_GetItemString(pDict, (char*)"change");
    if(!pFunc || !PyCallable_Check(pFunc)){
        std::cout<<"cannot find function [change]!"<<std::endl;
        return;
    }

    pArgs = PyTuple_New(1);
    //** method 01
//    PyTuple_SetItem(pArgs, 0, Py_BuildValue("[iiii]", 1, 2, 3, 4));

    //** method 02
    PyObject* pList = NULL;
    pList = PyList_New(0);
    for(int i = 0; i < 10; i++){
        PyList_Append(pList, Py_BuildValue("i",i));
    }
    PyTuple_SetItem(pArgs, 0, pList);

    pValue = PyObject_CallObject(pFunc, pArgs);
    std::cout<< PyLong_AsLong(pValue)<<std::endl;

    Py_Finalize();

}

//** test c call python with 2 arguments
void testCCallPythonWith2Arguments(){
    Py_Initialize();
    if(!Py_IsInitialized()){
        std::cout<<"Py Initialize failed!"<<std::endl;
        return;
    }

    PyObject* pModule = NULL;
    PyObject* pDict = NULL;
    PyObject* pFunc = NULL;
    PyObject* pValue = NULL;
    PyObject* pArgs = NULL;

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('/home/lewisliu/Clobotics/Codes/CVTestCodes/14CCallPython')");

    pModule = PyImport_ImportModule("hello");
    if(!pModule){
        std::cout<<"cannot find module hello.py!"<<std::endl;
        return;
    }

    pDict = PyModule_GetDict(pModule);
    printDict(pDict);
    pFunc = PyDict_GetItemString(pDict, (char*)"add2args");
    if(!pFunc || !PyCallable_Check(pFunc)){
        std::cout<<"cannot find function [doStuff]!"<<std::endl;
        return;
    }

    pArgs = PyTuple_New(2);
    PyTuple_SetItem(pArgs, 0, Py_BuildValue("i", 1));
    PyTuple_SetItem(pArgs, 1, Py_BuildValue("i", 2));
    pValue = PyObject_CallObject(pFunc, pArgs);
    std::cout<<PyLong_AsLong(pValue)<<std::endl;

    Py_Finalize();

    return;
}

uchar* data = (uchar*)malloc(sizeof(uchar)*900*200);
PyObject* convertImageToPyArray(cv::Mat& img){
    cv::resize(img,img,cv::Size(300,200));

    int m, n;
    m = img.cols*img.channels();
    n = img.rows;

//    uchar data[180000];

//    unsigned char* data = (unsigned char*)malloc(sizeof(unsigned char) *m * n);
    int p = 0;
    for(int i=0;i<m;i++){
        for(int j=0;j<n;j++){
            data[p] = img.at<uchar>(j, i);
            p++;
        }
    }

    std::cout<<"convert successfully!"<<std::endl;

    npy_intp Dims[2] = {m, n};
    PyObject* pArray = PyArray_SimpleNewFromData(2, Dims, NPY_UBYTE, (void*)data);
    PyObject* argArray = PyTuple_New(1);
    PyTuple_SetItem(argArray, 0, pArray);

//    free(data);

    return argArray;
}

int convertPyListToMat(PyObject* pyList, cv::Mat& resImg){
    cv::Mat resultImg(200,300, CV_8UC1,cv::Scalar(0,0,0));
    int sizeR = PyList_Size(pyList);
    PyObject* pRect = PyList_GetItem(pyList, 0);
    int sizeC = PyList_Size(pRect);
    std::cout<<"sizeR: "<< sizeR<<" sizeC: "<<sizeC<<std::endl;
    if(sizeR != resultImg.rows)
    {
        std::cout<<"the rows'size is not the same!"<<std::endl;
    }
    int uintData;
    for(int i=0;i<sizeR;i++){
        pRect = PyList_GetItem(pyList, i);
        if(PyList_Check(pRect)){
            for(int j=0;j<sizeC;j++){
                PyObject* item = PyList_GetItem(pRect, j);
                PyArg_Parse(item,"i",&uintData);
                resultImg.at<uchar >(i,j) = uintData;
            }
        }
    }
    resultImg.copyTo(resImg);
    return 0;
}

//** test c call python with image
void testCCallPythonWith1Image(){
    Py_Initialize();
    import_array();
    if(!Py_IsInitialized()){
        std::cout<<"Py Initialize failed!"<<std::endl;
        return;
    }

    PyObject* pModule = NULL;
    PyObject* pDict = NULL;
    PyObject* pFunc = NULL;
    PyObject* pValue = NULL;
    PyObject* pArgs = NULL;

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('/home/lewisliu/Clobotics/Codes/CVTestCodes/14CCallPython')");
//    PyRun_SimpleString("import numpy as np");

    pModule = PyImport_ImportModule("hello");
    if(!pModule){
        std::cout<<"cannot find module hello.py!"<<std::endl;
        return;
    }

    pDict = PyModule_GetDict(pModule);
    printDict(pDict);
    pFunc = PyDict_GetItemString(pDict, (char*)"load_image");
    if(!pFunc || !PyCallable_Check(pFunc)){
        std::cout<<"cannot find function [load_image]!"<<std::endl;
        return;
    }

    std::string imgPath = "/home/lewisliu/Desktop/defog_03.png";
    cv::Mat img = cv::imread(imgPath);

    pArgs = convertImageToPyArray(img);
    pValue = PyObject_CallObject(pFunc, pArgs);

    cv::Mat resultImg;

    convertPyListToMat(pValue,resultImg);

    cv::imshow("2",resultImg);

    cv::imshow("1",img);
    cv::waitKey(0);
}

int main(int argc, char** argv){

    //** test c call python function without arguments
//    testCCallPythonNoArgs();

    //** test c call python function with 1 argument
//    testCCallPython1Arg();

    //** test c call python function with an array
//    testCCallPythonWithArray();

    //** test c call python function with 2 arguments
//    testCCallPythonWith2Arguments();

    //** test c call python function with image
    testCCallPythonWith1Image();
    return 0;
}