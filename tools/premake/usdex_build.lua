local m = {} -- The main module table

repo_build = require("omni/repo/build")
repo_build.setup_options()

-- Setup build flavor options

include("usdex_options")
print("[usdex_build (lua)] Building with usd_flavor="..USD_FLAVOR.." and usd_ver="..USD_VERSION.." and python_ver="..PYTHON_VERSION)

-- Common Global Variables

client = not usdex

target_build_dir = target_build_dir or repo_build.target_dir()
target_bin_dir = target_bin_dir or target_build_dir.."/bin"
target_lib_dir = target_lib_dir or target_build_dir.."/lib"
target_python_dir = target_python_dir or target_build_dir.."/python"
target_deps = target_deps or repo_build.target_deps_dir()

-- note this variable only affects Linux builds
python_version_suffix = PYTHON_VERSION

-- Workspace Helpers

-- Configure workspace defaults.
-- This function will set up the premake workspace to add standard platforms and configurations.
-- The args match `repo_build.setup_workspace()`, but the defaults are changed in some cases.
function m.setup_workspace(args)
    print("[usdex_build (lua)] workspace setup")

    local args = args or {}

    repo_build.setup_workspace({
        windows_x86_64_enabled = args.windows_x86_64_enabled or true,
        linux_x86_64_enabled = args.linux_x86_64_enabled or true,
        linux_aarch64_enabled = args.linux_aarch64_enabled or false,
        macos_universal_enabled = args.macos_universal_enabled or false,
        msvc_version = args.msvc_version or "14.29.30133",
        winsdk_version = args.winsdk_version or "10.0.20348.0",
        copy_windows_debug_libs = args.copy_windows_debug_libs or false,
        allow_undefined_symbols_linux = args.allow_undefined_symbols_linux or true,
        extra_warnings = args.extra_warnings or true,
        security_hardening = args.security_hardening or false,
        fix_cpp_version = true,
    })

    repo_build.enable_vstudio_sourcelink()
    repo_build.remove_vstudio_jmc()

    exceptionhandling "On"
    rtti "On"

    filter { "configurations:debug" }
        defines { "TBB_USE_DEBUG=1" }
    filter {}

    filter { "system:windows" }
        defines { "NOMINMAX" }
    filter { "system:linux" }
        buildoptions { "-fvisibility=hidden", "-fdiagnostics-color", "-Wno-deprecated" }
    filter {}

    flags { "ShadowedVariables" }
end

-- Common Buildable Artifacts

-- Create a C++ shared library project
-- @param library_name: The base file name for the compiled binary target
-- @param headers: A list of header files to add to the project
-- @param sources: A list of source files to add to the project
function m.shared_library(options)
    kind "SharedLib"
    m.__library(options)
end

-- Create a C++ static library project
-- @param library_name: The base file name for the compiled binary target
-- @param headers: A list of header files to add to the project
-- @param sources: A list of source files to add to the project
function m.static_library(options)
    kind "StaticLib"
    m.__library(options)
end

function m.__library(options)
    -- check options
    if type(options.library_name) ~= "string" then
        error("`library_name` must be specified")
    end

    local library_name = options.library_name
    local headers = options.headers or {}
    local sources = options.sources or {}

    language "C++"
    defines { library_name.."_EXPORTS" }
    location (repo_build.workspace_dir().."/"..library_name)
    includedirs { "include" }
    libdirs { target_lib_dir }
    files { headers, sources }
    filter { "system:windows" }
        if os.isfile("version.rc") then
            files{ "version.rc" }
        end
    filter {}
    targetdir(target_lib_dir)
    targetname(library_name)

end

-- Create a C++ executable ConsoleApp project
-- @param name: The base file name for the compiled binary target
-- @param headers: A list of header files to add to the project
-- @param sources: A list of source files to add to the project
function m.executable(options)
    -- check options
    if type(options.name) ~= "string" then
        error("`name` must be specified")
    end

    local name = options.name
    local sources = options.sources or {}
    local headers = options.headers or {}

    kind "ConsoleApp"
    language "C++"
    location (repo_build.workspace_dir().."/"..name)
    includedirs { "include" }
    libdirs { target_lib_dir }
    files { headers, sources }
    filter { "system:windows" }
        if os.isfile("version.rc") then
            files{ "version.rc" }
        end
    filter {}
    targetdir(target_bin_dir)
    targetname(name)
end

