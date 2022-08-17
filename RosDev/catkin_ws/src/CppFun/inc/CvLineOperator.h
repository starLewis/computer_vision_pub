//
// Created by liuxun on 18-1-13.
//

#ifndef CVFUN_CVLINEOPERATOR_H
#define CVFUN_CVLINEOPERATOR_H

#include <math.h>
#include <iostream>
#include <vector>

namespace wicv{
#define UNKNOWNPARAM 1<<20
#define PI 3.1415924
#define ABS(a) (((a)>0?(a):(-(a))))
#define MINDIS 0.0001
#define DEGREE90TORADIANS 1.570796327
#define DEGREE0TORADIANS 0
#define DEGREE5TORADIANS 0.0872664626
    static float DegreeToRadian[90] = {};	//for mapping

    enum ReturnStatus
    {
        RETURN_OK = 0,
        RETURN_ERROR_INPUT = 1,
        RETURN_ERROR_CANNOTGETPOINT = 2,

        RETURN_MAXNUM,
    };

    class Point
    {
    public:
        float x;
        float y;

        Point() { x = 0; y = 0; };
        Point(float _x, float _y) { x = _x; y = _y; };
    };

    //** line: a*x + b*y + c = 0;
    class Line
    {
    public:
        //** ax+by+c = 0;
        float a;
        float b;
        float c;

        Line() { a = 0; b = 0; c = 0; };
        Line(float _a, float _b, float _c) { a = _a; b = -b; c = _c; }
    };

    //** Kernel of line operator
    class CvLineOperator
    {
    public:
        CvLineOperator();
        ~CvLineOperator();

        static float GetValueOfLineFunction(Point &p1, Line &l1);
        static float GetValueOfLineFunction(Point &p1, Point &lineP1, Point &lineP2);
        static float GetDistance(Point &p1, Point &p2);
        static float GetDistance(Line &l1, Line &l2);
        static float GetDistance(Point &p1, Line &l1);
        static Point GetMiddlePoint(Point &p1, Point &p2);
        static Line GetLineOfTwoPoints(Point &p1, Point &p2);
        static Line GetLineOfVxyXY0(float vx, float vy, float x0, float y0);
        static int GetPointInLine(Line &l1, float &x, float &y, Point &p1);
        static float GetRadiansOfLine(Line &l1);
        static float GetRadiansOfTwoPoints(Point &p1, Point &p2);
        static float GetRadianOfDegree(float d);
        static float GetDegreesOfRadian(float &r);
        static bool IsPointBetweenTwoParallelLines(Point p1, Line l1, Line l2);
        static Line GetNormalLineOfTwoPoints(Point &p1, Point &p2);
        static int GetNodeOfTwoLines(Line &l1, Line &l2, Point &pRes);

        //** rotate point
        static Point GetPointAfterWRadiansRotate(Point& p1, float w);

        //** Normal linePoint Node of one line
        static int GetNodeOfNormalLineFrom00ToLine(Line &l1, Point &pRes);

        //** Normal line of one point to (0,0)
        static Line GetNormalLineOfPointTo00(Point &p1);

        static Line GetLineAfterWRadiansRotate(Line &l1, float &w);

        //** move line (xOffset, yOffset) to another line
        static Line GetLineAfterMovedXY(Line &l1, float offsetX, float offsetY);
        static Line GetLineAfterMovedXY(Line &l1, Point &offset);

        //** w angle from line1 to line2
        static float GetWRadiansAngleFromL1ToL2(Line &l1, Line &l2);
        static float GetWRadiansAngleBetweenL1L2(Line &l1, Line &l2);

        //** get Offset(offsetx,offsety) from Parallel l1 to Parallel l2
        static Point GetOffsetPointFromParallelL1ToL2(Line &l1, Line &l2);

        //** get the nodes one line crossing edges of image
        static int GetTwoPointsOneLineCrossingOnImage(Line &l1, int imageWidth, int imageHeight, Point &p1, Point &p2);

        //** get two points besides one line and has D Distance from the line
        static int GetTwoPointsBesidesOneLine(Point &linePt1, Point &linePt2, int distance, Point &p1, Point &p2);

        //** get all points from the line
        static std::vector<wicv::Point> GetAllPointsOnLine(Point& startPoint, Point& endPoint);

    };

}

#endif //CVFUN_CVLINEOPERATOR_H
