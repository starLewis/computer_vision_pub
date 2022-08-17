#include <stdio.h>
#include <iostream>
#define ABS(a) (((a)>0?(a):(-(a))))
float curRoll(float inputDegree);
float get0ToMinus120Degree(float d);

int main()
{
    std::cout<<"Hello world!"<<std::endl;

    int arrSize = 3;
//    float degreeArr[3] = {-33.0576, 27.4756, 87.2824};//, 87.2824};27.4756
    float degreeArr[3] = {30.4524+180, -27.6998, 86.4216};//, 87.2824};27.4756

//    float inputDegree =  27.4756; //-33.0576;
//    float res =curRoll(inputDegree);

    float sumRoll = 0;
    for(int i=0;i<arrSize;i++)
    {
        sumRoll += curRoll(degreeArr[i]);
    }
    sumRoll /= arrSize;
    if(sumRoll > 60)
    {
        sumRoll -= 120;
    }

    std::cout<<"res: "<<sumRoll<<std::endl;

    return 0;
}

float getAbsDegree(float d)
{
    float res = d;
    while(res < 0)
    {
        res += 360;
    }
    while(res >= 360)
    {
        res -= 360;
    }

    return res;
}

float getMaxAbs180Degree(float d)
{
    float res = d;
    while(res <= -180)
    {
        res += 360;
    }
    while(res > 180)
    {
        res -= 360;
    }
    return res;
}

float curRoll(float inputDegree)
{
    //** calculate roll

    float res = 0;

    float a = getAbsDegree(inputDegree);
    float b = getAbsDegree(a+120);
    float c = getAbsDegree(a+240);

//    std::cout<<a<<" "<<b<<" "<<c<<std::endl;

    float aSub = getAbsDegree(a + 90);
    float bSub = getAbsDegree(b + 90);
    float cSub = getAbsDegree(c + 90);

    aSub = get0ToMinus120Degree(aSub);
    bSub = get0ToMinus120Degree(bSub);
    cSub = get0ToMinus120Degree(cSub);

//    std::cout<<aSub<<" "<<bSub<<" "<<cSub<<std::endl;

    if(ABS(aSub) <= ABS(bSub) && ABS(aSub) <= ABS(cSub))
    {
        res = getMaxAbs180Degree(aSub);
    }else if(ABS(bSub) <= ABS(aSub) && ABS(bSub) <= ABS(cSub))
    {
        res = getMaxAbs180Degree(bSub);
    }else if(ABS(cSub) <= ABS(aSub) && ABS(cSub) <= ABS(bSub))
    {
        res = getMaxAbs180Degree(cSub);
    }

    std::cout<<"res: "<< res<<std::endl;

    return res;
}

float get0ToMinus120Degree(float d)
{
    while(d > 0){
        d -= 120;
    }
    while(d <= -120)
    {
        d += 120;
    }
    return d;
}


//** 1. 背光，裂纹；
//** 2. 回扫自动去掉， 处理图像从现在的半自动到全自动；
//** 3.