function m.python_module(options)
    -- check options
    if type(options.module_name) ~= "string" and type(options.bindings_module_name) ~= "string" then
        error("One of `module_name` or `bindings_module_name` must be specified")
    end

    bindings_module_name = options.bindings_module_name
    python_module_name = options.module_name or bindings_module_name:gsub("_", ".")
    module_dir = python_module_name:gsub("%.", "/")
    python_sources = options.python_sources or {}
    bindings_sources = options.bindings_sources or {}

    target_bindings_dir = target_python_dir.."/"..module_dir

    repo_build.prebuild_copy({ python_sources, target_bindings_dir })

    if bindings_sources then

        m.use_pybind()

        defines { "MODULE_NAME="..bindings_module_name }
        includedirs { "include" }
        libdirs { target_lib_dir }
        files { python_sources, bindings_sources }
        targetdir(target_bindings_dir)

        repo_build.define_bindings_python("_"..bindings_module_name, target_deps.."/python", PYTHON_VERSION)

        -- its unclear why repo_build adds "-Wl,--no-undefined", but we don't want it
        -- or we'd have to explicitly link every upstream dependency
        removelinkoptions { "-Wl,--no-undefined" }

        -- this causes a compiliation error in the tbb headers... its doing something for pybind11, but
        -- its not clear what we're losing by removing this, nor how to avoid the tbb issue otherwise.
        removedefines {"_DEBUG"}

    end

end

-- usd-exchange artifacts

function m.use_usdex_core()
    m.use_omni_transcoding()
    links { "usdex_core" }

    if client == true then
        usdex_path = target_deps.."/usdex"
        usdex_build_path = usdex_path.."/%{cfg.buildcfg}"
        externalincludedirs { usdex_build_path.."/include" }
        syslibdirs { usdex_build_path.."/lib" }
    end
end

-- Common Dependencies

function m.with_python()
    return PYTHON_VERSION ~= "0"
end

function m.use_pybind()
    externalincludedirs { target_deps.."/pybind11/include" }
end

function m.use_python()
    python_folder = target_deps.."/python"

    filter { "system:windows" }
        externalincludedirs { python_folder.."/include" }
        syslibdirs { python_folder.."/libs" }
    filter { "system:linux" }
        externalincludedirs { python_folder.."/include/python"..python_version_suffix }
        syslibdirs { python_folder.."/lib" }
        links { "python"..python_version_suffix }
    filter {}
end

function m.use_fmt()
    externalincludedirs { target_deps.."/fmt/include" }
    files { target_deps.."/fmt/src/*.cc" }
end

function m.use_cxxopts()
    externalincludedirs { target_deps.."/cxxopts/include" }
end

function m.use_doctest()
    externalincludedirs { target_deps.."/doctest/include" }
    filter { "system:windows" }
        disablewarnings {
            "4805", -- '==': unsafe mix of type 'const bool' and type 'const R' in operation
        }
    filter {}
end

