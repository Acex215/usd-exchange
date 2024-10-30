# 1.0.0

## Core

### Features

- Added `usdex_core` shared library and `usdex.core` python module, which provide higher-level convenience functions on top of lower-level OpenUSD concepts, so developers can quickly adopt OpenUSD best practices when mapping their native data sources to OpenUSD-legible data models.

## Pybind


### Features

- Added `usdex/pybind`, a header-only cxx utility to enable seamless flow between `pybind11` & `boost_python`.
- Added bindings for all USD types exposed in the public API of the `usdex_core` library
  - Note: A minimal subset of USD types is supported. More types may be added in the future.

## RTX

### Features

- Added `usdex_rtx` shared library and `usdex.rtx` python module, which provide utility functions for creating, editing, and querying `UsdShade` data models which represent MDL Materials and Shaders for use with the RTX Renderer.

## Test

### Features

- Added `usdex.test`, a python module which provides `unittest` based test utilities for validating in-memory OpenUSD data for consistency and correctness.
- Added `usdex/test`, a header-only cxx utility which provides a more minimal set of `doctest` based test utilities.

## Dev Tools

### Features

- Added `install_usdex` tool to download and install precompiled OpenUSD Exchange binaries and all of its runtime dependencies.
  - This tool supports a variety of USD flavors & versions. See `repo install_usdex --help` or the [online docs](devtools.md#install_usdex) for details.
- Vendored `omni.asset_validator` python module for validating that USD Data output is compliant and conforms to expected standards.
  - This can be installed via `repo install_usdex --install-test`

## Documentation

- Added C++ and Python API docs for all public functions and classes.
- Added Getting Started article to help learn about & integrate the SDK into a project.
- Added Authoring USD Data article to briefly introduce each group of functions from `usdex_core` and `usdex_rtx`.
- Added Runtime Requirements article to exhaustively list the files required by our runtime.
- Added Deployment Options article explaining how to approach common deployments (e.g cli, docker container, DCC Plugin)
- Added License Notices article covering OpenUSD Exchange SDK and all its runtime dependencies.
- Added Dev Tools article to explain `install_usdex` and Omni Asset Validator.

## Dependencies

### Runtime Deps

- OpenUSD 24.08 (default), 24.05, 23.11
- Omni Transcoding 1.0.0
- Omni Asset Validator 0.14.2
- pybind 2.11.1

### Dev Tools

- packman 7.24.1
- repo_tools (all matching latest public)
- doctest 2.4.5
- cxxopts 2.2.0
- Premake 5.0.0-beta2
- GCC 11.4.0
- MSVC 2019-16.11
- Python 3.10.15 (default), 3.11.10
