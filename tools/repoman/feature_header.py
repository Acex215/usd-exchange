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
import datetime
import os
from typing import Callable, Dict


def replace_file(filename, new_file_contents):
    try:
        with open(filename, "r+") as f:
            old_file_contents = f.read()
            # only write if different otherwise this will force a rebuild every time
            if old_file_contents != new_file_contents:
                f.seek(0)
                f.write(new_file_contents)
                f.truncate()
    except IOError:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(new_file_contents)


def generate_header(target_file, license_preamble, license_text, with_python):
    license_preamble = "\n".join([f"// {x}" for x in license_preamble.strip("\n").split("\n")])
    license_text = "\n".join([f"// {x}" for x in license_text.strip("\n").split("\n")])
    new_file_contents = f"""{license_preamble}
//
{license_text}

#pragma once

//! @file {target_file.split("include/")[-1]}
//! @brief Feature macros for this library
//! Automatically generated file

//! With Python feature.
#define USDEX_WITH_PYTHON {with_python}

"""
    replace_file(target_file, new_file_contents)


def setup_repo_tool(parser: argparse.ArgumentParser, config: Dict) -> Callable:
    parser.description = """
        Tool to generate and install a header file with automated substitutions based on the OpenUSD Exchange SDK features being built.
    """

    parser.add_argument(
        "-t",
        "--targetFile",
        dest="target_file",
        help="Path to generate the target file",
    )

    parser.add_argument(
        "-p",
        "--python-version",
        dest="python_ver",
        help='Sets the python version. Any value other than "0" indicates the build is "with python".',
    )

    tool_config = config.get("repo_feature_header", {})
    if not tool_config.get("enabled", True):
        return None

    def run_repo_tool(options: Dict, config: Dict):

        target_file = options.target_file or config["repo_feature_header"]["target_file"]
        python_ver = options.python_ver or config["repo_feature_header"]["python_ver"]

        current_year = str(datetime.date.today().year)
        copyright_start = config.get("repo_docs", {}).get("copyright_start", current_year)
        years = current_year if copyright_start == current_year else f"{copyright_start}-{current_year}"
        license_preamble = config["repo_version_header"]["license_preamble"].replace("{years}", years)
        license_text = config["repo_version_header"]["license_text"]

        with_python = "1"
        if python_ver == "0":
            with_python = "0"

        generate_header(target_file, license_preamble, license_text, with_python)

    return run_repo_tool