function m.use_usd(libs)
    usd_path = target_deps.."/usd/%{cfg.buildcfg}"
    usd_lib_path = "\""..usd_path.."/lib".."\""
    externalincludedirs { usd_path.."/include" }
    syslibdirs { usd_lib_path }

    -- Some USD packages list boost headers in a subdirectory, so we need to locate them.
    -- We can't use the buildcfg token as it will not resolve "on the fly" to drive logic.
    boost_headers = os.matchdirs(target_deps.."/usd/*/include/boost-*")
    if #boost_headers > 0 then
        externalincludedirs { boost_headers[1] }
    end

    -- On Windows the vc runtime version is embedded in the boost lib suffix, and we need
    -- to extract it and set BOOST_LIB_TOOLSET in order to compile accordingly. We don't
    -- directly link to any boost libs, but MSVC still complains if these are mismatched.
    if os.target() == "windows" then
        boost_lib = os.matchfiles(target_deps.."/usd/*/lib/boost*.dll")[1]
        if boost_lib ~= nil then
            vc_version = string.explode(boost_lib:match("(.*).dll"):match("vc(.*)"), "-")[1]
            defines { "BOOST_LIB_TOOLSET=\"vc"..vc_version.."\"" }
        end
    end

    -- Suppress deprecated tbb/atomic.h and tbb/task.h warnings from OpenUSD
    defines { "TBB_SUPPRESS_DEPRECATED_MESSAGES" }

    -- For Houdini build
    local houdini_build = USD_VERSION:match("houdini-(.*)") ~= nil

    if houdini_build then
        boost_headers = os.matchdirs(target_deps.."/usd/*/include/hboost*")
        if #boost_headers > 0 then
            externalincludedirs { boost_headers[1] }
        end

        -- Disable automatic linking of boost libraries on Windows
        -- To avoid missing hboost_python*-*-mt-gd-x64-1_72.lib error.
        defines { "HBOOST_ALL_NO_LIB" }
        defines { "OMNICONNECTCORE_WITH_HOUDINI" }
    end

    -- We need to determine the correct PXR_LIB_PREFIX in order to link to the USD libraries.
    -- Note monolithic builds necessarily ignore the supplied `libs` argument and force linking
    -- to the mono library.
    if libs then
        -- we can't use the buildcfg token as it will not resolve "on the fly" to drive logic
        usd_lib_dirs = os.matchdirs(target_deps.."/usd/*/lib")
        if #usd_lib_dirs == 0 then
            error("The USD library path must exist on local disk")
        end
        usd_lib_dir = usd_lib_dirs[1]

        -- check if we have a monolithic build of USD
        monolithic = os.matchfiles(usd_lib_dir.."/*usd_ms.*")
        if #monolithic > 0 then
            -- there is only one library to link
            usd_lib_name = path.replaceextension(path.getbasename(monolithic[1]), "")
            if os.target() ~= "windows" and string.startswith(usd_lib_name, "lib") then
                usd_lib_name = usd_lib_name:sub(4)
            end
            links { usd_lib_name }
        else
            regular = os.matchfiles(usd_lib_dir.."/*usdGeom.*")
            if #regular == 0 then
                error("No USD libraries found at "..usd_lib_dir)
            end
            usd_lib_name = path.replaceextension(path.getbasename(regular[1]), "")
            usd_lib_prefix = string.sub(usd_lib_name, 0, string.findlast(usd_lib_name, "usd") - 1)
            -- strip off the leading "lib" except on Windows where it can be added intentionally
            if os.target() ~= "windows" and string.startswith(usd_lib_prefix, "lib") then
                usd_lib_prefix = string.sub(usd_lib_prefix, 4)
            end
            for _, lib in ipairs(libs) do
                links { usd_lib_prefix..lib }
            end
        end
    end

    if m.with_python() then
        -- this is required because of a boost::python build issue on Linux
        m.use_python()
        if houdini_build then
            externalincludedirs { usd_path.."/include/python"..python_version_suffix }
            syslibdirs { usd_lib_path }
            links { "hboost_python".._OPTIONS["py-flavor"].."-mt-x64" }
        else
            filter { "system:linux" }
                links { "boost_python"..PYTHON_VERSION:gsub("%.", "")}
            filter {}
        end
    end

    filter { "system:windows" }
        -- Warnings when including nearly any USD header
        disablewarnings {
            "4003", -- not enough arguments for function-like macro invocation
            "4100", -- unreferenced formal parameter
            "4005", -- Hide hundreds of warnings about NOMINMAX redfinition
            "4127", -- conditional expression is constant
            "4201", -- nonstandard extension used: nameless struct/union
            "4305", -- (warning C4305: truncation from 'double' to 'float')
            "4244", -- (warning C4244: conversion from 'double' to 'float')
            "4267", -- (warning C4267: 'return': conversion from 'size_t' to 'int')
            "4275", -- non dll-interface class used as base for dll-interface class
            "4996", -- (warning C4996: deprecated symbols)
        }
        if not m.with_python() then
            disablewarnings {
                "4251", -- struct needs to have dll-interface to be used by clients of class, caused by a bug in pxr::TfSingleton
            }
        end
    filter { "system:linux" }
        linkoptions { "-Wl,-rpath-link,"..repo_build.get_abs_path(usd_lib_path) }
    filter {}
end

function m.use_omni_transcoding()
    omni_transcoding_path = target_deps.."/omni_transcoding/%{cfg.buildcfg}"
    omni_transcoding_lib_path = "\""..omni_transcoding_path.."/lib".."\""
    externalincludedirs { omni_transcoding_path.."/include" }
    syslibdirs { omni_transcoding_lib_path }
    links { "omni_transcoding" }
    filter { "system:linux" }
        linkoptions { "-Wl,-rpath-link,"..repo_build.get_abs_path(omni_transcoding_lib_path) }
    filter {}
end

return m
