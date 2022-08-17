//
// Created by liuxun on 18-1-15.
//

#ifndef CPPFUN_CVKEYLINEOPERATOR_H
#define CPPFUN_CVKEYLINEOPERATOR_H

#include <vector>
#include "../inc/CvLineOperator.h"

namespace wicv
{

    //** declare a keyline class
    class MyKeyline {
    public:
        //**orientation of the line
        float angle;

        //** coordinates of the middlepoint
        Point pt;

        //**lines's extremes in original image
        float startPointX;
        float startPointY;
        float endPointX;
        float endPointY;

        //** the length of line
        float lineLength;

        //**the line function
        Line line;

        //** all points in the line
        std::vector<wicv::Point> allPoints;

        Point getStartPoint() const
        {
            return Point(startPointX, startPointY);
        }

        Point getEndPoint() const
        {
            return Point(endPointX, endPointY);
        }

        std::vector<wicv::Point> getAllPoints() const
        {
            return allPoints;
        }

        //** constructor
        MyKeyline()
        {
        }

        //** constructor
        MyKeyline(float _x1, float _y1, float _x2, float _y2)
        {
            startPointX = _x1;
            startPointY = _y1;
            endPointX = _x2;
            endPointY = _y2;

            Point startPoint = getStartPoint();
            Point endPoint = getEndPoint();

            pt = CvLineOperator::GetMiddlePoint(startPoint, endPoint);
            lineLength = CvLineOperator::GetDistance(startPoint, endPoint);

            line = CvLineOperator::GetLineOfTwoPoints(startPoint, endPoint);
            angle = CvLineOperator::GetRadiansOfTwoPoints(startPoint,endPoint);
            allPoints = CvLineOperator::GetAllPointsOnLine(startPoint,endPoint);

        }
    };

    //** Hexagons class
    class Hexagon
    {
    public:
        Hexagon();
        ~Hexagon();

        int addLine(wicv::MyKeyline line);

        //** copy
        void copyTo(Hexagon &hexagon);

        //** clear all lines
        void clear();

        std::vector<wicv::MyKeyline> getAllLines();
        std::vector<wicv::Point> getAllPoints();
    private:
        std::vector<wicv::MyKeyline> lines;
        std::vector<wicv::Point> points;
    };

    class CvKeyLineOperator
    {
    public:
        CvKeyLineOperator();
        ~CvKeyLineOperator();

        //**singleton
        static CvKeyLineOperator* getInstance();

        //** create a hexgon from a line of an image
        static int CreateHexagonBasedOnOneLine(MyKeyline& curKeyLine, int& imageWidth, int& imageHeight, std::vector<Hexagon> &hexagons);

    };
}

#endif //CPPFUN_CVKEYLINEOPERATOR_H
