# Getting Started

## Try the Samples

The best way to get started with the OpenUSD Exchange SDK is to try out the OpenUSD Exchange Samples. These are simple applications that showcase many features and key concepts of the SDK.

You can execute the samples to try them out, learn from their source code, and modify them to experiment with OpenUSD and the OpenUSD Exchange SDK for yourself.

### Get the Samples

The OpenUSD Exchange Samples are available on [GitHub](https://github.com/NVIDIA-Omniverse/usd-exchange-samples). You can clone the repository or download the source as a zip file.

### Build

To try the samples you will need to build them from source. The included build scripts make it easy.
``````{card}

`````{tab-set}

````{tab-item} Linux
:sync: linux

This project requires "make" and "g++".

1. Open a terminal.
2. To obtain "make" type `sudo apt install make` (Ubuntu/Debian), or `yum install make` (CentOS/RHEL).
3. For "g++" type `sudo apt install g++` (Ubuntu/Debian), or `yum install gcc-c++` (CentOS/RHEL).
4. Use the provided build script to download all other dependencies (e.g OpenUSD), create the Makefiles, and compile the code:
    ```bash
    ./repo.sh build
    ```
````

````{tab-item} Windows
:sync: windows

This project requires Microsoft Visual Studio 2019 or newer.

1. Download & install [Visual Studio with C++](https://visualstudio.microsoft.com/vs/features/cplusplus).
2. Use the provided build script to download all dependencies (e.g OpenUSD), create the projects, and compile the code:
```bash
.\repo.bat build
```
````

`````

``````

### Run

Once you have built the samples, you can run their executables to try them. All of the compiled samples are executed with a `run` script with the
program name as the first argument. There are many samples under the `source` folder, like `createStage`, `createLights`, `createTransforms`, etc.

``````{card}
`````{tab-set}

````{tab-item} Linux
:sync: linux

Use the `run.sh` script (e.g. `./run.sh createStage`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`
```bash
./run.sh createStage --help
```

Use the `python.sh` script (e.g. `./python.sh source/createStage/createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`
```bash
./python.sh source/createStage/createStage.py --help
```

Use the `--help` flag for each of the sample executables to learn more about the optional arguments that they accept. (e.g. `./run.sh createStage --help`)

````

````{tab-item} Windows
:sync: windows

Use the `run.bat` script (e.g. `.\run.bat createStage`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\run.bat createStage --help
```

Use the `python.bat` script (e.g. `.\python.bat source\createStage\createStage.py`) to execute each program with a pre-configured environment.

For command line argument help, use `--help`

```bash
.\python.bat source\createStage\createStage.py --help
```

Use the `--help` flag for each of the sample executables to learn more about the optional arguments that they accept. (e.g. `.\run.bat createStage --help`)
````

`````
``````

See also the [OpenUSD Exchange Samples README](https://github.com/NVIDIA-Omniverse/usd-exchange-samples) for more detailed descriptions and documentation about the individual samples.

### Experiment

Once you have oriented yourself with the samples that interest you, try modifying the source code in the `source/` directory of the repository to experiment with the SDK. Once you've made your change, just repeat the **Build** and **Run** steps in this guide and test out your change.

Proceed to the next section to learn how to start building your own application to convert data to OpenUSD.

## Integrate into an Application

The next step to familiarize yourself with the OpenUSD Exchange SDK is to create a simple standalone application.

This section will teach you how to create an application that opens a `UsdStage`, reports basic stage configuration details, and lists all of the `UsdPrim` paths.

This walkthrough will use these tokens:
- `$project_root` - the base directory where the project application is located
  - To keep things clean, it is recommended that this is completely separate from either the OpenUSD Exchange SDK or Exchange Samples repo folders
- `$config` - the build configuration (`debug` or `release`)
- `$platform` - the platform (`linux-x86_64` or `windows-x86_64`)

### Install the SDK

 Assembling the minimal requirements for the OpenUSD Exchange SDK can be complicated, so there is an [install_usdex](devtools.md#install_usdex) script that developers run to gather everything into one `_install` folder. This folder can then be copied into the project structure of the developer's application.

Running these commands *from the Sample's root folder* will generate the `_install` folder for both debug and release configurations and deep copy them to wherever the sample project is located.  Note that if running the install script from the Exchange Samples, it is necessary to build them first:

```{eval-rst}
.. tab-set::

    .. tab-item:: Linux
      :sync: linux

        .. code-block:: bash

          ./repo.sh build
          ./repo.sh install_usdex --config release --install-python-libs
          ./repo.sh install_usdex --config debug --install-python-libs
          cp -Lr _install $project_root/usdex

    .. tab-item:: Windows
      :sync: windows

        .. code-block:: batch

          repo.bat build
          repo.bat install_usdex --config release --install-python-libs
          repo.bat install_usdex --config debug --install-python-libs
          robocopy /s _install $project_root\usdex > NUL
```

This tree describes the proposed file layout for the project:

```text
$project_root
│   Makefile or UsdTraverse.sln|vsproj
│   UsdTraverse.cpp
│   ...
└───usdex
    ├───target-deps            <----- build dependencies
    │   ├───omni_transcoding
    │   ├───python
    │   ├───usd
    │   └───usd-exchange
    └───$platform/$config      <----- runtime dependencies
        ├───lib
        └───python
            ├───pxr
            └───usdex
```

```{eval-rst}
.. note::
  The ``install_usdex`` script may be run from either the Exchange Samples or the Exchange SDK root directory, it is provided with both repositories.  If ``repo.bat|sh install_usdex`` is run from within the usd-exchange repository root, there is no need to run ``repo.bat|sh build`` first. The version of OpenUSD Exchange that is downloaded will match the top line of the USD Exchange repository's [CHANGELOG.md](../CHANGELOG.md) if no ``--version`` argument is provided.
```

This `_install` folder will be copied into `$project_root/usdex` for this walkthrough.  Note that the `target-deps` folder contains soft links on Linux and junctions on Windows, so any time it is copied, it requires deep copy commands or options.

For more details on choosing build flavors & features, or different versions of the SDK, see the [install_usdex](devtools.md#install_usdex) documentation.

#### Runtime Dependencies

The `install_usdex` tool will assemble the exact runtime requirements based on the build flavor you have selected, so the easiest approach is to copy the file tree that it generated.

There is some flexibility however. For more thorough details about how to deploy the runtime dependencies for an application or plugin using the OpenUSD Exchange SDK, see the [detailed runtime requirements](./runtime-requirements.md).

### Sample Program

The application performs a few simple things with OpenUSD and the OpenUSD Exchange SDK:

- Expects one argument, the path to a USD stage
  - Acceptable forms:
    - `C:/USD/helloworld.usd` or `/tmp/USD/helloworld.usd` - an absolute path
    - A relative path based on the CWD of the program (`sample.usda`)
  - Open the USD stage
  - Print the stage's up-axis
  - Print the stage's linear units, or "meters per unit" setting
  - Traverse the stage prims and print the path of each one
  - If the prim is `xformable` then print its position

It is included here to copy into a `UsdTraverse.cpp` file within `$project_root`

```cpp
// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: MIT
//

#include <usdex/core/XformAlgo.h>

#include <pxr/usd/usd/primRange.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/xformable.h>

#include <iostream>


// The program expects one argument, a path to a USD file
int main(int argc, char* argv[])
{
    if (argc != 2)
    {
        std::cout << "Please provide a local file path to a USD stage to read." << std::endl;
        return -1;
    }

    std::cout << "OpenUSD Stage Traversal: " << argv[1] << std::endl;

    pxr::UsdStageRefPtr stage = pxr::UsdStage::Open(argv[1]);
    if (!stage)
    {
        std::cout << "Failure to open stage.  Exiting." << std::endl;
        return -2;
    }

    // Print the stage metadata metrics
    std::cout << "Stage up-axis: " << pxr::UsdGeomGetStageUpAxis(stage) << std::endl;
    std::cout << "Meters per unit: " << pxr::UsdGeomGetStageMetersPerUnit(stage) << std::endl;

    // Traverse the stage, print all prim names, print transformable prim positions
    pxr::UsdPrimRange range = stage->Traverse();
    for (const auto& prim : range)
    {
        std::cout << prim.GetPath();

        if (pxr::UsdGeomXformable(prim))
        {
            pxr::GfTransform xform = usdex::core::getLocalTransform(prim);
            std::cout << ":" << xform.GetTranslation();
        }
        std::cout << std::endl;
    }
}
```

### Build Configuration

#### Linux

For Linux, all of the build configuration settings are described in the Makefile included here:

```makefile
# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

# This makefile is a simple example for an application, or converter for including, linking, and executing with
# OpenUSD and the OpenUSD Exchange SDK
#
# By default it will build against the release version of OpenUSD, to build against the debug version run `make CONFIG=debug`.

# The expectation is that OpenUSD, the OpenUSD Exchange SDK, and other dependencies are present in the `$project_root/usdex/target-deps` directory
BOOSTVER = boost-1_78
DEPSDIR = $(CURDIR)/usdex/target-deps
PYTHONVER = python3.10
PROGRAMNAME = UsdTraverse

ifndef CONFIG
	CONFIG=release
endif

ifndef TARGETDIR
	TARGETDIR = $(CURDIR)/$(CONFIG)
endif

# Debug vs. Release differences
ifeq ($(CONFIG),debug)
	CONFIG_DEFINES += -g -DDEBUG -O0 -DTBB_USE_DEBUG=1
else ifeq ($(CONFIG),release)
	CONFIG_DEFINES += -DNDEBUG -O2
endif

# ABI Settings
ifndef ABI_DEFINES
	ABI_DEFINES = -D_GLIBCXX_USE_CXX11_ABI=1 -std=c++17
endif

# Ignored Warnings
ifndef IGNORED_WARNINGS
	IGNORED_WARNINGS = -Wno-deprecated -DTBB_SUPPRESS_DEPRECATED_MESSAGES
endif

# Include search directories
USDEX_INCLUDE_DIRS = \
 -isystem $(DEPSDIR)/usd-exchange/$(CONFIG)/include \
 -isystem $(DEPSDIR)/usd/$(CONFIG)/include \
 -isystem $(DEPSDIR)/usd/$(CONFIG)/include/$(BOOSTVER)

# USD libs (most of these not required, but this is a proper set for a fully featured converter)
USD_LIBS = \
 -lboost_python310 \
 -lusd_ar \
 -lusd_arch \
 -lusd_gf \
 -lusd_js \
 -lusd_kind \
 -lusd_pcp \
 -lusd_plug \
 -lusd_sdf \
 -lusd_tf \
 -lusd_trace \
 -lusd_usd \
 -lusd_usdGeom \
 -lusd_usdLux \
 -lusd_usdShade \
 -lusd_usdUtils \
 -lusd_vt \
 -lusd_work

USDEX_LIBS = \
 -lusdex_core \
 -lomni_transcoding

# Library dependency directories
USDEX_LIB_DIRS = \
 -L$(DEPSDIR)/usd-exchange/$(CONFIG)/lib \
 -L$(DEPSDIR)/omni_transcoding/$(CONFIG)/lib \
 -L$(DEPSDIR)/usd/$(CONFIG)/lib

# Python specifics
ifndef PYTHON_INCLUDE_DIR
	PYTHON_INCLUDE_DIR = -isystem $(DEPSDIR)/python/include/$(PYTHONVER)
endif

ifndef PYTHON_LIB
	PYTHON_LIB = -l$(PYTHONVER)
endif

ifndef PYTHON_LIB_DIR
	PYTHON_LIB_DIR = -L$(DEPSDIR)/python/lib
endif

# Common flags
CXXFLAGS += $(CONFIG_DEFINES) $(ABI_DEFINES) $(IGNORED_WARNINGS) -m64
INCLUDES += $(USDEX_INCLUDE_DIRS) $(PYTHON_INCLUDE_DIR)
LIBS += $(USD_LIBS) $(USDEX_LIBS) $(PYTHON_LIB)
LDFLAGS += $(USDEX_LIB_DIRS) $(PYTHON_LIB_DIR)

OBJS = $(TARGETDIR)/$(PROGRAMNAME).o

# Build Targets

all: $(TARGETDIR)/$(PROGRAMNAME)

# $@ matches the target; $< matches the first dependent
$(TARGETDIR)/$(PROGRAMNAME): $(OBJS)
	echo Linking $(PROGRAMNAME)
	g++ -o $@ $< $(LDFLAGS) $(LIBS)

$(OBJS): $(PROGRAMNAME).cpp | $(TARGETDIR)
	g++ $(INCLUDES) $(CXXFLAGS) -c $< -o $@

$(TARGETDIR):
	@echo Creating $(TARGETDIR)
	@mkdir -p $(TARGETDIR)

clean:
	rm -rf $(TARGETDIR)
```

#### Windows

Create a new Visual Studio 2019 or 2022 project based on the `C++ Console App`, `Empty Project` template and call it `UsdTraverse`.  Make sure that the solution and project files live in `$project_root`.  Add the CPP source that traverses the USD file to the project. All of the settings specified in this section are found by right clicking on the created project and selecting `Properties` from within Visual Studio.

```{eval-rst}
.. note::
  The OpenUSD Exchange Samples include `Visual Studio solution and project files <https://github.com/NVIDIA-Omniverse/usd-exchange-samples/tree/main/source/usdTraverse>`_ with all of the below build configuration settings setup.  Because Visual Studio solutions aren't as portable as Makefiles, your mileage may vary with them and you may need to start from scratch with a new solution.
```

##### Header Include Paths

`VC++ Directories > External Include Directories`
```
usdex/target-deps/usd-exchange/$(CONFIGURATION)/include
usdex/target-deps/python/include
usdex/target-deps/usd/$(CONFIGURATION)/include
usdex/target-deps/usd/$(CONFIGURATION)/include/boost-1_78
```

##### Library Include Paths

`VC++ Directories > Library Directories`
```
usdex/target-deps/usd-exchange/$(CONFIGURATION)/lib
usdex/target-deps/python/libs
usdex/target-deps/usd/$(CONFIGURATION)/lib
```

##### Compiler Flags from Settings
- Windows requires the `/std:c++17` flag, this can be enabled by setting the `C/C++ > Language > C++ Language Standard` to `ISO C++17 Standard`.
- The OpenUSD C++ headers generate many compiler warnings, the `/external:W0` flag will quiet them. Set `C/C++ > External Includes > External Header Warning Level` to `Turn Off All Warnings` (if the include folders were put into the `External Include Directories` list).

##### Preprocessor Definitions

`C/C++ > Preprocessor > Preprocessor Definitions` (all configurations)
```text
BOOST_LIB_TOOLSET="vc142"
NOMINMAX
TBB_SUPPRESS_DEPRECATED_MESSAGES
```

Note: the debug configuration will need to specify to use debug TBB
```text
TBB_USE_DEBUG=1
```

##### Libraries

`Linker > Input > Additional Dependencies` (All configurations)
```text
usdex_core.lib
usd_arch.lib
usd_gf.lib
usd_kind.lib
usd_pcp.lib
usd_plug.lib
usd_sdf.lib
usd_tf.lib
usd_usd.lib
usd_usdGeom.lib
usd_usdLux.lib
usd_usdUtils.lib
usd_vt.lib
usd_ar.lib
```

For the release configuration
```
boost_python310-vc142-mt-x64-1_78.lib
```

For the debug configuration
```
boost_python310-vc142-mt-gd-x64-1_78.lib
```

Each OpenUSD module must be linked by the application separately.  The list above is a subset of all of them, but actually more than what the example requires.  For instance, `usd_usdLux.lib` includes the [UsdLux : USD Lighting Schema](https://openusd.org/release/api/usd_lux_page_front.html), but the example doesn't actually use any of the UsdLux interface.  The developer can trim this library list according to the needs of their application.


##### Debugger Environment

If you want to launch or debug the sample from within Visual Studio, the `PATH` environment variable must be set in the settings:

`Configuration Properties > Debugging` (All configurations)
```
PATH=usdex/windows-x86_64/$(CONFIGURATION)/lib
```

### Runtime Environment

The application must be able to find the shared libraries located in `usdex/$platform/$config/lib`.  These variables should be setup from a launching script, Visual Studio debugger settings, or from within the application itself before using the OpenUSD Exchange Core module.

```{eval-rst}
.. tab-set::

    .. tab-item:: Linux
      :sync: linux

        ``run_usdex_app.sh``

        .. code-block:: bash

            #!/bin/bash

            set -e

            export RUNTIME_PATH=./usdex/linux-x86_64/release
            export LD_LIBRARY_PATH=${RUNTIME_PATH}/lib:${LD_LIBRARY_PATH}

            ./release/UsdTraverse "$@"

    .. tab-item:: Windows
      :sync: windows

        ``run_usdex_app.bat``

        .. code-block:: batch

            @echo off
            setlocal

            set RUNTIME_PATH=usdex/windows-x86_64/release
            set PATH=%RUNTIME_PATH%/lib;%PATH%
            x64\release\UsdTraverse.exe %*
```

```{eval-rst}
.. warning::
  If OpenUSD is installed on your system and its paths are in your ``PATH`` environment variable, the samples may not run correctly.
```

## Testing the Results

It is a good idea to author test data in your source format which you can use during development and for regression testing.

Once your data is converted to USD, it is recommended to test it for correctness & compliance with OpenUSD, using a tool like the [Omniverse Asset Validator](./devtools.md#asset-validator). It is a Python module & CLI which you can use to run a suite of validation rules that check for common USD authoring mistakes.

```{eval-rst}
.. note::
  While the Asset Validator was developed as a part of Omniverse, Kit is not required to use it. You can see example uses in the `OpenUSD Exchange Samples <https://github.com/NVIDIA-Omniverse/usd-exchange-samples>`__.
```

If you are using Python's [unittest framework](https://docs.python.org/3/library/unittest.html) for your regression testing, consider trying the [`usdex.test` python module](./python-usdex-test.rst) in your test suite. It includes a few `unittest.TestCase` derived classes to simplify some common OpenUSD testing scenarios, including the Asset Validator mentioned above (e.g `self.assertIsValidUsd()`), as well as context managers for asserting OpenUSD and OpenUSD Exchange Diagnostic logs.

If you require C++ testing, consider using [doctest](https://github.com/doctest/doctest) and the [`usdex/test` headers](../api/namespace_usdex__test.rebreather_rst), which provide similar diagnostic log assertions for the doctest framework.

## Debugging

### Diagnostic Logs

OpenUSD provides [diagnostics facilities](https://openusd.org/release/api/page_tf__diagnostic.html) to issue coding errors, runtime errors, warnings and status messages. The OpenUSD Exchange SDK also uses these `TfDiagnostic` messages to relay detailed status, warning, and error conditions the user.

There are functions to activate and configure a specialized "diagnostics delegate" within the SDK detailed in the [Diagnostic Messages group](../api/group__diagnostics.rebreather_rst).

Users may immediately notice that the OpenUSD Exchange SDK function, `usdex::core::createStage()` emits a Status message to `stdout` like:

```text
Status: in saveStage at line 254 of ...\source\core\library\StageAlgo.cpp -- Saving "stage with rootLayer @.../AppData/Local/Temp/usdex/sample.usdc@, sessionLayer @anon:000001927295CA60:sample-session.usda@"
```

One way to filter out these messages is to activate the SDK's diagnostic delegate using `usdex::core::activateDiagnosticsDelegate()`. Once this diagnostics delegate is engaged, the default diagnostics level emitted is "warning", so the "status" messages will be hidden.

### TF_DEBUG Logs

OpenUSD ships with a debug logging feature that prints to `stdout`. You can configure OpenUSD logging using the `TF_DEBUG` environment variable or the `TfDebug` interface. All of the debug message types are available using the [`TfDebug::GetDebugSymbolDescriptions()`](https://openusd.org/release/api/class_tf_debug.html#ac31e63c4d474fd7297df4d1cdac10937) method.

Here are some useful examples that are present in recent USD releases:

```text
AR_RESOLVER_INIT         : Print debug output during asset resolver initialization
PLUG_LOAD                : Plugin loading
PLUG_REGISTRATION        : Plugin registration
USD_CHANGES              : USD change processing
USD_STAGE_LIFETIMES      : USD stage ctor/dtor messages
```

Additionally, OpenUSD Exchange SDK adds its own TF_DEBUG settings:

```text
USDEX_TRANSCODING_ERROR  : Indicates when UsdPrim or UsdProperty name string encoding fails
```

The debug variables can be combined using wildcards to enable multiple symbol messages:

```text
TF_DEBUG=*               : Enable all debug symbols
TF_DEBUG='PLUG_* AR_*'   : Enable debug symbols for all ``PLUG_*`` and ``AR_*`` messages
TF_DEBUG=USDEX_*         : Enable only the debug symbols for OpenUSD Exchange SDK messages
```

### Attaching a Debugger

`TF_DEBUG` can be set to cause a debug break in a debugger when a warning, error, or fatal diagnostic message is emitted.

```text
TF_ATTACH_DEBUGGER_ON_ERROR         : attach/stop in a debugger for all errors
TF_ATTACH_DEBUGGER_ON_FATAL_ERROR   : attach/stop in a debugger for fatal errors
TF_ATTACH_DEBUGGER_ON_WARNING       : attach/stop in a debugger for all warnings
```

To debug break in any of these while a debugger is attached to the process:

```text
TF_DEBUG=TF_ATTACH_DEBUGGER*
```

[ARCH_DEBUGGER_TRAP/ArchDebuggerTrap()](https://openusd.org/release/api/debugger_8h.html#ad9fc0e50dd7ec1d9636c7e1222a321be) is a direct way to break if a debugger is attached from within application code.
