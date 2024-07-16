# OpenUSD Exchange Dev Tools

## Custom Repo Tools

In addition to the standard repo_tools suite, we provide a few custom repo_tools to assist common build issues.

To enable these tools with a default configuration, add the following to your `repo.toml`:

```
[repo]
extra_tool_paths."++" = [
    "_build/target-deps/usd-exchange/release/dev/tools/repoman/repo_tools.toml",
]
```

### repo_install_usdex

The first step to building an application or plugin using OpenUSD Exchange SDK is to install the SDK itself. Assembling the minimal runtime requirements of the SDK can be arduous. The `install_usdex` tool can be used to download precompiled binary artifacts for any flavor of the SDK, including all runtime dependencies, and assemble them into a single file tree on your local disk.

```{eval-rst}
.. important::
  Be sure to configure the `--usd-flavor`, `--usd-version`, `--python-version`, and `--version` arguments appropriately to download your preferred flavor of OpenUSD Exchange SDK. See `repo install_usdex -h` for available options.
```

This tool can be invoked from a clone of the [GitHub repository](https://github.com/NVIDIA-Omniverse/usd-exchange) or from a source archive downloaded from an [official release](https://github.com/NVIDIA-Omniverse/usd-exchange/releases).

To configure this tool from your own `repo_tools` enabled project, add the following to your `repo.toml` along with any tool configuration overrides from the default values:

```
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
.. repotools-confval:: use_existing_build
```

### repo_stubgun

Clients can use `repo_stubgen` to generate [Python Stubs](https://mypy.readthedocs.io/en/stable/stubs.html) for IntelliSense in IDEs. This tool is specifically adapted to work with pybind11 compiled bindings modules, as well as some OpenUSD module specifics.

OpenUSD Exchange SDK ships stubs for all modules in the runtime, including OpenUSD, which are generated using this tool. You can also use this tool to generate stubs for your own compiled python modules.

```{eval-rst}
.. important::
  This tool requires `repo_test` to also be enabled in your repo. It uses `repo_test` underlying functionality to configure a runtime environment. If that is not possible, this tool will not work.
```

If you would like to generate stubs for your own python modules, add the following to your `repo.toml` along with any tool configuration overrides from the default values:

```
[repo_stubgen]
enabled = true
```

If you would like to run this process automatically during a build, add it to the post build commands:

```{eval-rst}
.. repotools-file:: ../tools/repoman/repo_tools.toml
```

```
[repo_build.post_build]
commands = [
    ["${root}/repo${shell_ext}", "stubgen", "-c", "${config}"],
]
```

```{eval-rst}
.. repotools-confval:: pybind11_stubgen
.. repotools-confval:: stubgen_include
.. repotools-confval:: stubgen_exclude
```

### repo_version_header

Clients can use `repo_version_header` to generate an include file (e.g. `Version.h`) for common precomplier macros based on `repo_build_number`.

For Windows builds, the tool can optionally generate a `version.rc` [resource file](https://learn.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource), to embed the versioned assembly information into the final DLLs.

If you would like to generate these files, add the following to your `repo.toml` along with any tool configuration overrides from the default values:

```
[repo_version_header]
enabled = true
target_file = "include/foo/Version.h"
target_resource_file = "source/foo/version.rc"
company = "Foo Bar Inc."
product = "Foo Bar"
macro_namespace = "FOOBAR"
```

If you would like to run this process automatically during a build, add it to the `fetch.after_pull_commands`.

```{eval-rst}
.. important::
  This is different to other tools, where we usually suggest using `post_build.commands`. These files need to be in place before project generation occurs, and after fetch dependencies is the only hook available currently.
```

```{eval-rst}
.. repotools-file:: ../tools/repoman/repo_tools.toml
```

```
fetch.after_pull_commands = [
    ["${root}/repo${shell_ext}", "version_header"],
]
```

```{eval-rst}
.. repotools-confval:: target_version_header_file
.. repotools-confval:: target_resource_file
.. repotools-confval:: company
.. repotools-confval:: product
.. repotools-confval:: macro_namespace
.. repotools-confval:: generate_version_stub_file
```
