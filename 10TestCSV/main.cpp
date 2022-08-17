#include <iostream>
#include <fstream>

int main()
{

    std::string autoHeightResFileName = "autoHeightResFileIndex_0.csv";

    std::ifstream in;
    in.open(autoHeightResFileName);
    if(!in.is_open())
    {
        std::ofstream outfile;
        outfile.open(autoHeightResFileName,std::ios::out);

        outfile<<"time"<<","<<"turbineHeight"<<","<<"turbineYaw"<<","<<"turbineRoll"<<std::endl;
        outfile.close();
    }else
    {
        char line[512];
        int n = 0;
        while(!in.eof())
        {
            in.getline(line, 512, '\n');
            n++;
        }
        std::cout<<"line num: "<<n<<std::endl;
        in.close();

        if(n >= 400)
        {
            std::ofstream outfile;
            outfile.open(autoHeightResFileName,std::ios::out);

            outfile<<"time"<<","<<"turbineHeight"<<","<<"turbineYaw"<<","<<"turbineRoll"<<std::endl;
            outfile.close();
        }
    }


    std::string value = "create a new file!";
    std::ofstream outfile;
    outfile.open(autoHeightResFileName,std::ios::app);
    for(int i=0;i<100;i++)
    {
        outfile<<value<<","<<value<<","<<value<<","<<value<<std::endl;
    }
    outfile.close();
    std::cout<<"Hello World!"<<std::endl;

    

    return 0;
}
