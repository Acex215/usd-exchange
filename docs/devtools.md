# OpenUSD Exchange Dev Tools

Most users of OpenUSD Exchange SDK will have their own build systems & CI/CD processes, and our custom dev tools may be of limited use outside of the usd-exchange and usd-exchange-samples repositories.

However, one tool that we highly recommend using is the `repo install_usdex` tool, which can be used to acquire all of the OpenUSD Exchange build & runtime requirements.

## install_usdex

The first step to building an application or plugin using OpenUSD Exchange SDK is to install the SDK itself. Assembling the minimal runtime requirements of the SDK can be arduous. The `install_usdex` tool can be used to download precompiled binary artifacts for any flavor of the SDK, including all runtime dependencies, and assemble them into a single file tree on your local disk.

```{eval-rst}
.. important::
  Be sure to configure the ``--usd-flavor``, ``--usd-version``, ``--python-version``, and ``--version`` arguments appropriately to download your preferred flavor of OpenUSD Exchange SDK. See ``repo install_usdex -h`` for available options.
```

This tool can be invoked from a clone of the [GitHub repository](https://github.com/NVIDIA-Omniverse/usd-exchange) or from a source archive downloaded from an [official release](https://github.com/NVIDIA-Omniverse/usd-exchange/releases).

### Install usdex_core

By default, the tool will install the core library and module from OpenUSD Exchange SDK. For example, to download & assemble a USD 24.05 & Python 3.11 compatible binaries for OpenUSD Exchange v1.0.0 call:

``````{card}
`````{tab-set}
````{tab-item} Linux
:sync: linux

```bash
./repo.sh install_usdex --usd-version 24.05 --python-version 3.11 --version 1.0.0
```
````
````{tab-item} Windows
:sync: windows

```bash
.\run.bat install_usdex --usd-version 24.05 --python-version 3.11 --version 1.0.0
```
````
`````
``````

Similarly, to download & assemble a minimal monolithic USD 23.11, with no python support, for OpenUSD Exchange v1.0.0 call:

``````{card}
`````{tab-set}
````{tab-item} Linux
:sync: linux

```bash
./repo.sh install_usdex --usd-flavor usd-minimal --usd-version 23.11 --python-version 0 --version 1.0.0
```
````
````{tab-item} Windows
:sync: windows

```bash
.\run.bat install_usdex --usd-flavor usd-minimal --usd-version 23.11 --python-version 0 --version 1.0.0
```
````
`````
``````

### Extra OpenUSD plugins

If you need more OpenUSD modules than the strict minimal requirements of OpenUSD Exchange SDK, you can install them using `--install-extra-plugins`.

For example, to add on `usdSkel` and `usdPhysics` call:

``````{card}
`````{tab-set}
````{tab-item} Linux
:sync: linux

```bash
./repo.sh install_usdex --version 1.0.0 --install-extra-plugins usdSkel usdPhysics
```
````
````{tab-item} Windows
:sync: windows

```bash
.\run.bat install_usdex --version 1.0.0 --install-extra-plugins usdSkel usdPhysics
```
````
`````
``````

### Install usdex_rtx

If you are interested in RTX Rendering via NVIDIA Omniverse, you may want to use `usdex_rtx` to assist with [MDL Shader](https://www.nvidia.com/en-us/design-visualization/technologies/material-definition-language) authoring. Use the `--install-rtx` argument to install the [usdex_rtx library](../api/group__rtx__materials.rebreather_rst) and [`usdex.rtx` python module](./python-usdex-rtx.rst).

``````{card}
`````{tab-set}
````{tab-item} Linux
:sync: linux

```bash
./repo.sh install_usdex --version 1.0.0 --install-rtx
```
````
````{tab-item} Windows
:sync: windows

```bash
.\run.bat install_usdex --version 1.0.0 --install-rtx
```
````
`````
``````

### Python test helpers

If you would like to use our [`usdex.test` python module](./python-usdex-test.rst), or the [Omniverse Asset Validator](https://docs.omniverse.nvidia.com/kit/docs/asset-validator/latest/index.html), you can use `--install-test` to install them both.

``````{card}
`````{tab-set}
````{tab-item} Linux
:sync: linux

```bash
./repo.sh install_usdex --version 1.0.0 --install-test
```
````
````{tab-item} Windows
:sync: windows

```bash
.\run.bat install_usdex --version 1.0.0 --install-test
```
````
`````
``````

### repo_tools configuration

If you do use `repo_tools` in your project, you can configure `install_usdex` by adding the following to your `repo.toml` along with any tool configuration overrides from the default values:

```
[repo]
extra_tool_paths."++" = [
    "_build/target-deps/usd-exchange/release/dev/tools/repoman/repo_tools.toml",
]

[repo_install_usdex]
enabled = true
```

If you would like to run this process automatically during a build, add it to the post build commands:

```
[repo_build.post_build]
commands = [
    ["$root/repo${shell_ext}", "install_usdex", "-c", "$config"],
]
```

```{eval-rst}
.. repotools-file:: ../tools/repoman/repo_tools.toml
```

```{eval-rst}
.. repotools-confval:: staging_dir
.. repotools-confval:: install_dir
.. repotools-confval:: usd_flavor
.. repotools-confval:: usd_ver
.. repotools-confval:: python_ver
```
