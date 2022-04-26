#include "Muriel/Utils.hpp"

// headers for time
#include <ctime>

namespace Muriel
{

    namespace Utils
    {

        std::string GetFileDirectory(std::string filePath)
        {
            std::string directory = filePath;
            size_t lastSlash = directory.find_last_of("/\\");
            if(lastSlash != std::string::npos)
            {
                directory = directory.substr(0, lastSlash);
            }
            return directory;
        }

        bool StartsWith(std::string str, std::string prefix)
        {
            return str.substr(0, prefix.size()) == prefix;
        }

        std::vector<std::string> Split(std::string str, std::string delimiter)
        {
            std::vector<std::string> output;
            size_t pos = 0;
            std::string token;
            while((pos = str.find(delimiter)) != std::string::npos)
            {
                token = str.substr(0, pos);
                output.push_back(token);
                str.erase(0, pos + delimiter.length());
            }
            return output;
        }

        std::string Trim(std::string str)
        {
            std::string output = str;
            size_t first = output.find_first_not_of(" \t\r\n");
            size_t last = output.find_last_not_of(" \t\r\n");
            if(first != std::string::npos && last != std::string::npos)
            {
                output = output.substr(first, last - first + 1);
            }
            return output;
        }

        std::string ReadFile(const std::string& filePath)
        {
            std::stringstream buffer;
            try{
                std::ifstream file(filePath);
                buffer << file.rdbuf();
            }
            catch(std::exception& e)
            {
                return "[ERROR]";
            }
            return buffer.str();
        }

        std::string Replace(std::string str, std::string from, std::string to)
        {
            std::string output = str;
            size_t pos = 0;
            while((pos = output.find(from, pos)) != std::string::npos)
            {
                output.replace(pos, from.length(), to);
                pos += to.length();
            }
            return output;
        }

        bool FileExisits(const std::string& filePath)
        {
            std::ifstream file(filePath);
            bool exisits = file.good();
            file.close();
            return exisits;
        }

        std::string GetTimeStr()
        {
            time_t rawtime;
            struct tm * timeinfo;
            char buffer[80];

            time(&rawtime);
            timeinfo = localtime(&rawtime);

            strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", timeinfo);
            std::string str(buffer);
            return str;
        }

        bool WriteFile(std::string filePath, std::string contents)
        {
            std::ofstream file(filePath);
            if(file.is_open())
            {
                file << contents;
                file.close();
                return true;
            }
            return false;
        }

        std::vector<std::string> ListFilesInDirectory(const std::string& directory)
        {
            std::vector<std::string> files;
            for(const auto& entry : std::filesystem::directory_iterator(directory))
            {
                if(entry.is_regular_file())
                {
                    files.push_back(entry.path().string());
                }
            }
            return files;
        }

        void SetupContextDefaults(Context* context)
        {
            context->includePaths.clear();
            context->includePaths.push_back(".");

            context->sourcePath = "";
            context->outputPath = "a.c";
            
            context->preprocessedOutput = "";
            
            context->messages.clear();

            context->ReadFileFunc = [](const std::string& filePath)
            {
                return ReadFile(filePath);
            };

            context->ListFilesInDirectoryFunc = [](const std::string& directory)
            {
                return ListFilesInDirectory(directory);
            };            

            context->FileExistsFunc = [](const std::string& filePath)
            {
                return FileExisits(filePath);
            };
        }

        std::string ToString(TokenType type)
        {
            switch(type)
            {
                case TokenType::TokenType_None         :   return "None";  
                case TokenType::TokenType_Whitespace   :   return "Whitespace";
                case TokenType::TokenType_Number       :   return "Number";  
                case TokenType::TokenType_String       :   return "String";  
                case TokenType::TokenType_Character    :   return "Character";      
                case TokenType::TokenType_Operator     :   return "Operator";      
                case TokenType::TokenType_Keyword      :   return "Keyword";  
                case TokenType::TokenType_Separator    :   return "Separator";      
                default                                :   return "Unknown";
            }
        }

        std::string ToString(Token token)
        {
            std::stringstream ss;
            ss << "[" << ToString(token.type) << "]\t\t" << token.value;
            return ss.str();
        }

    }

}