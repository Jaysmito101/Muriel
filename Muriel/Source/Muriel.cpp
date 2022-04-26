#include "Muriel/Muriel.hpp"


// From : https://gist.github.com/Ph0enixKM/5a0d48c440a6dd664d7ae4c807c53008
#ifdef _WIN32


    #include <windows.h>
    void color(std::string color, std::string line, bool newLine = false) {
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        int col = 7;

        if (color == "blue") col = 1;
        else if (color == "green") col = 2;
        else if (color == "cyan") col = 3;
        else if (color == "red") col = 4;
        else if (color == "magenta") col = 5;
        else if (color == "yellow") col = 6;

        SetConsoleTextAttribute(hConsole, col);
        std::cout << line;
        if (newLine) {
            std::cout << std::endl;
        }
        SetConsoleTextAttribute(hConsole, 7);
    }


#else



    void color(std::string color, std::string line, bool newLine = false) {
        std::string col = "\033[0m";

        if (color == "blue") col = "\033[0;34m";
        else if (color == "green") col = "\033[0;32m";
        else if (color == "cyan") col = "\033[0;36m";
        else if (color == "red") col = "\033[0;31m";
        else if (color == "magenta") col = "\033[0;35m";
        else if (color == "yellow") col = "\033[0;33m";

        std::cout << col << line << "\033[0m";
        if (newLine) {
            std::cout << std::endl;
        }
    }


#endif


struct Arguments
{
    std::vector<std::string> includePaths;
    std::string sourcePath = "";
    std::string outputPath = "a.c";
    bool tillPreprocess = false;
    bool tillTokenize = false;
};

static void PrintHelp()
{
    std::cout << "Usage: Muriel [options] <source file>" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  -I<path>  Add a path to the include path" << std::endl;
    std::cout << "  -O<path>  Set the output path" << std::endl;
    std::cout << "  -P        Till Proprocess" << std::endl;
    std::cout << "  -T        Till Tokenize" << std::endl;
    std::cout << "  -h        Print this help" << std::endl;
}

static void ParseArguments(int argc, char** argv, Arguments* args)
{
    args->includePaths.clear();
    args->includePaths.push_back(".");
    for(int i = 1 ; i < argc ; i++)
    {
        if(Muriel::Utils::StartsWith(argv[i], "-I"))
        {
            args->includePaths.push_back(argv[i] + 2);
        }
        else if(Muriel::Utils::StartsWith(argv[i], "-O"))
        {
            args->outputPath = argv[i] + 2;
        }
        else if(Muriel::Utils::StartsWith(argv[i], "-h"))
        {
            PrintHelp();
            exit(0);
        }
        else if(Muriel::Utils::StartsWith(argv[i], "-P"))
        {
            args->tillPreprocess = true;
        }
        else if(Muriel::Utils::StartsWith(argv[i], "-T"))
        {
            args->tillTokenize = true;
        }
        else if(argv[i][0] == '-')
        {
            std::cout << "Unknown argument: " << argv[i] << std::endl;
            exit(-1);
        }
        else
        {
            args->sourcePath = argv[i];
        }
    }
    args->includePaths.push_back(Muriel::Utils::GetFileDirectory(args->sourcePath));
}

static void PrintMessages(Muriel::Context& context)
{
    if(context.messages.size() > 0)
    {
        for(auto& message : context.messages)
        {
            switch(message.type)
            {
                case Muriel::MessageType_Error:
                    color("red", "[ERROR] ");
                    std::cout << message.message << std::endl;
                    break;
                case Muriel::MessageType_Warning:
                    color("yellow", "[WARNING] ");
                    std::cout << message.message << std::endl;
                    break;
                case Muriel::MessageType_Info:
                    color("cyan", "[INFO] ");
                    std::cout << message.message << std::endl;
                    break;
            }
        }
        std::cout << std::endl;
    }
    else
    {
        std::cout << "No messages" << std::endl;
    }
}

int main(int argc, char** argv)
{
    srand(time(NULL));
    Arguments arguments;
    ParseArguments(argc, argv, &arguments);
    if(arguments.sourcePath == "")
    {
        std::cout << "No source file specified" << std::endl;
        PrintHelp();
        return -1;
    }
    Muriel::Context context;
    Muriel::Utils::SetupContextDefaults(&context);
    context.includePaths = arguments.includePaths;
    context.sourcePath = arguments.sourcePath;
    context.outputPath = arguments.outputPath;
    Muriel::Preprocessor::Preprocess(&context);

    if(arguments.tillPreprocess)
    {
        PrintMessages(context);
        std::cout << "Preprocessed file saved to " << (context.outputPath + ".mur") << std::endl;
        Muriel::Utils::WriteFile((context.outputPath + ".mur"), context.preprocessedOutput );
        return 0;
    }


    Muriel::Tokenizer::Tokenize(&context);

    if(arguments.tillTokenize)
    {
        PrintMessages(context);
        std::cout << "Tokenized file saved to " << (context.outputPath + ".txt") << std::endl;
        std::string tokenizedOutput = "";
        for(auto& token : context.tokens)
        {
            tokenizedOutput += Muriel::Utils::ToString(token) + "\n";
        }
        std::cout << tokenizedOutput << std::endl;
        Muriel::Utils::WriteFile((context.outputPath + ".txt"), tokenizedOutput );
        return 0;
    }

    return 0;
}
