//
// Created by liuxun on 18-1-20.
//
#include "../inc/CvLineOperator.h"
using namespace wicv;

wicv::CvLineOperator::CvLineOperator()
{

}
wicv::CvLineOperator::~CvLineOperator()
{

}


float wicv::CvLineOperator::GetValueOfLineFunction(Point & p1, wicv::Line & l1)
{
    return l1.a*p1.x + l1.b*p1.y + l1.c;
}

float wicv::CvLineOperator::GetValueOfLineFunction(Point & p1, Point & lineP1, Point & lineP2)
{
    Line l1 = GetLineOfTwoPoints(lineP1, lineP2);
    return GetValueOfLineFunction(p1, l1);
}

float wicv::CvLineOperator::GetDistance(Point &p1, Point &p2)
{
    return sqrtf((p1.x - p2.x)*(p1.x - p2.x) + (p1.y - p2.y)*(p1.y - p2.y));
}

float wicv::CvLineOperator::GetDistance(Line &l1, Line &l2)
{
    return ABS(l1.c - l2.c) / sqrtf(l1.a*l1.a + l1.b*l1.b);
}

float wicv::CvLineOperator::GetDistance(Point &p1, Line &l1)
{
    float res = ABS(l1.a*p1.x + l1.b*p1.y + l1.c);

    return res / sqrtf(l1.a*l1.a + l1.b*l1.b);
}

wicv::Point wicv::CvLineOperator::GetMiddlePoint(Point &p1, Point &p2)
{
    Point PRes;

    PRes.x = (p1.x + p2.x) / 2;
    PRes.y = (p1.y + p2.y) / 2;

    return PRes;
}

wicv::Line wicv::CvLineOperator::GetLineOfTwoPoints(Point &p1, Point &p2)
{
    Line lineRes;

    if (ABS(p1.x - p2.x) < MINDIS)
    {
        lineRes.a = 1;
        lineRes.b = 0;
        lineRes.c = -p1.x;
    }
    else
    {
        lineRes.a = (p1.y - p2.y) / (p1.x - p2.x);
        lineRes.b = -1;
        lineRes.c = p1.y - lineRes.a*p1.x;
    }

    return lineRes;
}

wicv::Line wicv::CvLineOperator::GetLineOfVxyXY0(float vx, float vy, float x0, float y0)
{
    Point p1(x0,y0);
    Point p2(x0,y0);
    p2.x += vx*10;
    p2.y += vy*10;

    std::cout<<"p2: "<<p2.x<<" "<<p2.y<<std::endl;

    return GetLineOfTwoPoints(p1,p2);
}

int wicv::CvLineOperator::GetPointInLine(Line & l1, float & x, float & y, Point & p1)
{
    if (x != UNKNOWNPARAM && y != UNKNOWNPARAM)
    {
        return RETURN_ERROR_INPUT;
    }

    if (x == UNKNOWNPARAM)
    {
        if (ABS(l1.a) <= MINDIS)
        {
            return RETURN_ERROR_CANNOTGETPOINT;
        }
        x = (-l1.c - l1.b*y) / l1.a;
    }
    else if (y == UNKNOWNPARAM)
    {
        if (ABS(l1.b) <= MINDIS)
        {
            return RETURN_ERROR_CANNOTGETPOINT;
        }
        y = (-l1.c - l1.a*x) / l1.b;
    }

    p1.x = x;
    p1.y = y;

    return RETURN_OK;
}

float wicv::CvLineOperator::GetRadiansOfLine(Line & l1)
{
    float y = -l1.a;
    if (ABS(y) <= MINDIS) { y = 0; }
//    std::cout<<"line:"<<l1.a<<" "<<l1.b<<" "<<l1.c<<std::endl;

    float res = atan2f(y,l1.b);
    while(res < 0)
    {
        res += PI;
    }

    while(res > PI)
    {
        res -= PI;
    }
    return res;
}

