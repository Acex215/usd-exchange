# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import argparse
import shutil

import omni.repo.ci
import omni.repo.man


def main(arguments: argparse.Namespace):
    repo = omni.repo.man.resolve_tokens("$root/repo${shell_ext}")
    usd_flavor = omni.repo.man.resolve_tokens("${usd_flavor}")
    usd_ver = omni.repo.man.resolve_tokens("${usd_ver}")
    python_ver = omni.repo.man.resolve_tokens("${python_ver}")
    abi = omni.repo.man.resolve_tokens("${abi}")

    omni.repo.man.logger.info(f"Using usd_flavor={usd_flavor}, usd_ver={usd_ver}, python_ver={python_ver}, abi={abi}")

    # copy internal packman config into place
    if omni.repo.ci.is_running_on_ci():
        shutil.copyfile("usd-exchange-ci/configs/config.packman.xml", "tools/packman/config.packman.xml")

    # generate the usd-deps.packman.xml
    omni.repo.ci.launch(
        [
            repo,
            "usd",
            "--generate-usd-deps",
            "--usd-flavor",
            usd_flavor,
            "--usd-ver",
            usd_ver,
            "--python-ver",
            python_ver,
        ],
    )

    test = [
        repo,
        "--set-token",
        f"usd_flavor:{usd_flavor}",
        "--set-token",
        f"usd_ver:{usd_ver}",
        "--set-token",
        f"python_ver:{python_ver}",
        f"--abi={abi}",
        "test",
        "--from-package",
        "--config",
        arguments.build_config,
        "--/repo_test/suites/main/verbosity=2",
    ]
    # disable python tests for nopy builds
    if python_ver == "0":
        test.extend(["--suite", "cpp"])
    omni.repo.ci.launch(test)
