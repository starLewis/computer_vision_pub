#include <iostream>
#include <opencv2/opencv.hpp>

class videoOperator
{
public:
    videoOperator(){}
    ~videoOperator(){}

    static void readVideoAndStoreFrame(std::string videoPath,std::string storeFrameFolderPath);

    static int readVideoAndCutStoreSubVideo(std::string videoPath,int subVideoFrameBegin, int subVideoFrameEnd);

};

//** function core

//**video read and press "s" to store current frame
void videoOperator::readVideoAndStoreFrame(std::string videoPath, std::string storeFrameFolderPath)
{
    cv::VideoCapture vCap;
    vCap.open(videoPath);
    cv::Mat frameMat;

    //**config
    int skipFrameNum = 100;

    if(!vCap.isOpened())
    {
        std::cout<<"video: "<<videoPath <<" open failed!"<<std::endl;
        return;
    }

    int frameSum = vCap.get(CV_CAP_PROP_FRAME_COUNT);
    int frameRate = vCap.get(CV_CAP_PROP_FPS);

    //** build the store image's path
    int findParentIndex = videoPath.rfind("/");
    if(findParentIndex<0)//** don't find '/'
    {
        findParentIndex = 0;
    }else
    {
        findParentIndex++;
    }
    int findDotIndex = videoPath.rfind(".");
    if(findDotIndex<=findParentIndex)
    {
        findDotIndex = findParentIndex;
    }
    std::string frameName = videoPath.substr(findParentIndex,findDotIndex-findParentIndex);
    if(storeFrameFolderPath[storeFrameFolderPath.length()-1]!='/')storeFrameFolderPath+="/";

    int frameIndex = 0;
    while(frameIndex < frameSum)
    {
        frameIndex++;
        std::cout<<"frameIndex: "<<frameIndex<<std::endl;
        vCap.read(frameMat);

        if(frameIndex < skipFrameNum)continue;

        cv::imshow("video",frameMat);

        int key = cv::waitKey(20);
        if(key == 115) //'s' = 115
        {
            std::stringstream ss;
            ss<<"_frame"<<frameIndex<<".jpg";

            cv::imwrite(storeFrameFolderPath+frameName+ss.str(),frameMat);
        }

    }

}

int videoOperator::readVideoAndCutStoreSubVideo(std::string videoPath, int subVideoFrameBegin, int subVideoFrameEnd)
{
    cv::VideoCapture vCap;
    vCap.open(videoPath);

    int storeVideoFrameWidth = 400;
    int storeVideFrameHeight = 224;

    if(!vCap.isOpened())
    {
        std::cout<<"video: "<<videoPath<<" open failed!"<<std::endl;
        return -1;
    }

    int frameSum = vCap.get(CV_CAP_PROP_FRAME_COUNT);
    int frameHeight = vCap.get(CV_CAP_PROP_FRAME_HEIGHT);
    int frameWidth = vCap.get(CV_CAP_PROP_FRAME_WIDTH);
    int frameRate = vCap.get(CV_CAP_PROP_FPS);
    std::cout<<"video frameSum:"<<frameSum<<" frameRate:"<<frameRate<<" Size:("<<frameWidth<<","<<frameHeight<<")"<<std::endl;

    //**video Writer
    cv::VideoWriter vWrt;
    int findDotIndex = videoPath.rfind(".");
    std::string storeVideoPath = videoPath.substr(0,findDotIndex);
    storeVideoPath+="_1.avi";
    vWrt.open(storeVideoPath,CV_FOURCC('M','P','4','2'),frameRate,cv::Size(storeVideoFrameWidth,storeVideFrameHeight));

    if(!vWrt.isOpened())
    {
        std::cout<<"video: "<<storeVideoPath<<" write failed!"<<std::endl;
        return -1;
    }

    if(subVideoFrameEnd>frameSum-1)subVideoFrameEnd = frameSum-1;

    //**read video and store sub video
    int frameIndex = 0;
    cv::Mat frameMat;
    while(frameIndex < frameSum)
    {
        frameIndex++;
        frameIndex++;
        std::cout<<"frameIndex: "<<frameIndex<<std::endl;
        vCap.read(frameMat);
        vCap.read(frameMat);
        cv::Mat resizeMat;
        cv::Rect rect(0,0,storeVideoFrameWidth,storeVideFrameHeight);
        resizeMat = frameMat(rect);
//        cv::imshow("1",resizeMat);
//        cv::waitKey(30);

        if(frameIndex >= subVideoFrameBegin&&frameIndex <= subVideoFrameEnd)
        {
            vWrt.write(resizeMat);

            if(frameIndex == subVideoFrameBegin)
            {
                std::cout<<"*** begin cut video..."<<std::endl;
            }
            if(frameIndex == subVideoFrameEnd)
            {
                std::cout<<"...cut video over ***"<<std::endl;
            }
        }else if(frameIndex == subVideoFrameEnd+1)
        {
            vWrt.release();
        }
    }
    vWrt.release();

    return 0;

}

//**


int main()
{

    std::string videoPath = "/home/lewisliu/Desktop/forKeSir/DJI_0014_fengxian_20171110_resize_middleRes.avi";
    std::string storeFrameFolderPath = "/home/lewisliu/Desktop/forKeSir";

    //** read and store frame by press 's'
    //videoOperator::readVideoAndStoreFrame(videoPath,storeFrameFolderPath);

    //** read and cut store sub video
    videoOperator::readVideoAndCutStoreSubVideo(videoPath,1,2000);

    std::cout<<"Hello World!"<<std::endl;

    return 0;
}