float wicv::CvLineOperator::GetRadiansOfTwoPoints(Point & p1, Point & p2)
{
    float dy = p2.y-p1.y;
    float dx = p2.x-p1.x;

    return atan2(dy,dx);
}


float wicv::CvLineOperator::GetRadianOfDegree(float d)
{
    while (d > MINDIS)
    {
        d -= 360;
    }
    while (d < MINDIS)
    {
        d += 360;
    }

    return d*PI / 180;
}

float wicv::CvLineOperator::GetDegreesOfRadian(float & r)
{
    return r * 180 / PI;
}

bool wicv::CvLineOperator::IsPointBetweenTwoParallelLines(Point p1, Line l1, Line l2)
{
    float res1 = l1.a*p1.x + l1.b*p1.y + l1.c;
    float res2 = l2.a*p1.x + l2.b*p1.y + l2.c;

    res1 *= res2;
    if (res1 <= MINDIS)
    {
        return true;
    }
    else
    {
        return false;
    }
}

int wicv::CvLineOperator::GetNodeOfTwoLines(Line & l1, Line & l2, Point &pRes)
{
    if (ABS(l1.a - l2.a) <= MINDIS && ABS(l1.b - l2.b) <= MINDIS)
    {
        return RETURN_ERROR_INPUT;
    }

    Point p;

    if (ABS(l1.a*l2.b - l2.a*l1.b) > MINDIS)
    {
        p.x = (l1.b*l2.c - l2.b*l1.c) / (l1.a*l2.b - l2.a*l1.b);

        if (ABS(l1.b) > MINDIS)
        {
            p.y = (-l1.c - l1.a*p.x) / l1.b;
        }
        else if (ABS(l2.b) > MINDIS)
        {
            p.y = (-l2.c - l2.a*p.x) / l2.b;
        }
        else
        {
            p.y = 0;
        }
    }
    else if (ABS(l2.a*l1.b - l1.a*l2.b) > MINDIS)
    {
        p.y = (l1.a*l2.c - l2.a*l1.c) / (l2.a*l1.b - l1.a*l2.b);

        if (ABS(l1.a) > MINDIS)
        {
            p.x = (-l1.c - l1.b*p.y) / l1.a;
        }
        else if (ABS(l2.a) > MINDIS)
        {
            p.x = (-l2.c - l2.b*p.y) / l2.a;
        }
        else
        {
            p.x = 0;
        }
    }
    else
    {
        p.x = 0;
        p.y = 0;

        return RETURN_ERROR_INPUT;
    }

    pRes = p;

    return RETURN_OK;
}


wicv::Point wicv::CvLineOperator::GetPointAfterWRadiansRotate(Point & p1, float w)
{
    float matrix[2][2] = { { cosf(w),-sinf(w) },{ sinf(w),cosf(w) } };

    Point pRes;
    pRes.x = p1.x*matrix[0][0] + p1.y*matrix[0][1];
    pRes.y = p1.x*matrix[1][0] + p1.y*matrix[1][1];

    return pRes;
}

int wicv::CvLineOperator::GetNodeOfNormalLineFrom00ToLine(Line & l1, Point &pRes)
{
    if (ABS(l1.a) <= MINDIS&&ABS(l1.b) <= MINDIS)
    {
        return RETURN_ERROR_INPUT;
    }

    if (ABS(l1.a) <= MINDIS)
    {
        pRes.x = 0;
        pRes.y = -l1.c / l1.b;
    }
    else if (ABS(l1.b) <= MINDIS)
    {
        pRes.x = -l1.c / l1.a;
        pRes.y = 0;
    }
    else
    {
        float l1K = -l1.a / l1.b;
        float normalLineK = -1 / l1K;

        Line normalLine;
        normalLine.a = normalLineK;
        normalLine.b = -1;
        normalLine.c = 0;

        int res = GetNodeOfTwoLines(normalLine, l1, pRes);

        if (res == RETURN_ERROR_INPUT) { return RETURN_ERROR_INPUT; }
    }


    return RETURN_OK;
}

