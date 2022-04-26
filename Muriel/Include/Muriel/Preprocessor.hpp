#pragma once

#include "Muriel/Utils.hpp"
#include "Muriel/Types.hpp"

namespace Muriel
{

    class Preprocessor
    {
    private:
        Preprocessor() = default;
        ~Preprocessor() = default;

        /*
        * Preprocess the string
        */
        static std::string PreprocessString(std::string contents, Context* context);

    public:
        static void Preprocess(Context* context);
    };

}