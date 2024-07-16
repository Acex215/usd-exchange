# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import os
import re
import shutil
import tempfile
import unittest

import pkg_resources
import usdex
from pxr import Sdf, Usd


class TestCase(unittest.TestCase):
    """
    A unittest base class to simplify testing common USD authoring functionality
    """

    maxDiff = None
    validFileIdentifierRegex = r"[^A-Za-z0-9_-]"

    def assertUsdLayerEncoding(self, layer: Sdf.Layer, encoding: str):
        """Assert that the given layer uses the given encoding type"""
        self.assertEqual(self.getUsdEncoding(layer), encoding)

    def tmpLayer(self, name: str = "", ext: str = "usda") -> Sdf.Layer:
        """
        Create a temporary Sdf.Layer on the local filesystem

            Args:
                name: an optional identifier prefix. If not provided the test name will be used
                ext: an optional file extension (excluding `.`) which must match a registered Sdf.FileFormatPlugin

            Returns:
                The Sdf.Layer object
        """
        return Sdf.Layer.CreateNew(self.tmpFile(name=name, ext="usda"))

    def tmpFile(self, name: str = "", ext: str = "") -> str:
        """
        Create a temporary file on the local filesystem

            Args:
                name: an optional filename prefix. If not provided the test name will be used
                ext: an optional file extension (excluding `.`)

            Returns:
                The filesystem path
        """
        tempDir = self.tmpBaseDir()
        if not os.path.exists(tempDir):
            os.makedirs(tempDir)

        # Sanitize name string
        name = re.sub(TestCase.validFileIdentifierRegex, "_", name or self._testMethodName)
        (handle, fileName) = tempfile.mkstemp(prefix=f"{os.path.join(tempDir, name)}_", suffix=f".{ext}")
        # closing the os handle immediately. we don't need this now that the file is known to be unique
        # and it interferes with some internal processes.
        os.close(handle)
        return fileName

    @staticmethod
    def isUsdOlderThan(version: str):
        """Determine if the provided versions is older than the current USD runtime"""
        return pkg_resources.parse_version(".".join([str(x) for x in Usd.GetVersion()])) < pkg_resources.parse_version(version)

    @staticmethod
    def tmpBaseDir() -> str:
        """Get the path of the base temp directory. All temp files and directories in the same process will be created under this directory.
        Returns:
            The filesystem path
        """
        # Sanitize Version string
        versionString = re.sub(TestCase.validFileIdentifierRegex, "_", usdex.core.version())

        # Create all subdirs under $TEMP
        pidString = os.environ.get("CI_PIPELINE_IID", os.getpid())
        subdirsPrefix = os.path.join("usdex", f"{versionString}-{pidString}")
        return os.path.join(tempfile.tempdir, subdirsPrefix)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpBaseDir(), ignore_errors=True)

    @staticmethod
    def getUsdEncoding(layer: Sdf.Layer):
        """Get the extension of the encoding type used within an SdfLayer"""
        fileFormat = layer.GetFileFormat()

        # If the encoding is explicit usda return that extension
        usdaFileFormat = Sdf.FileFormat.FindById("usda")
        if fileFormat == usdaFileFormat:
            return "usda"

        # If the encoding is explicit usdc return that extension
        usdcFileFormat = Sdf.FileFormat.FindById("usdc")
        if fileFormat == usdcFileFormat:
            return "usdc"

        # If the encoding is implicit check which of the explicit extensions can read the layer and return that type
        usdFileFormat = Sdf.FileFormat.FindById("usd")
        if fileFormat == usdFileFormat:
            if usdaFileFormat.CanRead(layer.identifier):
                return "usda"
            if usdcFileFormat.CanRead(layer.identifier):
                return "usdc"