wicv::Line wicv::CvLineOperator::GetNormalLineOfPointTo00(Point & p1)
{
    Line lRes(0, 0, 0);
    Point p0(0, 0);

    Line l1 = GetLineOfTwoPoints(p0, p1);
    Line normalLine(0, 0, 0);

    if (ABS(l1.a) <= MINDIS)
    {
        normalLine.a = 1;
        normalLine.b = 0;
        normalLine.c = -p1.x;
    }
    else if (ABS(l1.b) <= MINDIS)
    {
        normalLine.a = 0;
        normalLine.b = 1;
        normalLine.c = -p1.y;
    }
    else
    {
        float l1K = -l1.a / l1.b;
        float normalLineK = -1 / l1K;
        float normalLineB = p1.y - p1.x*normalLineK;

        normalLine.a = normalLineK;
        normalLine.b = -1;
        normalLine.c = normalLineB;
    }

    return normalLine;
}

wicv::Line wicv::CvLineOperator::GetLineAfterWRadiansRotate(Line & l1, float & w)
{
    Line lRes(0, 0, 0);

    if (ABS(l1.c) <= MINDIS)
    {
        float l1Angle = atan2f(-l1.a, l1.b);
        l1Angle += w;

        float tanF = tanf(l1Angle);
        if (ABS(tanF) <= MINDIS)
        {
            lRes.a = 0;
            lRes.b = 1;
            lRes.c = 0;
        }
        else if (ABS(1 / tanF) <= MINDIS)
        {
            lRes.a = 1;
            lRes.b = 0;
            lRes.c = 0;
        }
        else
        {
            lRes.a = tanF;
            lRes.b = -1;
            lRes.c = 0;
        }
    }
    else
    {
        Point normalNodeFrom00;
        GetNodeOfNormalLineFrom00ToLine(l1, normalNodeFrom00);

        normalNodeFrom00 = GetPointAfterWRadiansRotate(normalNodeFrom00, w);

        lRes = GetNormalLineOfPointTo00(normalNodeFrom00);
    }

    return lRes;
}

wicv::Line wicv::CvLineOperator::GetLineAfterMovedXY(Line & l1, float offsetX, float offsetY)
{
    Line lRes = l1;

    lRes.a = l1.a;
    lRes.b = l1.b;
    lRes.c = -l1.a*offsetX - l1.b*offsetY + l1.c;

    return lRes;
}

wicv::Line wicv::CvLineOperator::GetLineAfterMovedXY(Line & l1, Point & offset)
{
    Line lRes = l1;

    lRes.a = l1.a;
    lRes.b = l1.b;
    lRes.c = -l1.a*offset.x - l1.b*offset.y + l1.c;

    return lRes;
}

float wicv::CvLineOperator::GetWRadiansAngleFromL1ToL2(Line & l1, Line & l2)
{
    float res = atan2f(l1.a*l2.b - l2.a*l1.b, l1.b*l2.b + l1.a*l2.a);

    return res;
}

float wicv::CvLineOperator::GetWRadiansAngleBetweenL1L2(Line & l1, Line & l2)
{
    float l1ToL2 = GetWRadiansAngleFromL1ToL2(l1, l2);

    l1ToL2 = ABS(l1ToL2);

    if (l1ToL2 > DEGREE90TORADIANS)
    {
        l1ToL2 = PI - l1ToL2;
    }

    return l1ToL2;
}

wicv::Point wicv::CvLineOperator::GetOffsetPointFromParallelL1ToL2(Line & l1, Line & l2)
{
    Point offsetP(0, 0);

    if (ABS(l1.a) <= MINDIS)
    {
        offsetP.x = 0;
        offsetP.y = (l1.c - l2.c) / l1.b;
    }
    else if (ABS(l1.b) <= MINDIS)
    {
        offsetP.x = (l1.c - l2.c) / l1.a;
        offsetP.y = 0;
    }
    else
    {
        offsetP.x = (l1.c - l2.c) / l1.a;
        offsetP.y = 0;
    }

    return offsetP;
}

