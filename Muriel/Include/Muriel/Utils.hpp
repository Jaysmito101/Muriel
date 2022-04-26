#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <fstream>
#include <filesystem>

#include "Muriel/Types.hpp"

namespace Muriel
{

    namespace Utils
    {

        std::string GetFileDirectory(std::string filePath);

        bool StartsWith(std::string str, std::string prefix);

        bool FileExisits(const std::string& filePath);

        std::vector<std::string> Split(std::string str, std::string delimiter);

        std::string Trim(std::string str);

        std::string Replace(std::string str, std::string from, std::string to);

        std::string GetTimeStr();

        std::string ReadFile(const std::string& filePath);

        bool WriteFile(std::string filePath, std::string contents);

        std::vector<std::string> ListFilesInDirectory(const std::string& directory);

        void SetupContextDefaults(Context* context);

        std::string ToString(TokenType type);

        std::string ToString(Token token);

    }

}