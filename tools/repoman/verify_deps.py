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
from typing import Callable, Dict

import omni.repo.man
import packmanapi


def run_verify_deps(options: argparse.Namespace, toolConfig: Dict):
    if options.verbose:
        packmanapi.set_verbosity_level(packmanapi.VERBOSITY_HIGH)

    depsFiles = ["deps/repo-deps.packman.xml", toolConfig["repo"]["folders"]["host_deps_xml"]]
    depsFiles.extend(toolConfig["repo_build"]["fetch"]["packman_target_files_to_pull"])
    platforms = ["linux-x86_64", "windows-x86_64"]
    buildConfigs = ["release", "debug"]
    remotes = ["cloudfront"]

    status = 0
    for platform in platforms:
        tokens = omni.repo.man.get_tokens(platform=platform)
        for config in buildConfigs:
            tokens["config"] = config
            for depsFile in depsFiles:
                omni.repo.man.print_log(f"Verifying deps `{depsFile}` for platform={platform} config={config}")
                (_, missing) = packmanapi.verify(
                    depsFile,
                    platform=platform,
                    tokens=tokens,
                    exclude_local=True,
                    remotes=remotes,
                    tags={"public": "true"},
                )

                for remote, package in missing:
                    omni.repo.man.logger.log(
                        level=omni.repo.man.logging.ERROR,
                        msg=f"Failed: {package.name}@{package.version} is missing from {remote}",
                    )
                    status = 1

    if status == 0:
        omni.repo.man.print_log("Verification Passed")
    else:
        raise omni.repo.man.RepoToolError("Verification Failed")


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    parser.description = "Tool to verify whether packman dependencies are public"
    tool_config = config.get("repo_verify_deps", {})
    if not tool_config.get("enabled", True):
        return None

    return run_verify_deps
