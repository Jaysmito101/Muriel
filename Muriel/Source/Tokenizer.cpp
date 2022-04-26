#include "Muriel/Tokenizer.hpp"

static const std::string operators = "+-*/%=!<>&|^~?:.";
static const std::string seperators = "{}()[];,\"\'";
static const std::string whitespace = "\t\n\r ";

static bool IsWhitespace(char c)
{
    return std::find(whitespace.begin(), whitespace.end(), c) != whitespace.end();
}

static bool IsSeperator(char c)
{
    return std::find(seperators.begin(), seperators.end(), c) != seperators.end();
}

static bool IsOperator(char c)
{
    return std::find(operators.begin(), operators.end(), c) != operators.end();
}

static bool IsDigit(char c)
{
    return c >= '0' && c <= '9';
}

namespace Muriel
{

    std::vector<Token> Tokenizer::ParseTokens(std::string contents)
    {
        std::vector<Token> tokens;
        std::stringstream stream(contents);
        std::string line;
        uint32_t lineNumber = 0;
        TokenType currentToken = TokenType_None;
        std::string tokenString = "";
        while (std::getline(stream, line))
        {
            lineNumber++;
            for(char c : line)   
            {
                switch (currentToken)
                {
                    case TokenType_Number:
                    {
                        if(IsDigit(c) || c == '.')
                        {
                            tokenString += c;
                        }
                        else
                        {
                            tokens.push_back({ tokenString, currentToken, lineNumber });
                            if(IsOperator(c))
                            {
                                currentToken = TokenType_Operator;
                                tokenString = c;
                                tokens.push_back({ tokenString, currentToken, lineNumber });
                                currentToken = TokenType_None;
                                tokenString = "";
                            }
                            else if (IsSeperator(c))
                            {
                                currentToken = TokenType_Separator;
                                tokenString = c;
                                tokens.push_back({ tokenString, currentToken, lineNumber });
                                currentToken = TokenType_None;
                                tokenString = "";
                            }
                            else
                            {
                                currentToken = TokenType_String;
                                tokenString = "";
                                if(!IsWhitespace(c))
                                    tokenString += c;
                            }
                        }
                        break;
                    }
                    case TokenType_String:
                    {
                        if(IsWhitespace(c))
                        {
                            tokens.push_back({ tokenString, currentToken, lineNumber });
                            currentToken = TokenType_None;
                            tokenString = "";
                        }
                        else
                        {
                            if(IsOperator(c))
                            {
                                tokens.push_back({ tokenString, currentToken, lineNumber });
                                currentToken = TokenType_Operator;
                                tokenString = c;
                                tokens.push_back({ tokenString, currentToken, lineNumber });
                                currentToken = TokenType_None;
                                tokenString = "";
                            }
                            else if (IsSeperator(c))
                            {
                                tokens.push_back({ tokenString, currentToken, lineNumber });
                                currentToken = TokenType_Separator;
                                tokenString = c;
                                tokens.push_back({ tokenString, currentToken, lineNumber });
                                currentToken = TokenType_None;
                                tokenString = "";
                            }
                            else
                            {
                                tokenString += c;
                            }
                        }
                        break;
                    }
                    case TokenType_None:
                    {
                        if(IsDigit(c))
                        {
                            currentToken = TokenType_Number;
                            tokenString += c;
                        }
                        else if(IsOperator(c))
                        {
                            currentToken = TokenType_Operator;
                            tokenString = c;
                            tokens.push_back({ tokenString, currentToken, lineNumber });
                            currentToken = TokenType_None;
                            tokenString = "";
                        }
                        else if(IsSeperator(c))
                        {
                            currentToken = TokenType_Separator;
                            tokenString = c;
                            tokens.push_back({ tokenString, currentToken, lineNumber });
                            currentToken = TokenType_None;
                            tokenString = "";
                        }
                        else if(IsWhitespace(c))
                        {

                        }
                        else
                        {
                            currentToken = TokenType_String;
                            tokenString += c;
                        }

                        break;
                    }
                }
            }
            if(currentToken != TokenType_None)
            {
                tokens.push_back({ tokenString, currentToken, lineNumber });
            }
        }
        
        return tokens;
    }

    void Tokenizer::Tokenize(Context* context)
    {
        context->tokens = ParseTokens(context->preprocessedOutput);
    }
}