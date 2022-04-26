#include "Muriel/Preprocessor.hpp"

namespace Muriel
{

    std::string Preprocessor::PreprocessString(std::string contents, Context* context)
    {
        std::string output = "";
        std::vector<std::string> lines = Utils::Split(contents, "\n");
        int lineNumber = 1;
        bool skipLines = false;
        for(std::string& line : lines)
        {

            if(Utils::StartsWith(line, "#"))
            {
                line = Utils::Trim(line);
                //  Get command name without the arguments
                std::string command = line.substr(1).substr(0, line.substr(1).find_first_of(" "));
                std::string arguments  = line.substr(1).substr(line.substr(1).find_first_of(" ") + 1);
                if(command == "include")
                {
                    std::string filePath = arguments.substr(1, arguments.size() - 2);
                    bool pathExists = false;
                    for(std::string& includePath : context->includePaths)
                    {
                        std::string fullPath = includePath + "/" + filePath;
                        if(context->FileExistsFunc(fullPath))
                        {
                            output += PreprocessString(context->ReadFileFunc(fullPath), context);
                            pathExists = true;
                            break;
                        }
                    }
                    if(!pathExists)
                        context->messages.push_back(Message(lineNumber, "Could not find file \"" + filePath + "\"", MessageType_Error));
                }
                else if(command == "define")
                {
                    std::string macroName = arguments.substr(0, arguments.find_first_of(" "));
                    std::string macroValue = arguments.substr(arguments.find_first_of(" ") + 1);
                    macroValue = PreprocessString(macroValue + "\n", context).substr(0, macroValue.size());
                    // check if macro name is already defined
                    if(context->macros.find(macroName) != context->macros.end())
                    {
                        context->messages.push_back(Message(lineNumber, "Macro \"" + macroName + "\" is already defined", MessageType_Warning));
                    }
                    context->macros[macroName] = macroValue;
                }
                else if(command == "undef")
                {
                    if(context->macros.find(arguments) != context->macros.end())
                    {
                        context->macros.erase(arguments);
                    }
                    else
                    {
                        context->messages.push_back(Message(lineNumber, "Macro \"" + arguments + "\" is not defined", MessageType_Warning));
                    }
                }
                else if(command == "ifdef")
                {
                    std::string macroName = arguments.substr(0, arguments.find_first_of(" "));
                    if(context->macros.find(macroName) == context->macros.end())
                        skipLines = true;
                    else
                        skipLines = false;
                }
                else if(command == "elifdef")
                {
                    std::string macroName = arguments.substr(0, arguments.find_first_of(" "));
                    if(context->macros.find(macroName) == context->macros.end())
                        skipLines = true;
                    else
                        skipLines = false;
                }
                else if(command == "endif")
                {
                    skipLines = false;
                }
            }
            else
            {
                if(!skipLines)
                {
                    context->macros["__LINE__"] = std::to_string(lineNumber);
                    context->macros["__FILE__"] = "";
                    context->macros["__TIME__"] = Utils::GetTimeStr();
                    context->macros["__RANDOM__"] = std::to_string(rand());
                    for(auto& [macroName, macroValue] : context->macros)
                    {
                        line = Utils::Replace(line, "{" + macroName + "}", macroValue);
                    }
                    output += line + "\n";
                }
            }

            lineNumber++;
        }
        return output;
    }


    void Preprocessor::Preprocess(Context* context)
    {
        std::string preprocessedOutput = "";
        std::string source = Utils::ReadFile(context->sourcePath) + "\n";
        if(source == "[ERROR]\n")
        {
            context->messages.push_back(Message(0, "Could not find file \"" + context->sourcePath + "\"", MessageType_Error));
            return;
        }
        preprocessedOutput = PreprocessString(source, context);
        context->preprocessedOutput = preprocessedOutput;
    }

}