int wicv::CvLineOperator::GetTwoPointsOneLineCrossingOnImage(Line & l1, int imageWidth, int imageHeight, Point & p1, Point & p2)
{
    if (imageWidth <= 0 || imageHeight <= 0 || (ABS(l1.a)<=MINDIS && ABS(l1.b)<=MINDIS))
    {
        return RETURN_ERROR_INPUT;
    }

    int x = 0, y = 0;

    if (ABS(l1.a) <= MINDIS)
    {
        y = -l1.c / l1.b;
        if (y<0 || y>imageHeight)
        {
            return RETURN_ERROR_INPUT;
        }

        p1.x = 0;
        p1.y = y;
        p2.x = imageWidth;
        p2.y = y;
    }
    else if(ABS(l1.b) <= MINDIS)
    {
        x = -l1.c / l1.a;
        if (x < 0 || x > imageWidth)
        {
            return RETURN_ERROR_INPUT;
        }

        p1.x = x;
        p1.y = 0;
        p2.x = x;
        p2.y = imageHeight;

    }
    else
    {
        y = 0;
        x = -l1.c / l1.a;
        if (x<0)
        {
            x = 0;
            y = -l1.c / l1.b;
        }
        else if (x > imageWidth)
        {
            x = imageWidth;
            y = (-l1.c - l1.a*x) / l1.b;
        }
        p1.x = x;
        p1.y = y;

        y = imageHeight;
        x = (-l1.c - l1.b*y) / l1.a;
        if (x < 0)
        {
            x = 0;
            y = -l1.c / l1.b;
        }
        else if (x > imageWidth)
        {
            x = imageWidth;
            y = (-l1.c - l1.a*x) / l1.b;
        }
        p2.x = x;
        p2.y = y;
    }

    if (ABS(p1.x - p2.x)<=MINDIS && ABS(p1.y-p2.y)<=MINDIS)
    {
        return RETURN_ERROR_INPUT;
    }

    return RETURN_OK;
}

int wicv::CvLineOperator::GetTwoPointsBesidesOneLine(Point & linePt1, Point & linePt2, int distance, Point & p1, Point & p2)
{
    float radian = GetRadiansOfTwoPoints(linePt1, linePt2);
    float degree = GetDegreesOfRadian(radian);

    degree = 90 - degree;
    radian = GetRadianOfDegree(degree);

    int xDistance = distance*cosf(radian);
    int yDistance = -distance*sinf(radian);

    Point centerPoint;
    centerPoint.x = (linePt1.x + linePt2.x) / 2;
    centerPoint.y = (linePt1.y + linePt2.y) / 2;

    p1.x = centerPoint.x + xDistance;
    p1.y = centerPoint.y + yDistance;

    p2.x = centerPoint.x - xDistance;
    p2.y = centerPoint.y - yDistance;

    return 0;
}

//** find all points of one line
std::vector<wicv::Point> wicv::CvLineOperator::GetAllPointsOnLine(Point& startPoint, Point& endPoint)
{
    std::vector<wicv::Point> res;

    int x0 = startPoint.x, y0 = startPoint.y;
    int x1 = endPoint.x, y1 = endPoint.y;
    int dx = ABS(x1 - x0), sx = x0 < x1 ? 1 : -1;
    int dy = ABS(y1 - y0), sy = y0 < y1 ? 1 : -1;
    int err = (dx > dy ? dx : -dy)/2, e2;


    for(;;)
    {
        res.push_back(wicv::Point(x0,y0));
        if(x0 == x1 && y0 == y1)break;
        e2 = err;
        if(e2 > -dx)
        {
            err -= dy;
            x0 += sx;
        }
        if(e2 < dy)
        {
            err += dx;
            y0 += sy;
        }
    }

    return res;
}
