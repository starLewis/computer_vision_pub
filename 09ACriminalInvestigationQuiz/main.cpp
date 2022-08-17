#include <iostream>
#include <cstring>
#define MIN(a, b) ((a)<(b)?(a):(b))
using namespace std;


//** 1: A, 2: B, 3: C, 4: D
int A1Set[4] = {0, 1, 2, 3};    //**ABCD
int A2Set[4] = {2, 3, 0, 1};    //**CDAB
int A3Set[4] = {3,6,2,4};
int A4Set[4][2] = {{1,5},{2,7},{1,9},{6,10}};
int A5Set[4] = {8,4,9,7};
int A6Set[4][2] = {{2,4},{1,6},{3,10},{5,9}};
int A7Set[4] = {2, 1, 0, 3};    //**CBAD
int A8Set[4] = {7,5,2,10};
int A9Set[4] = {6,10,2,9};
int A10Set[4] = {3,2,4,1};

int AResult[10]={-1};
int P1(); int P2(); int P3(); int P4(); int P5(); int P6(); int P7(); int P8(); int P9(); int P10();
int (*P[10])() = {P1,P2,P3,P4,P5,P6,P7,P8,P9,P10};

int preNoResSum = 10;
int curNoResSum = 10;

int updateCurPreNoResSum()
{
    int resFunc = 0;

    curNoResSum = 0;
    for(int j=0;j<10;j++)
    {
        if(AResult[j] < 0)
        {
            curNoResSum++;
        }
    }
    if(curNoResSum > preNoResSum)
    {
        resFunc = 1;
    }else if(curNoResSum == preNoResSum)
    {
        resFunc = 0;
    }else if(curNoResSum < preNoResSum)
    {
        resFunc = -1;
    }
    preNoResSum = curNoResSum;

    return resFunc;
}


//
//int P5()
//{
//    for(int i=0;i<4;i++)
//    {
//        AResult[5-1] = i;
//        int resValue = A5Set[i];
//
//        int res = (*P[resValue-1])();
//        int resUpdate = updateCurPreNoResSum();
//
//        if(resUpdate != 0)
//        {
//            i = -1;
//        }
//
//        if(AResult[resValue-1] == i && resUpdate == 0)
//        {
//            return 1;
//        }
//    }
//
//    return -1;
//}

int P4()
{
    for(int i=0;i<4;i++)
    {
        AResult[4-1] = i;
        int resValue01 = A4Set[i][0];
        int resValue02 = A4Set[i][1];
        int resValue01Value = AResult[resValue01-1];
        int resValue02Value = AResult[resValue02-1];

        if(resValue01Value >= 0)
        {
            AResult[resValue02-1] = resValue01Value;

            int resUpdate = updateCurPreNoResSum();

            if(resUpdate == 0)
            {
                return 1;
            }
        }





    }

    return -1;
}

int P7()
{
    for(int i=0;i<4;i++)
    {
        AResult[7-1] = i;

        int minChosedNum = 1<<10;
        int chosedNum[4] = {0};
        memset(chosedNum,0,sizeof(chosedNum));
        for(int j=0;j<10;j++)
        {
            if(AResult[j] >= 0 && AResult[j] < 4)
            {
                chosedNum[AResult[j]]++;
            }
        }

        for(int j=0;j<4;j++)
        {
            minChosedNum = MIN(minChosedNum,chosedNum[j]);
        }

        int resUpdate = updateCurPreNoResSum();
        if(i == minChosedNum && resUpdate == 0)
        {
            return 1;
        }

    }

    return -1;

}

int P8()
{
    for(int i=0;i<4;i++)
    {
        AResult[8-1] = i;  //** A8
        int resValue = A8Set[i];  //** A8 value

        int res = (*P[resValue-1])();
        int resValueValue = AResult[resValue-1];  //** A8 value's value
        int resUpdate = updateCurPreNoResSum();
        if(resUpdate != 0)
        {
            i = -1;
        }

        if(resValueValue>=0 && AResult[0]>=0&&(resValueValue - AResult[0] > 1 || resValueValue - AResult[0] < -1))
        {
            return 1;
        }

    }

    return -1;
}

int P5() //** -> P8, P4, P9, P7
{
    for(int i=0;i<4;i++)
    {
        AResult[5-1] = i;   //** A5
        int resValue = A5Set[i];  //** A5 value
        AResult[resValue-1] = AResult[5 - 1];  //** A5 value's result

        int res = (*P[resValue-1])();
        int resUpdate = updateCurPreNoResSum();
        if(resUpdate != 0)
        {
            i = -1;
        }

        if(res == 1 && resUpdate == 0)
        {
            return 1;
        }

    }

    return -1;
}

int P2()
{
    for(int i=0;i<4;i++)
    {
        AResult[4] = i;

        //** go to P4
        int res = (*P[4-1])();
        int resUpdate = updateCurPreNoResSum();
        if(resUpdate != 0)
        {
            i = -1;
        }

        if(res == 1 && resUpdate == 0)
        {
            return 1;
        }
    }

    return -1;
}

int P1()
{
    for(int i=0;i<4;i++)
    {
        AResult[0] = i;

        //** go to P2
        int res = (*P[2-1])();
        int resUpdate = updateCurPreNoResSum();

        if(resUpdate != 0)
        {
            i = -1;
        }

        if(res == 1 && resUpdate == 0)
        {
            return 1;
        }
    }

    return -1;
}

int main()
{



    return 0;
}
