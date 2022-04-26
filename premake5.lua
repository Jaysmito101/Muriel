workspace "Muriel"

    startproject "Muriel"
    
    configurations { "Debug", "Release" }
    platforms { "x86", "x64" }
    flags { "MultiProcessorCompile" }

    filter "configurations:Debug"
        defines { "DEBUG" }
        symbols "On"
        optimize "Off"
    
    filter "configurations:Release"
        defines { "NDEBUG" }
        optimize "Full"
        symbols "Off"
    
    filter "configurations:*"

    filter "platforms:x86"
        architecture "x86"
    
    filter "platforms:x64"
        architecture "x86_64"
    
    filter "platforms:*"

    project "Muriel"
        kind "StaticLib"
        language "C++"
        cppdialect "C++17"

        targetdir "bin/%{prj.name}/%{cfg.platform}-%{cfg.buildcfg}"
        objdir "bin/obj/%{prj.name}/%{cfg.platform}-%{cfg.buildcfg}"

        includedirs { "./Muriel/Include", "./Dependencies" }

        files { "./Muriel/Source/**.hpp", "./Muriel/Source/**.cpp" }

        excludes { "./Muriel/Source/Muriel.cpp" }

    project "MurielCLI"
        kind "ConsoleApp"
        language "C++"
        cppdialect "C++17"

        targetdir "bin/%{prj.name}/%{cfg.platform}-%{cfg.buildcfg}"
        objdir "bin/obj/%{prj.name}/%{cfg.platform}-%{cfg.buildcfg}"

        includedirs { "./Muriel/Include", "./Dependencies" }

        files { "./Muriel/Source/**.hpp", "./Muriel/Source/Muriel.cpp" }

        links { "Muriel" }