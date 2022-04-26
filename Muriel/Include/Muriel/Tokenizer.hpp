#pragma once
#include "Muriel/Utils.hpp"
#include "Muriel/Types.hpp"

namespace Muriel
{

    class Tokenizer
    {
    private:
        Tokenizer(const Tokenizer&) = default;
        ~Tokenizer() = default;

        static std::vector<Token> ParseTokens(std::string contents);

    public:
        static void Tokenize(Context* context);
    };

}