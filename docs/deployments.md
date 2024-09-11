# Deployment Options

While there are certainly a large range of deployment options & styles, the most common cases for OpenUSD Exchange SDK customers fall into a few main categories:

- A standalone C++ [Executable](#standalone-executable) application.
- A standalone python or shell script invoked as a [command line interface](#scripted-cli).
- Deployed [in a Container](#docker-containers) (e.g. via [Docker](https://www.docker.com))
- A [plugin or extension](#plugin-to-a-dcc) to an existing Digital Content Creation (DCC) Application.

The sections below briefly discuss each of these options and list some common intricacies.

## Standalone Executable

The most common use case for OpenUSD Exchange integrated standalone applications is for a headless data converter executable. Another common use case is for unit testing (and integration testing). Often, we write tests as standalone executables. Each of these apps must be able to bootstrap OpenUSD and OpenUSD Exchange libraries.

You should be able to use the prebuilt binaries from [`install_usdex`](./devtools.md#install_usdex) directly.

See our [example runtime file layouts](./runtime-requirements.md#example-runtime-file-layouts) for a listing of dynamic libraries, python modules, and OpenUSD Plugins (`plugInfo.json`) that you will need to distribute along with your executable program. You will need to ensure that the dynamic libraries are on the appropriate system path.

If you need command line arguments for your program, we recommend using [cxxopts](https://github.com/jarro2783/cxxopts), which is a header-only C++ command line option parser. The headers are available in the `--staging-dir` when you use [`install_usdex`](./devtools.md#install_usdex).

You can see many examples of standalone executables in the [OpenUSD Exchange Samples](https://github.com/NVIDIA-Omniverse/usd-exchange-samples).

## Scripted CLI

Scripted CLIs are similar to [standalone executables](#standalone-executable), but easier to integrate into a pipeline. Or you may just prefer to write your program in Python.

You should be able to use the prebuilt binaries & python modules from [`install_usdex`](./devtools.md#install_usdex) directly.

See our [example runtime file layouts](./runtime-requirements.md#example-runtime-file-layouts) for a listing of dynamic libraries, python modules, and OpenUSD Plugins (`plugInfo.json`) that you will need to distribute along with your python script. Your script will need to ensure that the dynamic libraries are on the appropriate system path and that the python modules are on your `PYTHONPATH`.

If you need command line arguments for your program, we recommend using Python's native [argparse](https://docs.python.org/3/library/argparse.html).

You can see many examples of scripted CLIs in the [OpenUSD Exchange Samples](https://github.com/NVIDIA-Omniverse/usd-exchange-samples).

## Docker Containers

When integrating OpenUSD Exchange libraries and modules into a microservice or other containerized process, you will likely want to install from within your `Dockerfile`.

This process is fairly straightforward, but there are a couple intricacies that you should be aware of in order to end up with the minimal amount of files in your final image.

Below is an example `Dockerfile` for a microservice that uses the [`usdex.core`](./python-usdex-core.rst) python module:

```docker
FROM ubuntu:22.04

# Install git (to clone the repo), curl (to download binaries), and python (to run)
RUN apt update && apt install -y git curl python3.10 libpython3.10

# Install OpenUSD and OpenUSD Exchange, making sure to match the system python version
RUN git clone https://github.com/NVIDIA-Omniverse/usd-exchange.git
RUN cd usd-exchange && ./repo.sh install_usdex --python-version 3.10 --version 1.0.0 --install-dir /usdex-runtime

# Clean up temporary files not needed for runtime
RUN usd-exchange/tools/packman/packman prune 0 && rm -rf usd-exchange

# Install the OpenUSD and OpenUSD Exchange libraries and python modules
RUN python3.10 -m site --user-site
RUN ln -s /usdex-runtime/python/* /usr/local/lib/python3.10/dist-packages/
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usdex-runtime/lib"
```

Once you build the image you should be able to run it and use [`usdex.core`](./python-usdex-core.rst) from any python process in the container:

```bash
> docker run my-image python3.10 -c 'import pxr.Usd, usdex.core; print(f"OpenUSD: {pxr.Usd.GetVersion()}\nOpenUSD Exchange: {usdex.core.version()}")'
OpenUSD: (0, 24, 5)
OpenUSD Exchange: 1.0.0
```

```{eval-rst}
.. note::
  The example above is Ubuntu based using Python 3.10, but neither of these are strict requirements. The precompiled OpenUSD Exchange SDK binaries are ``manylinux_2_35`` compatible and available for multiple python versions (or without python entirely).
```

You may wish to approach your container organization differently, but the main steps should be the same:
- Download and stage the [runtime requirements](./runtime-requirements.md)
- Clean up temporary files
- Configure your environment so the dynamic libraries and python modules are available to other processes in your container

```{eval-rst}
.. important::
  You must ensure that the OpenUSD libraries and plugins from the ``install_usdex`` process are the **only** OpenUSD binaries configured in the container.

  If, for example, you had previously run ``pip install usd-core`` in your container, you will almost certainly have two copies of the OpenUSD binaries configured, and they are very likely to conflict with each other in unpredictable ways.
```

## Plugin to a DCC

This approach generally takes the form of a dynamic library and/or python module that is loaded into the DCC via a native plugin mechanism. Sometimes, they can be built into the DCC directly, if a single 3rd Party is developing both the DCC and integrating OpenUSD Exchange libraries and modules. For the purposes of this article we will consider both as "Plugins".

When integrating OpenUSD Exchange libraries and modules into an existing DCC Application, making your own library that links `usdex_core` (or module that imports `usdex.core`) is recommended.

See our [example runtime file layouts](./runtime-requirements.md#example-runtime-file-layouts) for a listing of dynamic libraries, python modules, and OpenUSD Plugins (`plugInfo.json`) that you will need to distribute along with your DCC Plugin.

You will also need to determine a few important details about your target DCC:

### Does it provide its own OpenUSD runtime?

If it does, you will likely want to match the exact OpenUSD binaries. You _might_ be able to use the prebuilt binaries from [`install_usdex`](./devtools.md#install_usdex) if they were built with compatible [dependencies and options](https://github.com/PixarAnimationStudios/OpenUSD/blob/release/BUILDING.md).

However, the more likely outcome is that you should re-compile the OpenUSD Exchange SDK from source code, making sure to compile & link against your application's USD distribution.

Once you have a USD distro assembled, you can "source link" it into a local clone of OpenUSD Exchange SDK:

``````{card}
`````{tab-set}
````{tab-item} Linux
:sync: linux

```bash
git clone https://github.com/NVIDIA-Omniverse/usd-exchange.git
cd usd-exchange
./repo.sh source link usd_release ../path/to/your/usd
./repo.sh build
```
````
````{tab-item} Windows
:sync: windows

```bat
git clone https://github.com/NVIDIA-Omniverse/usd-exchange.git
cd usd-exchange
.\repo.bat source link usd_release ..\path\to\your\usd
.\repo.bat build
```
````
`````
``````

If you encounter missing file errors, it likely indicates a difference between your USD distro file layout and the ones NVIDIA produces internally. Inspect the two folder structures and try to align them.

```{eval-rst}
.. note::
  The ``repo source link`` command will generate a ``deps/usd-deps.packman.xml.user`` file with the relative filesystem path to your USD distro. The ``repo build`` command will respect this. If you want to alter the path later, you can hand edit this file. If you want to revert to using the pre-built USD distros, just remove this file entirely or call ``repo source unlink usd_release``.
```

See [CONTRIBUTING.md](https://github.com/NVIDIA-Omniverse/usd-exchange/blob/main/CONTRIBUTING.md#building) for more information on the OpenUSD Exchange SDK build process.

### Does it use TBB or Boost?

[TBB](https://oneapi-src.github.io/oneTBB) and [Boost](https://www.boost.org) are open source software that OpenUSD requires. While OpenUSD Exchange does not use them directly, several critical OpenUSD libraries do link & require them.

If your application ships its own TBB or Boost, you _might_ be able to use the prebuilt binaries from [`install_usdex`](./devtools.md#install_usdex), it works out more often than not.

However, some applications use an older TBB or Boost library that is incompatible. There isn't any great way to detect this, other than to try & see if you hit issues. If you do, you should re-compile OpenUSD against your application's TBB and/or Boost libraries, then re-compile the OpenUSD Exchange SDK from source code, making sure to compile & link against your new USD distribution.

### Does it provide its own Python runtime?

If you want to use the OpenUSD or OpenUSD Exchange python modules, you will need a python interpreter at runtime. If your application has one natively, you will need to match at least the Python major.minor version to be able to import the precompiled python modules from [`install_usdex`](./devtools.md#install_usdex).

We support a range of python versions, but if yours is unsupported, you will need to re-compile both OpenUSD and the OpenUSD Exchange SDK modules from source code, making sure to compile & link against your application's Python distribution.

```{eval-rst}
.. warning::
  Even if you don't require python in your application, you may still require ``libpython.so/python3.dll`` as the OpenUSD C++ libraries do link python by default unless you are using a flavor of the OpenUSD binaries without the python dependency or have explicitly built OpenUSD without python. See `install_usdex <./devtools.html#install_usdex>`_ if you want to automatically install the necessary python library.
```
