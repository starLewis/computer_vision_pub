//
// Created by liuxun on 18-1-15.
//
#include "../inc/CvKeyLineOperator.h"

//** class Hexagon
wicv::Hexagon::Hexagon()
{

}

wicv::Hexagon::~Hexagon()
{

}

int wicv::Hexagon::addLine(wicv::MyKeyline line)
{
    this->lines.push_back(line);

    std::vector<wicv::Point> allPointsOfLine = line.getAllPoints();

    this->points.insert(this->points.end(),allPointsOfLine.begin(),allPointsOfLine.end());
}

void wicv::Hexagon::copyTo(Hexagon &hexagon)
{
    hexagon.clear();

    for(int i=0;i<lines.size();i++)
    {
        hexagon.addLine(lines[i]);
    }
}

void wicv::Hexagon::clear()
{
    this->points.clear();
    this->lines.clear();
}

std::vector<wicv::MyKeyline> wicv::Hexagon::getAllLines()
{
    return this->lines;
}

std::vector<wicv::Point> wicv::Hexagon::getAllPoints()
{
    return this->points;
}

//**

//** class CvKeyLineOperator
wicv::CvKeyLineOperator::CvKeyLineOperator()
{

}

wicv::CvKeyLineOperator::~CvKeyLineOperator()
{

}

//** singleton
static wicv::CvKeyLineOperator* instanceClass = NULL;
wicv::CvKeyLineOperator* wicv::CvKeyLineOperator::getInstance()
{
    if(instanceClass == NULL)
    {
        instanceClass = new CvKeyLineOperator();
    }

    return instanceClass;
}

int wicv::CvKeyLineOperator::CreateHexagonBasedOnOneLine(MyKeyline &curKeyLine, int &imageWidth, int &imageHeight,
                                                      std::vector<Hexagon> &hexagons)
{
    //** error
    if(imageWidth <= 0 || imageHeight <= 0)
    {
        std::cout<<"error: "<<__FUNCTION__<<" image size error!"<<std::endl;
        return -1;
    }

    if(curKeyLine.startPointX < 0 || curKeyLine.startPointX >= imageWidth || curKeyLine.startPointY < 0 || curKeyLine.startPointY >= imageHeight ||
       curKeyLine.endPointX < 0 || curKeyLine.endPointX >= imageWidth || curKeyLine.endPointY < 0 || curKeyLine.endPointY >= imageHeight)
    {
        std::cout<<"error: "<<__FUNCTION__<<" input line size error!"<<std::endl;
        return -1;
    }

    //**
    hexagons.clear();
    wicv::Hexagon curHexagon;

    //**hexagon in one side of the curKeyLine;
    wicv::MyKeyline preKeyLine = curKeyLine;
    curHexagon.addLine(preKeyLine);

    int i = 1;
    for(i=1;i<6;i++)
    {
        wicv::Point p0 = preKeyLine.getStartPoint();
        wicv::Point p1 = preKeyLine.getEndPoint();
        int L = preKeyLine.lineLength;
        float angle = preKeyLine.angle;
        angle -= wicv::CvLineOperator::GetRadianOfDegree(60.0);
        p1.x += L*cos(angle);
        p1.y += L*sin(angle);
        p0 = preKeyLine.getEndPoint();

        if(p0.x < 0 || p0.x >= imageWidth || p0.y < 0 || p0.y >= imageHeight || p1.x < 0 || p1.x >= imageWidth || p1.y < 0 || p1.y >= imageHeight)
        {
            break;
        }
        preKeyLine = wicv::MyKeyline(p0.x,p0.y,p1.x,p1.y);
        curHexagon.addLine(preKeyLine);
    }
    if(i >= 6)
    {
        hexagons.push_back(curHexagon);
    }

    //** hexagon in other side of the curKeyLine;
    preKeyLine = wicv::MyKeyline(curKeyLine.endPointX,curKeyLine.endPointY,curKeyLine.startPointX,curKeyLine.startPointY);
    curHexagon.clear();
    curHexagon.addLine(preKeyLine);
    i = 1;
    for(i=1;i<6;i++)
    {
        wicv::Point p0 = preKeyLine.getStartPoint();
        wicv::Point p1 = preKeyLine.getEndPoint();
        int L = preKeyLine.lineLength;
        float angle = preKeyLine.angle;
        angle -= wicv::CvLineOperator::GetRadianOfDegree(60.0);
        p1.x += L*cos(angle);
        p1.y += L*sin(angle);
        p0 = preKeyLine.getEndPoint();
        preKeyLine = wicv::MyKeyline(p0.x,p0.y,p1.x,p1.y);

        if(p0.x < 0 || p0.x >= imageWidth || p0.y < 0 || p0.y >= imageHeight || p1.x < 0 || p1.x >= imageWidth || p1.y < 0 || p1.y >= imageHeight)
        {
            break;
        }
        curHexagon.addLine(preKeyLine);
    }
    if(i >= 6)
    {
        hexagons.push_back(curHexagon);
    }

    return hexagons.size();
}