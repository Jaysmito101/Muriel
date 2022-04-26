#pragma once

#include <string>
#include <vector>
#include <filesystem>
#include <functional>
#include <unordered_map>

#define MURIEL_ARRAY_SIZE(array) (sizeof(array) / sizeof(array[0]))

namespace Muriel
{

    enum MessageType
    {
        MessageType_Info,
        MessageType_Warning,
        MessageType_Error
    };

    struct Message
    {
        uint32_t line;
        std::string message;
        MessageType type;

        Message(uint32_t line, const std::string& message, MessageType type)
            : line(line), message(message), type(type)
        { }
    };

    enum TokenType
    {
        TokenType_None = 0,
        TokenType_Whitespace,
        TokenType_Number,
        TokenType_String,
        TokenType_Character,
        TokenType_Operator,
        TokenType_Keyword,
        TokenType_Separator
    };

    struct Token
    {
        std::string value = "";
        TokenType type = TokenType_None;
        uint32_t line = 0;        
    };


    struct Context
    {
        /*
        * The Preprocessor will work with the following
        */
        std::string sourcePath = "";
        std::vector<std::string> includePaths;
        std::string preprocessedOutput = "";
        std::unordered_map<std::string, std::string> macros;
        std::function<std::string(const std::string&)> ReadFileFunc;
        std::function<std::vector<std::string>(const std::string&)> ListFilesInDirectoryFunc;
        std::function<bool(const std::string&)> FileExistsFunc;

        /*
        * Tokenizer will work with the following
        */
        std::vector<Token> tokens;

        /*
        * For general use
        */
        std::vector<Message> messages;

        /*
        * To be used by CodeGenerator
        */
        std::string outputPath = "a.c";        
    };

}