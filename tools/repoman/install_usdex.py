# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import argparse
import contextlib
import os
import shutil
from typing import Callable, Dict

import omni.repo.man
import packmanapi


def __installPythonModule(prebuild_copy_dict: Dict, sourceRoot: str, moduleNamespace: str, libPrefix: str):
    prebuild_copy_dict.extend(
        [
            [f"{sourceRoot}/{moduleNamespace}/*.py", "${install_dir}/python/" + moduleNamespace],
            [f"{sourceRoot}/{moduleNamespace}/*.pyi", "${install_dir}/python/" + moduleNamespace],
            [f"{sourceRoot}/{moduleNamespace}/{libPrefix}*" + "${bindings_ext}", "${install_dir}/python/" + moduleNamespace],
        ]
    )


def __acquireUSDEX(installDir, useExistingBuild, targetDepsDir, usd_flavor, usd_ver, python_ver, buildConfig, version, tokens):
    if useExistingBuild:
        print(f"Using local usd-exchange from {installDir}")
        return installDir

    packageName = None
    packageVersion = version
    if not packageVersion:
        info = {}
        # check for a packman dependency
        with contextlib.suppress(packmanapi.PackmanError):
            info = packmanapi.resolve_dependency(
                "usd-exchange",
                "deps/target-deps.packman.xml",
                platform=tokens["platform"],
                remotes=["cloudfront"],
                tokens=tokens,
            )
        if "remote_filename" in info:
            # override the package info using details from the remote
            parts = info["remote_filename"].split("@")
            packageName = parts[0]
            packageVersion = os.path.splitext(parts[1])[0]
        elif "local_path" in info:
            # its a local source linked usdex
            linkPath = f"{targetDepsDir}/usd-exchange/{buildConfig}"
            print(f"Link local usd-exchange to {linkPath}")
            packmanapi.link(linkPath, info["local_path"])
            return linkPath

    if not packageVersion:
        raise omni.repo.man.exceptions.ConfigurationError(
            "No version was specified. Use the `--version` argument or setup a packman dependency for usd-exchange"
        )

    # respect flavor variations if they are provided
    if not packageName or (usd_flavor and usd_ver and python_ver):
        pyFlavor = "nopy" if python_ver == "0" else f"py{python_ver}"
        packageName = f"usd-exchange.usd-{usd_flavor}-{usd_ver}.{pyFlavor}.{tokens['platform']}.{buildConfig}"  # note: needs adjusting

    linkPath = f"{targetDepsDir}/usd-exchange/{buildConfig}"
    print(f"Download and Link usd-exchange {packageVersion} to {linkPath}")
    try:
        result = packmanapi.install(name=packageName, package_version=packageVersion, remotes=["cloudfront"], link_path=linkPath)
        return list(result.values())[0]
    except packmanapi.PackmanErrorFileNotFound:
        raise omni.repo.man.exceptions.ConfigurationError(f"Unable to download {packageName}, version {packageVersion}")


