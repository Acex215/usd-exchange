# OpenUSD Exchange License Notices

## NVIDIA Software License Agreement

The NVIDIA OpenUSD Exchange SDK is governed by the [NVIDIA Agreements | Enterprise Software | NVIDIA Software License Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement) and [NVIDIA Agreements | Enterprise Software | Product Specific Terms for Omniverse](https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-omniverse).

As the NVIDIA OpenUSD Exchange SDK is made source available, “Derivative Samples” can be produced from its source code, and all modifications, derivatives, adaptations, extensions or enhancements to that source code are permissible, provided the “Derivative Samples” requirements of license is adhered to.

## Runtime License Notices

The NVIDIA OpenUSD Exchange SDK makes direct use of several 3rd Party Open Source Software (OSS). Each of these 3rd Party OSS may use other OSS internally.

In addition, the NVIDIA OpenUSD Exchange SDK uses some NVIDIA proprietary technologies. All such proprietary technologies fall under the NVIDIA Software License Agreement and, for redistribution purposes, can be considered a part of the NVIDIA OpenUSD Exchange SDK itself. Some of these proprietary technologies may use 3rd Party OSS as well.

Some of the runtime dependencies are compile-time optional, and some only apply to individual modules.

Detailed below are the licenses of all runtime dependencies of each OpenUSD Exchange library & module. Each dependency listed links to the relevant [individual licenses](#individual-licenses).

```{eval-rst}
.. note::
  OpenUSD uses many 3rd Party OSS to build and at runtime. Most of these are isolated to individual modules (USD plugins). Many are only relevant to a rendering context (e.g via Hydra) and do not apply to a 3D scene description authoring context. Some *do apply to 3D authoring*, but are not utilized by any OpenUSD Exchange SDK modules.

  The listings below do not include dependencies required to re-build (compile) the OpenUSD Exchange libraries. Similarly, they exclude licenses for OpenUSD modules that OpenUSD Exchange SDK does not leverage.

  This listing represents the technologies in-use for a shipping runtime that uses each OpenUSD Exchange module. If you ship a complete OpenUSD runtime as well (as opposed to our intentionally limited subset) you will need to gather the appropriate licenses manually. They can be found in `_install/target-deps/usd/release/PACKAGE-LICENSES` if you used `repo install_usdex` with default arguments.
```

The versions of some dependencies can vary across each build flavor of OpenUSD Exchange:
- Many are static/common to all flavors and are listed in the source code [target-deps xml file](https://github.com/NVIDIA-Omniverse/usd-exchange/blob/main/deps/target-deps.packman.xml).
- OpenUSD and Python versions vary per flavor, with all official flavors listed in [usd_flavors.json](https://github.com/NVIDIA-Omniverse/usd-exchange/blob/main/deps/usd_flavors.json).
- Additionally, as OpenUSD Exchange is source available, it can be recompiled against newer, older, or customized versions of any of its dependencies.

### Core C++ Shared Library

These licenses pertain to the `usdex_core` shared library.

**Mandatory Runtime Dependencies**

```{eval-rst}
- OpenUSD Exchange `(jump to license) <https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement>`_
- OpenUSD `(jump to license) <usd LICENSE_>`_
- Omni Transcoding `(jump to license) <omni_transcoding LICENSE_>`_
- TBB :ref:`(jump to license) <tbblicense>`
- zlib `(jump to license) <zlib LICENSE_>`_
```

**Optional Runtime Dependencies**

These licenses are optional in that the python-less flavors of `usdex_core` do not use them.

```{eval-rst}
.. important::
  If you are using a `WITH_PYTHON` flavor, then these licenses become mandatory.
```

```{eval-rst}
- Python `(jump to license) <python LICENSE_>`_
- Boost `(jump to license) <boost LICENSE_>`_
```

### Core Python Module

These licenses pertain to the `usdex.core` python module, its compiled bindings library, and its use of the `usdex_core` shared library.

```{eval-rst}
- OpenUSD Exchange `(jump to license) <https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement>`_
- OpenUSD `(jump to license) <usd LICENSE_>`_
- Omni Transcoding `(jump to license) <omni_transcoding LICENSE_>`_
- TBB :ref:`(jump to license) <tbblicense>`
- zlib `(jump to license) <zlib LICENSE_>`_
- Python `(jump to license) <python LICENSE_>`_
- Boost `(jump to license) <boost LICENSE_>`_
- pybind11 `(jump to license) <pybind11 LICENSE_>`_
- pyboost11 `(jump to license) <pyboost11 LICENSE_>`_
```

### C++ Python Binding Helpers

These licenses pertain to the `usdex/pybind` c++ headers and any compiled library or executable in which they are used (e.g. the `usdex.core` python binding library).

```{eval-rst}
- OpenUSD Exchange `(jump to license) <https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement>`_
- OpenUSD `(jump to license) <usd LICENSE_>`_
- Python `(jump to license) <python LICENSE_>`_
- Boost `(jump to license) <boost LICENSE_>`_
- pybind11 `(jump to license) <pybind11 LICENSE_>`_
- pyboost11 `(jump to license) <pyboost11 LICENSE_>`_
```

### C++ Test Helpers

These licenses pertain to the `usdex/test` c++ headers and any compiled library or executable in which they are used (i.e. [doctest](https://github.com/doctest/doctest) executable binaries).

```{eval-rst}
- OpenUSD Exchange `(jump to license) <https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement>`_
- OpenUSD `(jump to license) <usd LICENSE_>`_
- cxxopts `(jump to license) <cxxopts LICENSE_>`_
- doctest `(jump to license) <doctest LICENSE_>`_
```

### Python Test Module

These licenses pertain to the `usdex.test` python module, which is based on python's `unittest` framework.

```{eval-rst}
- OpenUSD Exchange `(jump to license) <https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement>`_
- OpenUSD `(jump to license) <usd LICENSE_>`_
- Omni Transcoding `(jump to license) <omni_transcoding LICENSE_>`_
- Omni Asset Validator `(jump to license) <omni.asset_validator LICENSE_>`_
- TBB :ref:`(jump to license) <tbblicense>`
- zlib `(jump to license) <zlib LICENSE_>`_
- Python `(jump to license) <python LICENSE_>`_
- Boost `(jump to license) <boost LICENSE_>`_
- pybind11 `(jump to license) <pybind11 LICENSE_>`_
- pyboost11 `(jump to license) <pyboost11 LICENSE_>`_
```

### Source Code Inspiration

Some design patterns used in OpenUSD Exchange SDK source code may resemble those found in the following products. These licenses are relevant as inspiration only. There is no common implementation nor shipping binary that is relevant, neither at compile, link, nor runtime.

```{eval-rst}
- Cortex `(jump to license) <cortex LICENSE_>`_
- Gaffer `(jump to license) <gaffer LICENSE_>`_
```

## Individual Licenses

```{eval-rst}
.. include-licenses:: /_build/target-deps/usd/release/PACKAGE-LICENSES/usd-license.txt

.. include-licenses:: /_build/target-deps/omni_transcoding/release/PACKAGE-LICENSES/omni_transcoding-LICENSE.txt

.. include-licenses:: /_build/target-deps/omni_asset_validator/PACKAGE-LICENSES/omni.asset_validator-LICENSE.txt

.. Workaround for TBB as the name of the license file varies between packages

.. _tbblicense:

.. include-licenses:: /_build/target-deps/usd/release/PACKAGE-LICENSES/*TBB-LICENSE.txt

.. include-licenses:: /_build/target-deps/usd/release/PACKAGE-LICENSES/zlib-LICENSE.txt

.. include-licenses:: /_build/target-deps/cxxopts/PACKAGE-LICENSES/cxxopts-LICENSE.txt

.. include-licenses:: /_build/target-deps/doctest/PACKAGE-LICENSES/doctest-LICENSE.txt

.. include-licenses:: /_build/target-deps/usd/release/PACKAGE-LICENSES/python-LICENSE.txt

.. include-licenses:: /_build/target-deps/usd/release/PACKAGE-LICENSES/boost-LICENSE.txt

.. include-licenses:: /_build/target-deps/pybind11/PACKAGE-LICENSES/pybind11-LICENSE.txt

.. include-licenses:: /tools/internal-licenses/pyboost11-LICENSE.txt

.. include-licenses:: /tools/internal-licenses/cortex-LICENSE.txt

.. include-licenses:: /tools/internal-licenses/gaffer-LICENSE.txt
```
