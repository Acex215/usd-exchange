# OpenUSD Exchange SDK

# Overview

[OpenUSD Exchange SDK](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk) accelerates [OpenUSD](https://openusd.org) adoption by helping developers design and develop their own USD I/O solutions that produce consistent and correct USD assets across diverse 3D ecosystems.

It provides higher-level convenience functions on top of lower-level USD concepts, so developers can quickly adopt OpenUSD best practices when mapping their native data sources to OpenUSD-legible data models.

# Get Started

To start using OpenUSD Exchange SDK see the [Getting Started](docs/getting-started.md) guide.

## Downloading or Building

We provide precompiled binaries of the OpenUSD Exchange SDK, as well as all dependencies required to compile, link, and run a program that uses the OpenUSD Exchange libraries and modules. Additionally, OpenUSD Exchange SDK is source available and is licensed for modification & re-distribution (see our [License Notices](docs/licenses.md)).

To download the precompiled OpenUSD Exchange SDK binaries and all the necessary dependencies:
  - Download or clone the [OpenUSD Exchange SDK repository](https://github.com/NVIDIA-Omniverse/usd-exchange)
  - Navigate to your local `usd-exchange` directory
  - Run `./repo.sh install_usdex` or `.\repo.bat install_usdex` to download & assemble the OpenUSD Exchange SDK runtime requirements into a dedicated folder.

For more details on choosing build flavors & features, or different versions of the SDK, see the [install_usdex](docs/devtools.md#install_usdex) tool documentation.

If you would like to modify it, or build it against your own OpenUSD distribution, see [CONTRIBUTING.md](https://github.com/NVIDIA-Omniverse/usd-exchange/blob/main/CONTRIBUTING.md#building) to learn about building from source.

# Contribution Guidelines

We are not currently accepting code contributions to OpenUSD Exchange SDK directly. See [CONTRIBUTING.md](https://github.com/NVIDIA-Omniverse/usd-exchange/blob/main/CONTRIBUTING.md) to learn about contributing via GitHub issues, as well as building the libraries from source. Feel free to modify & rebuild the SDK libraries to suite your needs.

# Community

For questions about OpenUSD Exchange SDK, feel free to join or start a [GitHub Discussion](https://github.com/NVIDIA-Omniverse/usd-exchange/discussions).

For questions about using OpenUSD in NVIDIA Omniverse, use the [Omniverse Forums](https://forums.developer.nvidia.com/tags/c/omniverse/300/usd).

For general questions about OpenUSD itself, use the [Alliance for OpenUSD Forum](https://forum.aousd.org).

# References

- [NVIDIA OpenUSD Exchange SDK Docs](https://docs.omniverse.nvidia.com/usd/code-docs/usd-exchange-sdk)
- [NVIDIA OpenUSD Exchange Samples](https://github.com/NVIDIA-Omniverse/usd-exchange-samples)
- [OpenUSD API Docs](https://openusd.org/release/api/index.html)
- [OpenUSD User Docs](https://openusd.org/release/index.html)
- [NVIDIA OpenUSD Resources and Learning](https://developer.nvidia.com/usd)
- [NVIDIA OpenUSD Code Samples](https://github.com/NVIDIA-Omniverse/OpenUSD-Code-Samples)

# License

The NVIDIA OpenUSD Exchange SDK is governed by the [NVIDIA Agreements | Enterprise Software | NVIDIA Software License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement) and [NVIDIA Agreements | Enterprise Software | Product Specific Terms for Omniverse](https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-omniverse).

See our [License Notices](docs/licenses.md) for more details, including Third Party License Notices for open source dependencies.