def __install(installDir: str, useExistingBuild: bool, stagingDir: str, usd_flavor: str, usd_ver: str, python_ver: str, buildConfig: str, clean: bool, version: str):
    tokens = omni.repo.man.get_tokens()
    tokens["config"] = buildConfig
    platform = tokens["platform"]
    installDir = omni.repo.man.resolve_tokens(installDir, extra_tokens=tokens)
    targetDepsDir = omni.repo.man.resolve_tokens(f"{stagingDir}/target-deps", extra_tokens=tokens)

    if clean:
        print(f"Cleaning install dir {installDir}")
        shutil.rmtree(installDir, ignore_errors=True)
        print(f"Cleaning staging dir {stagingDir}")
        shutil.rmtree(stagingDir, ignore_errors=True)
        return

    usd_exchange_path = __acquireUSDEX(installDir, useExistingBuild, targetDepsDir, usd_flavor, usd_ver, python_ver, buildConfig, version, tokens)

    # determine the required runtime dependencies
    runtimeDeps = ["omni_transcoding", f"usd-{buildConfig}"]
    if python_ver != "0":
        runtimeDeps.append("python")

    print("Download usd-exchange dependencies...")
    depsFile = f"{usd_exchange_path}/dev/deps/all-deps.packman.xml"
    # TODO: filter downloads for runtimeDeps only
    result = packmanapi.pull(depsFile, platform=platform, tokens=tokens, return_extra_info=True)
    for dep, info in result.items():
        if dep in runtimeDeps:
            if dep == f"usd-{buildConfig}":
                linkPath = f"{targetDepsDir}/usd/{buildConfig}"
            elif buildConfig in info["package_name"]:  # dep uses omniflow v2 naming with separate release/debug packages
                linkPath = f"{targetDepsDir}/{dep}/{buildConfig}"
            else:
                linkPath = f"{targetDepsDir}/{dep}"
            print(f"Link {dep} to {linkPath}")
            packmanapi.link(linkPath, info["local_path"])

    print(f"Install usd-exchange to {installDir}")
    mapping = omni.repo.man.get_platform_file_mapping(platform)
    mapping["config"] = buildConfig
    mapping["root"] = tokens["root"]
    mapping["install_dir"] = installDir
    os_name, arch = omni.repo.man.get_platform_os_and_arch(platform)
    filters = [platform, buildConfig, os_name, arch]

    python_path = f"{targetDepsDir}/python"
    usd_path = f"{targetDepsDir}/usd/{buildConfig}"
    transcoding_path = f"{targetDepsDir}/omni_transcoding/{buildConfig}"

    prebuild_dict = {
        "copy": [
            # transcoding
            [transcoding_path + "/lib/${lib_prefix}omni_transcoding${lib_ext}", "${install_dir}/lib"],
            # usdex
            [usd_exchange_path + "/lib/${lib_prefix}usdex_core${lib_ext}", "${install_dir}/lib"],
            # usd
            [usd_path + "/lib/${lib_prefix}*ar${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*arch${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*gf${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*js${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*kind${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*ndr${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*pcp${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*plug${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*sdf${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*sdr${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*tf${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*trace${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*usd${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*usdGeom${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*usdLux${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*usdShade${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*usdUtils${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*vt${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*work${lib_ext}", "${install_dir}/lib"],
            [usd_path + "/lib/${lib_prefix}*usd_ms${lib_ext}", "${install_dir}/lib"],  # special case for monolithic flavors
        ],
    }
    if usd_flavor == "blender":
        prebuild_dict["copy"].extend(
            [
                # blender uses a monolithic usd build which requires extra libs
                [usd_path + "/bin/${lib_prefix}*${lib_ext}", "${install_dir}/lib"],
                # blender separates usd plugins into two folders, but requires them all at runtime
                [f"{usd_path}/lib/usd", "${install_dir}/lib/usd"],
                [f"{usd_path}/plugin/usd", "${install_dir}/lib/usd"],
            ]
        )
        for moduleNamespace, libPrefix in (
            ("pxr/PxOsd", "_pxOsd"),
            ("pxr/Garch", "_garch"),
            ("pxr/Glf", "_glf"),
            ("pxr/CameraUtil", "_cameraUtil"),
            ("pxr/UsdImagingGL", "_usdImagingGL"),
            ("pxr/GeomUtil", "_geomUtil"),
            ("pxr/SdrGlslfx", "_sdrGlslfx"),
            ("pxr/UsdAppUtils", "_usdAppUtils"),
            ("pxr/UsdMedia", "_usdMedia"),
            ("pxr/UsdPhysics", "_usdPhysics"),
            ("pxr/UsdProc", "_usdProc"),
            ("pxr/UsdRender", "_usdRender"),
            ("pxr/UsdRi", "_usdRi"),
            ("pxr/UsdShaders", "_usdShaders"),
            ("pxr/UsdVol", "_usdVol"),
        ):
            __installPythonModule(prebuild_dict["copy"], f"{usd_path}/lib/python", moduleNamespace, libPrefix)
    elif usd_flavor == "houdini":
        prebuild_dict["copy"].extend(
            [
                # houdini ships with custom `usd_plugins` folder and it appears to be a hardcoded search location in their usd libs
                [f"{usd_path}/lib/usd_plugins", "${install_dir}/lib/usd_plugins"],
            ]
        )
    else:
        prebuild_dict["copy"].extend(
            [
                # default usd plugins folder
                [f"{usd_path}/lib/usd", "${install_dir}/lib/usd"],
            ]
        )
    if buildConfig == "debug":
        prebuild_dict["copy"].extend(
            [
                # tbb ships with usd, but is named differently in release/debug
                [usd_path + "/lib/${lib_prefix}tbb_debug${lib_ext}*", "${install_dir}/lib"],
                [usd_path + "/bin/${lib_prefix}tbb_debug${lib_ext}*", "${install_dir}/lib"],  # windows
            ]
        )
    else:
        prebuild_dict["copy"].extend(
            [
                # tbb ships with usd, but is named differently in release/debug
                [usd_path + "/lib/${lib_prefix}tbb${lib_ext}*", "${install_dir}/lib"],
                [usd_path + "/bin/${lib_prefix}tbb${lib_ext}*", "${install_dir}/lib"],  # windows
            ]
        )
    if python_ver != "0":
        # usdex
        __installPythonModule(prebuild_dict["copy"], f"{usd_exchange_path}/python", "usdex/core", "_usdex_core")
        # usd
        prebuild_dict["copy"].extend(
            [
                [usd_path + "/lib/${lib_prefix}*boost_python*${lib_ext}*", "${install_dir}/lib"],
                # note: revisit installing libpython, it can cause issues in some deployments
                [python_path + "/lib/${lib_prefix}*python*${lib_ext}*", "${install_dir}/lib"],
                [python_path + "/${lib_prefix}*python*${lib_ext}*", "${install_dir}/lib"],  # windows
            ]
        )
        for moduleNamespace, libPrefix in (
            ("pxr/Ar", "_ar"),
            ("pxr/Gf", "_gf"),
            ("pxr/Kind", "_kind"),
            ("pxr/Ndr", "_ndr"),
            ("pxr/Pcp", "_pcp"),
            ("pxr/Plug", "_plug"),
            ("pxr/Sdf", "_sdf"),
            ("pxr/Sdr", "_sdr"),
            ("pxr/Tf", "_tf"),
            ("pxr/Trace", "_trace"),
            ("pxr/Usd", "_usd"),
            ("pxr/UsdGeom", "_usdGeom"),
            ("pxr/UsdLux", "_usdLux"),
            ("pxr/UsdShade", "_usdShade"),
            ("pxr/UsdUtils", "_usdUtils"),
            ("pxr/Vt", "_vt"),
            ("pxr/Work", "_work"),
        ):
            __installPythonModule(prebuild_dict["copy"], f"{usd_path}/lib/python", moduleNamespace, libPrefix)

    omni.repo.man.fileutils.ERROR_IF_NOT_EXIST = True
    omni.repo.man.fileutils.copy_and_link_using_dict(prebuild_dict, filters, mapping)


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    toolConfig = config.get("repo_install_usdex", {})
    if not toolConfig.get("enabled", True):
        return None

    installDir = toolConfig["install_dir"]
    stagingDir = toolConfig["staging_dir"]
    usd_flavor = toolConfig["usd_flavor"]
    usd_ver = toolConfig["usd_ver"]
    python_ver = toolConfig["python_ver"]

    parser.description = "Tool to download and install precompiled OpenUSD Exchange binaries and all of its runtime dependencies."
    parser.add_argument(
        "--version",
        dest="version",
        help="The exact version of OpenUSD Exchange to install. Overrides any specified packman dependency. "
        "If this arg is not specified, and no packman dependency exists, then repo_build_number will be used to determine the current version. "
        "Note this last fallback assumes source code and git history are available. If they are not, the install will fail.",
    )
    parser.add_argument(
        "-s",
        "--staging-dir",
        dest="staging_dir",
        help=f"Required compile, link, and runtime dependencies will be downloaded & linked this folder. Defaults to `{stagingDir}`",
    )
    parser.add_argument(
        "-i",
        "--install-dir",
        dest="install_dir",
        help=f"Required runtime files will be assembled into this folder. Defaults to `{installDir}`",
    )
    parser.add_argument(
        "--use-existing-build",
        action="store_true",
        dest="use_existing_build",
        help="Enable this to use an existing build of OpenUSD Exchange rather than download a package. "
        "The OpenUSD Exchange distro must already exist in the --install-dir or the process will fail.",
        default=False,
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        dest="clean",
        help="Clean the install directory and staging directory and exit.",
        default=False,
    )
    omni.repo.man.add_config_arg(parser)
    parser.add_argument(
        "--usd-flavor",
        dest="usd_flavor",
        choices=["usd", "nv-usd"],  # public flavors only
        help=f"The OpenUSD flavor to install. 'usd' means stock pxr builds. Defaults to `{usd_flavor}`",
    )
    parser.add_argument(
        "--usd-version",
        dest="usd_ver",
        choices=["23.11"],  # public versions only
        help=f"The OpenUSD version to install. Defaults to `{usd_ver}`",
    )
    parser.add_argument(
        "--python-version",
        dest="python_ver",
        choices=["3.10", "0"],
        help=f"The Python flavor to install. Use `0` to disable Python features. Defaults to `{python_ver}`",
    )

    def run_repo_tool(options: Dict, config: Dict):
        toolConfig = config["repo_install_usdex"]
        stagingDir = options.staging_dir or toolConfig["staging_dir"]
        installDir = options.install_dir or toolConfig["install_dir"]
        useExistingBuild = options.use_existing_build or toolConfig["use_existing_build"]
        usd_flavor = options.usd_flavor or toolConfig["usd_flavor"]
        usd_ver = options.usd_ver or toolConfig["usd_ver"]
        python_ver = options.python_ver or toolConfig["python_ver"]
        __install(installDir, useExistingBuild, stagingDir, usd_flavor, usd_ver, python_ver, options.config, options.clean, options.version)

    return run_repo_tool
