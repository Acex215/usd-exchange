# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import pathlib
import tempfile
import unittest
from abc import abstractmethod

import omni.asset_validator
import usdex.core
import usdex.test
from pxr import Gf, Kind, Sdf, Tf, Usd, UsdGeom, Vt


class TemporaryDirectoryChange:
    """Context manager for temporarily changing the current working directory."""

    def __init__(self, new_directory):
        self.new_directory = new_directory
        self.original_directory = None

    def __enter__(self):
        self.original_directory = os.getcwd()
        os.chdir(self.new_directory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_directory is not None:
            os.chdir(self.original_directory)


class AssetStructureTestBase:
    """Base class for asset structure tests, providing helper functions for creating temp files and getting relative identifiers."""

    def getRelativeIdentifier(self, sourceLayerIdentifier, referencingLayerIdentifier):
        try:
            relativePath = os.path.relpath(sourceLayerIdentifier, os.path.dirname(referencingLayerIdentifier)).replace(os.sep, "/")
            # all relative paths must be anchored
            if not os.path.isabs(relativePath) and not relativePath.startswith("."):
                relativePath = "./" + relativePath
            return relativePath
        except ValueError:
            # ValueError occurs when paths are on different mounts (e.g., different drives on Windows)
            return sourceLayerIdentifier

    def subDirTmpFile(self, subdirs: list = [], name: str = "", ext: str = "") -> str:
        # Helper function to create a temp file under the temp base dir within a subdir
        tempDir = pathlib.Path(self.tmpBaseDir())
        for subdir in subdirs:
            tempDir = tempDir / subdir
        tempDir.mkdir(parents=True, exist_ok=True)
        (handle, fileName) = tempfile.mkstemp(prefix=f"{os.path.join(tempDir, name)}_", suffix=f".{ext}")
        os.close(handle)
        return fileName


class GetAssetStructureTokensTestCase(usdex.test.TestCase):

    def testGetAssetToken(self):
        token = usdex.core.getAssetToken()
        self.assertEqual(token, "Asset")

    def testGetContentsToken(self):
        token = usdex.core.getContentsToken()
        self.assertEqual(token, "Contents")

    def testGetGeometryToken(self):
        token = usdex.core.getGeometryToken()
        self.assertEqual(token, "Geometry")

    def testGetLibraryToken(self):
        token = usdex.core.getLibraryToken()
        self.assertEqual(token, "Library")

    def testGetMaterialsToken(self):
        token = usdex.core.getMaterialsToken()
        self.assertEqual(token, "Materials")

    def testGetPayloadToken(self):
        token = usdex.core.getPayloadToken()
        self.assertEqual(token, "Payload")

    def testGetPhysicsToken(self):
        token = usdex.core.getPhysicsToken()
        self.assertEqual(token, "Physics")

    def testGetTexturesToken(self):
        token = usdex.core.getTexturesToken()
        self.assertEqual(token, "Textures")


class DefineScopeTestCase(usdex.test.DefineFunctionTestCase):

    # Configure the DefineFunctionTestCase
    defineFunc = usdex.core.defineScope
    requiredArgs = tuple()
    schema = UsdGeom.Scope
    typeName = "Scope"
    requiredPropertyNames = set()


class AssetStructureTestCase(usdex.test.TestCase):

    def setUp(self):
        super().setUp()
        self.validationEngine.enable_rule(omni.asset_validator.AnchoredAssetPathsChecker)
        self.validationEngine.enable_rule(omni.asset_validator.SupportedFileTypesChecker)

    def assertLayerNotRegistered(self, identifier):
        """Assert that an Sdf.Layer with a given identifier has not been registered"""
        self.assertFalse(Sdf.Layer.Find(identifier))

    def deleteStages(self, stageFiles: list[str]):
        """Delete a list of stages"""
        for stageFile in stageFiles:
            if os.path.exists(stageFile):
                os.remove(stageFile)

    def testInvalidAssetStage(self):
        # invalid asset stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid asset stage")]):
            assetPayloadStage = usdex.core.createAssetPayload(None)
        self.assertIsNone(assetPayloadStage)

        # anonymous asset stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*anonymous asset stage")]):
            assetStage = Usd.Stage.CreateInMemory()
            assetPayloadStage = usdex.core.createAssetPayload(assetStage)
        self.assertIsNone(assetPayloadStage)

    def testCreateAssetPayload(self):
        stageExtensions = ["usda", "usdc", "usd"]
        expectedEncodings = ["usda", "usdc", "usda"]  # note: "usd" extension will be encoded with "usda" intentionally (non-default)

        for stageExtension, expectedEncoding in zip(stageExtensions, expectedEncodings):
            assetStageIdentifier = self.tmpFile("test", stageExtension)

            assetStage = usdex.core.createStage(
                assetStageIdentifier,
                self.defaultPrimName,
                self.defaultUpAxis,
                self.defaultLinearUnits,
                self.defaultAuthoringMetadata,
            )
            self.assertIsInstance(assetStage, Usd.Stage)

            fileFormatArgs = {"format": expectedEncoding}
            assetPayloadStage = usdex.core.createAssetPayload(assetStage, stageExtension, fileFormatArgs)
            self.assertIsInstance(assetPayloadStage, Usd.Stage)

            assetPayloadStageIdentifier = f"{usdex.core.getPayloadToken()}/{usdex.core.getContentsToken()}.{stageExtension}"
            fullIdentifier = pathlib.Path(assetStageIdentifier).parent / assetPayloadStageIdentifier
            self.assertSdfLayerIdentifier(assetPayloadStage.GetRootLayer(), fullIdentifier)
            self.assertUsdLayerEncoding(assetPayloadStage.GetRootLayer(), expectedEncoding)
            self.assertTrue(usdex.core.hasLayerAuthoringMetadata(assetPayloadStage.GetRootLayer()))
            self.assertEqual(usdex.core.getLayerAuthoringMetadata(assetPayloadStage.GetRootLayer()), self.defaultAuthoringMetadata)
            self.assertIsValidUsd(assetPayloadStage)

            # cleanup
            assetStage = None
            assetPayloadStage = None
            self.deleteStages([assetStageIdentifier, fullIdentifier])

    def testInvalidPayloadStage(self):
        # invalid payload stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid payload stage")]):
            assetContentStage = usdex.core.addAssetContent(None, "test", "usda")
        self.assertIsNone(assetContentStage)

        # anonymous payload stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*anonymous payload stage")]):
            assetContentStage = usdex.core.addAssetContent(Usd.Stage.CreateInMemory(), "test", "usda")
        self.assertIsNone(assetContentStage)

    def testAddAssetContent(self):
        assetContentNames = [usdex.core.getGeometryToken(), usdex.core.getMaterialsToken(), usdex.core.getPhysicsToken()]
        stageExtensions = ["usda", "usdc", "usd"]
        expectedEncodings = ["usda", "usdc", "usda"]  # note: "usd" extension will be encoded with "usda" intentionally (non-default)

        for stageExtension, expectedEncoding in zip(stageExtensions, expectedEncodings):
            assetStageIdentifier = self.tmpFile("test", stageExtension)
            generatedFiles = [assetStageIdentifier]

            # create asset stage
            assetStage = usdex.core.createStage(
                assetStageIdentifier,
                self.defaultPrimName,
                self.defaultUpAxis,
                self.defaultLinearUnits,
                self.defaultAuthoringMetadata,
            )
            self.assertIsInstance(assetStage, Usd.Stage)

            # create asset payload stage
            assetPayloadStage = usdex.core.createAssetPayload(assetStage)
            self.assertIsInstance(assetPayloadStage, Usd.Stage)

            #################################
            # add asset content stage (prependLayer=True, createScope=True)
            fileFormatArgs = {"format": expectedEncoding}
            assetContentStage = usdex.core.addAssetContent(assetPayloadStage, assetContentNames[0], stageExtension, fileFormatArgs=fileFormatArgs)
            self.assertIsInstance(assetContentStage, Usd.Stage)

            # check that the asset content stage has the expected encoding
            self.assertUsdLayerEncoding(assetContentStage.GetRootLayer(), expectedEncoding)
            self.assertTrue(usdex.core.hasLayerAuthoringMetadata(assetContentStage.GetRootLayer()))
            self.assertEqual(usdex.core.getLayerAuthoringMetadata(assetContentStage.GetRootLayer()), self.defaultAuthoringMetadata)

            # check that the asset content stage is a sublayer of the asset payload stage
            relativeIdentifier = f"./{assetContentNames[0]}.{stageExtension}"
            subLayerPaths = assetPayloadStage.GetRootLayer().subLayerPaths
            # check that there is only one sublayer and that it's the correct identifier
            self.assertEqual(len(subLayerPaths), 1)
            self.assertEqual(subLayerPaths.index(relativeIdentifier), 0)

            # check that the asset content stage is the correct identifier
            expectedIdentifier = pathlib.Path(assetStageIdentifier).parent / usdex.core.getPayloadToken() / f"{assetContentNames[0]}.{stageExtension}"
            generatedFiles.append(expectedIdentifier)
            self.assertSdfLayerIdentifier(assetContentStage.GetRootLayer(), expectedIdentifier)

            # check that the asset content stage has a default prim and it's the correct name
            defaultPrim = assetContentStage.GetDefaultPrim()
            self.assertEqual(defaultPrim.GetName(), self.defaultPrimName)

            # check that the asset content stage has a correctly named scope
            prim = assetContentStage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(assetContentNames[0]))
            self.assertTrue(prim)
            scopePrim = UsdGeom.Scope(prim)
            self.assertTrue(scopePrim)

            #################################
            # add asset content stage (prependLayer=False, createScope=True)
            assetContentStage = usdex.core.addAssetContent(
                assetPayloadStage,
                assetContentNames[1],
                stageExtension,
                prependLayer=False,
                createScope=True,
            )
            self.assertIsInstance(assetContentStage, Usd.Stage)

            # check that the asset content stage is a sublayer of the asset payload stage
            relativeIdentifier = f"./{assetContentNames[1]}.{stageExtension}"
            subLayerPaths = assetPayloadStage.GetRootLayer().subLayerPaths
            # check that there are two sublayers and that the second one is the correct identifier
            self.assertEqual(len(subLayerPaths), 2)
            self.assertEqual(subLayerPaths.index(relativeIdentifier), 1)

            # check that the asset content stage is the correct identifier
            expectedIdentifier = pathlib.Path(assetStageIdentifier).parent / usdex.core.getPayloadToken() / f"{assetContentNames[1]}.{stageExtension}"
            generatedFiles.append(expectedIdentifier)
            self.assertSdfLayerIdentifier(assetContentStage.GetRootLayer(), expectedIdentifier)

            #################################
            # add asset content stage (prependLayer=True, createScope=False)
            assetContentStage = usdex.core.addAssetContent(
                assetPayloadStage,
                assetContentNames[2],
                stageExtension,
                prependLayer=True,
                createScope=False,
            )
            self.assertIsInstance(assetContentStage, Usd.Stage)

            # check that the asset content stage is a sublayer of the asset payload stage
            relativeIdentifier = f"./{assetContentNames[2]}.{stageExtension}"
            subLayerPaths = assetPayloadStage.GetRootLayer().subLayerPaths
            # check that there are three sublayers and that the third one is prepended at index 0
            self.assertEqual(len(subLayerPaths), 3)
            self.assertEqual(subLayerPaths.index(relativeIdentifier), 0)

            # check that the asset content stage is the correct identifier
            expectedIdentifier = pathlib.Path(assetStageIdentifier).parent / usdex.core.getPayloadToken() / f"{assetContentNames[2]}.{stageExtension}"
            generatedFiles.append(expectedIdentifier)
            self.assertSdfLayerIdentifier(assetContentStage.GetRootLayer(), expectedIdentifier)

            # check that the asset content stage has a default prim and it's the correct name
            defaultPrim = assetContentStage.GetDefaultPrim()
            self.assertEqual(defaultPrim.GetName(), self.defaultPrimName)

            # check that no scope was created (createScope=False)
            prim = assetContentStage.GetPrimAtPath(defaultPrim.GetPath().AppendChild(assetContentNames[2]))
            self.assertFalse(prim)

            self.assertIsValidUsd(assetContentStage)

            # cleanup
            assetStage = None
            assetPayloadStage = None
            assetContentStage = None
            self.deleteStages(generatedFiles)


class AddAssetLibraryTestCase(usdex.test.TestCase):

    def setUp(self):
        super().setUp()
        self.validationEngine.enable_rule(omni.asset_validator.AnchoredAssetPathsChecker)
        self.validationEngine.enable_rule(omni.asset_validator.SupportedFileTypesChecker)

    def deleteStages(self, stageFiles: list[str]):
        """Delete a list of stages"""
        for stageFile in stageFiles:
            if os.path.exists(stageFile):
                os.remove(stageFile)

    def testInvalidPayloadStage(self):
        # invalid payload stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid content stage")]):
            assetLibraryStage = usdex.core.addAssetLibrary(None, "test")
        self.assertIsNone(assetLibraryStage)

        # anonymous payload stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*anonymous content stage")]):
            assetLibraryStage = usdex.core.addAssetLibrary(Usd.Stage.CreateInMemory(), "test")
        self.assertIsNone(assetLibraryStage)

    def testAddAssetLibrary(self):
        libraryName = usdex.core.getGeometryToken()
        formats = ["usda", "usdc", "usd"]
        expectedEncodings = ["usda", "usdc", "usda"]  # note: "usd" extension will be encoded with "usda" intentionally (non-default)

        for format, expectedEncoding in zip(formats, expectedEncodings):
            payloadStageIdentifier = self.tmpFile(f"{usdex.core.getPayloadToken()}/{usdex.core.getContentsToken()}", "usda")

            # create payload stage directly
            payloadStage = usdex.core.createStage(
                payloadStageIdentifier,
                self.defaultPrimName,
                self.defaultUpAxis,
                self.defaultLinearUnits,
                self.defaultAuthoringMetadata,
            )
            self.assertIsInstance(payloadStage, Usd.Stage)

            # test with explicit format
            fileFormatArgs = {"format": expectedEncoding}
            assetLibraryStage = usdex.core.addAssetLibrary(payloadStage, libraryName, format, fileFormatArgs)
            self.assertIsInstance(assetLibraryStage, Usd.Stage)

            # check that the library stage file path is correct
            expectedLibraryIdentifier = pathlib.Path(payloadStageIdentifier).parent / f"{libraryName}{usdex.core.getLibraryToken()}.{format}"
            self.assertSdfLayerIdentifier(assetLibraryStage.GetRootLayer(), expectedLibraryIdentifier)

            # check that the library stage has the correct encoding
            self.assertUsdLayerEncoding(assetLibraryStage.GetRootLayer(), expectedEncoding)

            # check that the library stage has the correct default prim name and it has a class specifier
            defaultPrim = assetLibraryStage.GetDefaultPrim()
            self.assertEqual(defaultPrim.GetName(), libraryName)
            self.assertEqual(defaultPrim.GetSpecifier(), Sdf.SpecifierClass)

            # check stage metadata
            self.assertEqual(UsdGeom.GetStageUpAxis(assetLibraryStage), self.defaultUpAxis)
            self.assertEqual(UsdGeom.GetStageMetersPerUnit(assetLibraryStage), self.defaultLinearUnits)
            self.assertTrue(usdex.core.hasLayerAuthoringMetadata(assetLibraryStage.GetRootLayer()))
            self.assertEqual(usdex.core.getLayerAuthoringMetadata(assetLibraryStage.GetRootLayer()), self.defaultAuthoringMetadata)

            self.assertIsValidUsd(payloadStage)

            # cleanup
            payloadStage = None
            assetLibraryStage = None
            self.deleteStages([payloadStageIdentifier, expectedLibraryIdentifier])

    def testAddAssetLibraryDefaultFormat(self):
        libraryName = usdex.core.getGeometryToken()
        payloadStageIdentifier = self.tmpFile(f"{usdex.core.getPayloadToken()}/{usdex.core.getContentsToken()}", "usda")

        # create payload stage directly
        payloadStage = usdex.core.createStage(
            payloadStageIdentifier,
            self.defaultPrimName,
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        self.assertIsInstance(payloadStage, Usd.Stage)

        # test with default format (usdc)
        assetLibraryStage = usdex.core.addAssetLibrary(payloadStage, libraryName)
        self.assertIsInstance(assetLibraryStage, Usd.Stage)

        # check that the library stage file path is correct (should use usdc by default)
        expectedLibraryIdentifier = pathlib.Path(payloadStageIdentifier).parent / f"{libraryName}{usdex.core.getLibraryToken()}.usdc"
        self.assertSdfLayerIdentifier(assetLibraryStage.GetRootLayer(), expectedLibraryIdentifier)

        # check that the library stage has the correct encoding (usdc by default)
        self.assertUsdLayerEncoding(assetLibraryStage.GetRootLayer(), "usdc")
        self.assertIsValidUsd(payloadStage)


class AddAssetInterfaceTestCase(usdex.test.TestCase, AssetStructureTestBase):

    def setUp(self):
        super().setUp()
        self.validationEngine.enable_rule(omni.asset_validator.AnchoredAssetPathsChecker)
        self.validationEngine.enable_rule(omni.asset_validator.SupportedFileTypesChecker)

    def testInvalidStages(self):
        assetStageIdentifier = self.tmpFile("testAsset", "usda")
        assetStage = usdex.core.createStage(
            assetStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )

        payloadStageIdentifier = self.tmpFile(f"{usdex.core.getPayloadToken()}/{usdex.core.getContentsToken()}", "usda")
        payloadStage = usdex.core.createStage(
            payloadStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        # Test with both stages invalid
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid stage")]):
            success = usdex.core.addAssetInterface(None, None)
            self.assertFalse(success)

        # Test with invalid asset stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid stage")]):
            success = usdex.core.addAssetInterface(None, payloadStage)
            self.assertFalse(success)

        # Test with invalid payload stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid source stage")]):
            success = usdex.core.addAssetInterface(assetStage, None)
            self.assertFalse(success)

        # Test with anonymous stages
        anonymousAssetStage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(anonymousAssetStage, "testAsset", self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)

        anonymousPayloadStage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(anonymousPayloadStage, "testAsset", self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)

        # Test with both stages anonymous
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*anonymous stage")]):
            success = usdex.core.addAssetInterface(anonymousAssetStage, anonymousPayloadStage)
            self.assertFalse(success)

        # Test with anonymous asset stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*anonymous stage")]):
            success = usdex.core.addAssetInterface(anonymousAssetStage, payloadStage)
            self.assertFalse(success)

        # Test with anonymous payload stage
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*anonymous source stage")]):
            success = usdex.core.addAssetInterface(assetStage, anonymousPayloadStage)
            self.assertFalse(success)

    def testAddAssetInterface(self):
        # Create asset stage with "testAsset" as the name
        assetStageIdentifier = self.tmpFile("testAsset", "usda")
        assetStage = usdex.core.createStage(
            assetStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        self.assertIsInstance(assetStage, Usd.Stage)

        # Create payload stage using createAssetPayload
        payloadStage = usdex.core.createAssetPayload(assetStage)
        self.assertIsInstance(payloadStage, Usd.Stage)

        # Jumble the asset stage configuration
        usdex.core.configureStage(assetStage, "wrongName", UsdGeom.Tokens.z, UsdGeom.LinearUnits.feet, "not the default metadata")

        # Add asset interface
        success = usdex.core.addAssetInterface(assetStage, payloadStage)
        self.assertTrue(success)

        # Remove the bad prim so the asset validator doesn't fail later
        assetStage.RemovePrim("/wrongName")

        # Verify the asset stage configuration
        self.assertEqual(assetStage.GetDefaultPrim().GetName(), "testAsset")
        self.assertEqual(UsdGeom.GetStageUpAxis(assetStage), self.defaultUpAxis)
        self.assertEqual(UsdGeom.GetStageMetersPerUnit(assetStage), self.defaultLinearUnits)
        self.assertTrue(usdex.core.hasLayerAuthoringMetadata(assetStage.GetRootLayer()))
        self.assertEqual(usdex.core.getLayerAuthoringMetadata(assetStage.GetRootLayer()), self.defaultAuthoringMetadata)

        # Verify payload was added
        defaultPrim = assetStage.GetDefaultPrim()
        self.assertTrue(defaultPrim.HasPayload())
        payloads = defaultPrim.GetPayloads()
        self.assertTrue(payloads)

        # Verify USD Model API was applied and kind is set to component
        modelAPI = Usd.ModelAPI(defaultPrim)
        self.assertEqual(modelAPI.GetKind(), Kind.Tokens.component)

        geomModel = UsdGeom.ModelAPI(defaultPrim)
        self.assertTrue(geomModel)

        # Get the extents hint attribute
        extentsHintAttr = geomModel.GetExtentsHintAttr()
        self.assertTrue(extentsHintAttr)

        # Get the extents hint value
        extentsValue = extentsHintAttr.Get()
        self.assertTrue(extentsValue)
        self.assertIsInstance(extentsValue, Vt.Vec3fArray)

        self.assertAlmostEqual(extentsValue[0], Gf.Range3f().GetMin())
        self.assertAlmostEqual(extentsValue[1], Gf.Range3f().GetMax())

        self.assertIsValidUsd(assetStage)

    def testExtentsWithGeometry(self):
        # Create asset stage with "testAsset" as the name
        assetStageIdentifier = self.tmpFile("testAsset", "usda")
        assetStage = usdex.core.createStage(
            assetStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        self.assertIsInstance(assetStage, Usd.Stage)

        # Create payload stage using createAssetPayload
        payloadStage = usdex.core.createAssetPayload(assetStage)
        self.assertIsInstance(payloadStage, Usd.Stage)

        # Add geometry content stage
        geometryStage = usdex.core.addAssetContent(payloadStage, "Geometry", "usda")
        self.assertIsInstance(geometryStage, Usd.Stage)

        # Create some geometry in the geometry stage
        defaultPrim = geometryStage.GetDefaultPrim()
        geometryScope = geometryStage.GetPrimAtPath(defaultPrim.GetPath().AppendChild("Geometry"))

        # Add gprims with different purposes to test extentsHint computation
        from pxr import Gf, Vt

        # Create a cube with default purpose (at origin)
        cube = UsdGeom.Cube.Define(geometryStage, geometryScope.GetPath().AppendChild("Cube"))
        self.assertTrue(cube)
        cube.CreateSizeAttr().Set(10.0)
        UsdGeom.Imageable(cube).CreatePurposeAttr().Set(UsdGeom.Tokens.default_)

        # Create a sphere with render purpose (offset to x=2)
        sphere = UsdGeom.Sphere.Define(geometryStage, geometryScope.GetPath().AppendChild("Sphere"))
        self.assertTrue(sphere)
        sphere.CreateRadiusAttr().Set(5.0)
        usdex.core.setLocalTransform(sphere.GetPrim(), Gf.Transform(Gf.Vec3d(2.0, 0.0, 0.0)))
        UsdGeom.Imageable(sphere).CreatePurposeAttr().Set(UsdGeom.Tokens.render)

        # Create a cylinder with proxy purpose (offset to x=-2)
        cylinder = UsdGeom.Cylinder.Define(geometryStage, geometryScope.GetPath().AppendChild("ProxyCylinder"))
        self.assertTrue(cylinder)
        cylinder.CreateRadiusAttr().Set(0.5)
        cylinder.CreateHeightAttr().Set(1.0)
        usdex.core.setLocalTransform(cylinder.GetPrim(), Gf.Transform(Gf.Vec3d(-2.0, 0.0, 0.0)))
        UsdGeom.Imageable(cylinder).CreatePurposeAttr().Set(UsdGeom.Tokens.proxy)

        # Create a cone with guide purpose (offset to y=2)
        cone = UsdGeom.Cone.Define(geometryStage, geometryScope.GetPath().AppendChild("GuideCone"))
        self.assertTrue(cone)
        cone.CreateRadiusAttr().Set(0.5)
        cone.CreateHeightAttr().Set(1.0)
        usdex.core.setLocalTransform(cone.GetPrim(), Gf.Transform(Gf.Vec3d(0.0, 2.0, 0.0)))
        UsdGeom.Imageable(cone).CreatePurposeAttr().Set(UsdGeom.Tokens.guide)

        # Add asset interface
        success = usdex.core.addAssetInterface(assetStage, payloadStage)
        self.assertTrue(success)

        # Verify the asset stage configuration
        self.assertEqual(assetStage.GetDefaultPrim().GetName(), "testAsset")
        self.assertEqual(UsdGeom.GetStageUpAxis(assetStage), self.defaultUpAxis)
        self.assertEqual(UsdGeom.GetStageMetersPerUnit(assetStage), self.defaultLinearUnits)

        # Verify payload was added
        defaultPrim = assetStage.GetDefaultPrim()
        self.assertTrue(defaultPrim.HasPayload())

        # Verify extents hint was computed for different purposes
        geomModel = UsdGeom.ModelAPI(defaultPrim)
        self.assertTrue(geomModel)

        # Get the extents hint attribute
        extentsHintAttr = geomModel.GetExtentsHintAttr()
        self.assertTrue(extentsHintAttr)

        # Get the extents hint value
        extentsValue = extentsHintAttr.Get()
        self.assertTrue(extentsValue)
        self.assertIsInstance(extentsValue, Vt.Vec3fArray)

        bboxCache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), UsdGeom.Imageable(defaultPrim).GetOrderedPurposeTokens())
        expectedExtents = geomModel.ComputeExtentsHint(bboxCache)
        self.assertListEqual(list(extentsValue), list(expectedExtents))

        self.assertIsValidUsd(assetStage)
        self.assertIsValidUsd(payloadStage)
        self.assertIsValidUsd(geometryStage)

    def testRelativePathsUp(self):
        # Check that relative paths are correct if the asset stage is below the payload stage (probably not a good idea)
        assetStageIdentifier = self.subDirTmpFile(subdirs=["foo", "bar"], name="testAsset", ext="usda")
        assetStage = usdex.core.createStage(
            assetStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )

        payloadStageIdentifier = self.subDirTmpFile(subdirs=[usdex.core.getPayloadToken()], name=usdex.core.getContentsToken(), ext="usda")
        payloadStage = usdex.core.createStage(
            payloadStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )

        success = usdex.core.addAssetInterface(assetStage, payloadStage)
        self.assertTrue(success)

        # Verify payload was added and is relative to the asset stage
        defaultPrim = assetStage.GetDefaultPrim()
        self.assertTrue(defaultPrim.HasPayload())

        rootLayer = assetStage.GetRootLayer()
        primSpec = rootLayer.GetPrimAtPath(defaultPrim.GetPath())

        payloadList = primSpec.payloadList.prependedItems
        self.assertTrue(payloadList)
        self.assertEqual(len(payloadList), 1)

        relativePath = self.getRelativeIdentifier(payloadStageIdentifier, assetStageIdentifier)
        self.assertEqual(payloadList[0].assetPath, relativePath)

        # AnchoredAssetPathsChecker will fail for this test since the relative payloads go outside the asset root.
        # "../../Payload/Contents.usda" in this case
        # /Payload/
        #   Contents.usda <-----+
        # /foo/                 |
        #   bar/                |
        #     testAsset.usda ---+
        self.assertIsValidUsd(
            assetStage,
            issuePredicates=[omni.asset_validator.IssuePredicates.ContainsMessage("is outside of the asset root")],
        )
        self.assertIsValidUsd(payloadStage)

    def testRelativePathsUpDown(self):
        assetStageIdentifier = self.tmpFile("testAsset", "usda")
        assetStage = usdex.core.createStage(
            assetStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )

        payloadStageIdentifier = self.subDirTmpFile(
            subdirs=[usdex.core.getPayloadToken(), "foo", "bar"],
            name=usdex.core.getContentsToken(),
            ext="usda",
        )
        payloadStage = usdex.core.createStage(
            payloadStageIdentifier,
            "testAsset",
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )

        success = usdex.core.addAssetInterface(assetStage, payloadStage)
        self.assertTrue(success)

        # Verify payload was added and is relative to the asset stage
        defaultPrim = assetStage.GetDefaultPrim()
        self.assertTrue(defaultPrim.HasPayload())

        rootLayer = assetStage.GetRootLayer()
        primSpec = rootLayer.GetPrimAtPath(defaultPrim.GetPath())

        payloadList = primSpec.payloadList.prependedItems
        self.assertTrue(payloadList)
        self.assertEqual(len(payloadList), 1)

        relativePath = self.getRelativeIdentifier(payloadStageIdentifier, assetStageIdentifier)
        self.assertEqual(payloadList[0].assetPath, relativePath)

        self.assertIsValidUsd(assetStage)
        self.assertIsValidUsd(payloadStage)


class DefineReferencePayloadBase(AssetStructureTestBase):
    """Base class for defineReference and definePayload tests.

    This class provides a base class for defineReference and definePayload tests.
    It provides a common interface for defining references and payloads.

    The child classes must implement the defineReferencePayloadFunc and getReferencePayloadList methods.
    This class rearranges the arguments to the defineReferencePayloadFunc to match the expected argument
    order for the DefineFunctionTestCase class.
    """

    @property
    @abstractmethod
    def defineReferencePayloadFunc(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def getReferencePayloadList(self, prim):
        raise NotImplementedError()

    # This function rearranges the arguments to the defineReferencePayloadFunc to match the expected argument
    # order for the DefineFunctionTestCase class.
    def defineReferenceWrapper(self, *args):
        if len(args) == 3 and isinstance(args[1], Sdf.Path):  # (stage, path, source)
            stage, path, source = args
            return self.defineReferencePayloadFunc(stage, path, source)
        elif len(args) == 3:  # (parent, name, source)
            parent, name, source = args
            return self.defineReferencePayloadFunc(parent, source, name)
        else:
            raise ValueError(f"Unexpected arguments: {args}")

    # Configure the DefineFunctionTestCase
    defineFunc = defineReferenceWrapper
    schema = Usd.Prim
    typeName = "Xform"
    requiredPropertyNames = set()

    def setUp(self):
        super().setUp()

        self.sourcePrimName = "SourceXform"
        self.sourceStage = usdex.core.createStage(
            self.tmpFile("source", "usda"),
            self.sourcePrimName,
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        self.sourceXform = usdex.core.defineXform(self.sourceStage.GetPseudoRoot(), self.sourcePrimName)

    # Configure the DefineFunctionTestCase
    @property
    def requiredArgs(self):
        """A tuple of valid values for the required arguments"""
        return (self.sourceXform.GetPrim(),)

    # Add to the DefineFunctionTestCase methods
    def assertDefineFunctionSuccess(self, result):
        """Assert the common expectations of a successful call to defineBasisCurves"""
        super().assertDefineFunctionSuccess(result)

        # The name check here isn't really verifying anything because the base class picks a name for us
        self.assertReferencePayload(
            result,
            result.GetPath(),
            self.sourceXform.GetPrim(),
            result.GetName(),
        )

    # Override this because defineReference() already has a (prim, prim) overload
    def testDefineFromInvalidPrim(self):
        pass

    # Override this because defineReference() already has a (prim, prim) overload
    # Prim redefinition is tested in testRepeatedCalls()
    def testRedefinePrim(self):
        pass

    def assertReferencePayload(self, prim: Usd.Prim, primPath: Sdf.Path, sourcePrim: Usd.Prim, name: str, listIndex: int = 0):
        """Assert the common expectations of a successful call to defineReferencePayloadFunc.

        Args:
            prim: The prim that was defined
            primPath: The path of the prim that was defined
            sourcePrim: The source prim that was referenced
            name: The name of the prim that was defined
            listIndex: The index of the last reference in the reference list, used to check the list length and the last reference
        """
        self.assertTrue(prim)
        self.assertEqual(prim.GetName(), name)
        self.assertEqual(prim.GetTypeName(), sourcePrim.GetTypeName())
        self.assertEqual(prim.GetSpecifier(), sourcePrim.GetSpecifier())
        self.assertEqual(prim.GetPath(), primPath)

        refList = self.getReferencePayloadList(prim)
        self.assertTrue(refList)
        self.assertEqual(len(refList), listIndex + 1)

        expectedPath = self.getRelativeIdentifier(
            sourcePrim.GetStage().GetRootLayer().identifier,
            prim.GetStage().GetEditTarget().GetLayer().identifier,
        )

        # Check for internal references
        if prim.GetStage().GetRootLayer().identifier == sourcePrim.GetStage().GetRootLayer().identifier:
            self.assertEqual(refList[listIndex].assetPath, "")
        else:
            self.assertEqual(refList[listIndex].assetPath, expectedPath)

        # Check that the reference's primPath is correct
        if sourcePrim.GetPath() == sourcePrim.GetStage().GetDefaultPrim().GetPath():
            self.assertEqual(refList[listIndex].primPath, Sdf.Path())
        else:
            self.assertEqual(refList[listIndex].primPath, sourcePrim.GetPath())

    def testSameDirectory(self):
        self.validationEngine.enable_rule(omni.asset_validator.AnchoredAssetPathsChecker)
        self.validationEngine.enable_rule(omni.asset_validator.SupportedFileTypesChecker)

        referencingStageIdentifier = self.tmpFile("referencing", "usda")
        referencingStage = usdex.core.createStage(
            referencingStageIdentifier, self.sourcePrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata
        )

        sourceXformB = usdex.core.defineXform(self.sourceStage.GetPseudoRoot(), self.sourcePrimName)

        # test both (stage, path, source) and (parent, source) args
        # source could be a default prim or a non-default prim
        argsList = [
            (referencingStage.GetPseudoRoot(), self.sourceXform.GetPrim()),
            (referencingStage, referencingStage.GetDefaultPrim().GetPath(), self.sourceXform.GetPrim()),
            (referencingStage.GetPseudoRoot(), sourceXformB.GetPrim()),
            (referencingStage, referencingStage.GetDefaultPrim().GetPath(), sourceXformB.GetPrim()),
        ]
        for args in argsList:
            referencePrim = self.defineReferencePayloadFunc(*args)

            if len(args) == 2:
                sourcePrim = args[1]
            else:
                sourcePrim = args[2]

            self.assertReferencePayload(
                referencePrim,
                referencingStage.GetDefaultPrim().GetPath(),
                sourcePrim,
                sourcePrim.GetName(),
            )

            self.assertIsValidUsd(referencingStage)
            referencingStage.RemovePrim(referencePrim.GetPath())

        self.assertIsValidUsd(self.sourceStage)

    def testInternalReference(self):
        self.validationEngine.enable_rule(omni.asset_validator.AnchoredAssetPathsChecker)
        self.validationEngine.enable_rule(omni.asset_validator.SupportedFileTypesChecker)
        stageIdentifier = self.tmpFile("referencing", "usda")
        stage = usdex.core.createStage(
            stageIdentifier, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata
        )
        defaultPrim = usdex.core.defineScope(stage.GetPseudoRoot(), self.defaultPrimName)

        stage.CreateClassPrim("/Prototypes")
        sourceXform = UsdGeom.Xform.Define(stage, f"/Prototypes/{self.sourcePrimName}")

        # test both (stage, path, source) and (parent, source) args
        argsList = [
            (stage.GetDefaultPrim(), sourceXform.GetPrim()),
            (stage, stage.GetDefaultPrim().GetPath().AppendChild(self.sourcePrimName), sourceXform.GetPrim()),
        ]
        for args in argsList:
            referencePrim = self.defineReferencePayloadFunc(*args)

            self.assertReferencePayload(
                referencePrim,
                stage.GetDefaultPrim().GetPath().AppendChild(self.sourcePrimName),
                sourceXform.GetPrim(),
                sourceXform.GetPrim().GetName(),
            )

            self.assertIsValidUsd(stage)
            stage.RemovePrim(referencePrim.GetPath())

        # check that the prim can't reference itself
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*pointing to itself")]):
            referencePrim = self.defineReferencePayloadFunc(stage, defaultPrim.GetPath(), defaultPrim.GetPrim())
        self.assertFalse(referencePrim)

        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*pointing to itself")]):
            referencePrim = self.defineReferencePayloadFunc(defaultPrim.GetPrim().GetParent(), defaultPrim.GetPrim())
        self.assertFalse(referencePrim)

    def testAnonymousStages(self):
        referencingStageIdentifier = self.tmpFile("referencing", "usda")
        referencingStage = usdex.core.createStage(
            referencingStageIdentifier, self.sourcePrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata
        )

        anonStage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(anonStage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        anonScope = usdex.core.defineScope(anonStage.GetPseudoRoot(), self.sourcePrimName)

        # anonymous referencing stage (stage, path, source)
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*anonymous referencing stage")]):
            referencePrim = self.defineReferencePayloadFunc(anonStage, anonScope.GetPrim().GetPath(), self.sourceXform.GetPrim())
        self.assertFalse(referencePrim)

        # anonymous referencing stage (parent, source)
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*anonymous referencing stage")]):
            referencePrim = self.defineReferencePayloadFunc(anonScope.GetPrim().GetParent(), self.sourceXform.GetPrim())
        self.assertFalse(referencePrim)

        # anonymous source (stage, path, source)
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*anonymous source stage")]):
            referencePrim = self.defineReferencePayloadFunc(referencingStage, referencingStage.GetDefaultPrim().GetPath(), anonScope.GetPrim())
        self.assertFalse(referencePrim)

        # anonymous source (parent, source)
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*anonymous source stage")]):
            referencePrim = self.defineReferencePayloadFunc(referencingStage.GetPseudoRoot(), anonScope.GetPrim())
        self.assertFalse(referencePrim)

    def testLayersFromDifferentDirectories(self):
        # Test that references defined in different layers with different relative paths are supported
        # Create a source model stage (tmp/assets/models/source.usda)
        # Create a multilayer stage with a sublayer in a different directory than the root layer
        # root - (tmp/scenes/scene.usda)
        # layer - (tmp/scenes/layers/layer.usda)

        # Create source stage in assets/models/ directory
        sourceStageIdentifier = self.subDirTmpFile(subdirs=["assets", "models"], name="source", ext="usda")
        sourceStage = usdex.core.createStage(
            sourceStageIdentifier,
            self.sourcePrimName,
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        sourceXform = usdex.core.defineXform(sourceStage.GetPseudoRoot(), self.sourcePrimName)

        # Create layered stage structure
        rootLayerIdentifier = self.subDirTmpFile(subdirs=["scenes"], name="scene", ext="usda")
        layerIdentifier = self.subDirTmpFile(subdirs=["scenes", "layers"], name="layer", ext="usda")

        # Create the individual layers
        rootLayer = Sdf.Layer.CreateNew(rootLayerIdentifier)
        layer = Sdf.Layer.CreateNew(layerIdentifier)

        # Set up sublayer relationships using relative paths from the actual filenames
        layerRelativePath = self.getRelativeIdentifier(layerIdentifier, rootLayerIdentifier)
        rootLayer.subLayerPaths.append(layerRelativePath)

        # Open the stage
        stage = Usd.Stage.Open(rootLayer)

        # Configure the stage in the root layer
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)

        # Define a reference in the root layer
        stage.SetEditTarget(Usd.EditTarget(rootLayer))
        rootRef = self.defineReferencePayloadFunc(stage.GetDefaultPrim(), sourceXform.GetPrim())
        self.assertReferencePayload(
            rootRef,
            stage.GetDefaultPrim().GetPath().AppendChild(sourceXform.GetPrim().GetName()),
            sourceXform.GetPrim(),
            sourceXform.GetPrim().GetName(),
        )

        # Define a reference in the layer
        stage.SetEditTarget(Usd.EditTarget(layer))
        layerPrim = self.defineReferencePayloadFunc(stage.GetDefaultPrim(), sourceXform.GetPrim(), "LayerRef")
        self.assertReferencePayload(
            layerPrim,
            stage.GetDefaultPrim().GetPath().AppendChild("LayerRef"),
            sourceXform.GetPrim(),
            "LayerRef",
        )

        # Verify the stage is valid
        self.assertIsValidUsd(stage)
        self.assertIsValidUsd(sourceStage)

    def testPrimName(self):
        # Test that the optional name argument is supported
        stage = self.createTestStage()
        parent = stage.GetDefaultPrim()

        # When None is passed (default), name should match source prim
        refPrim = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim())
        self.assertReferencePayload(
            refPrim,
            parent.GetPath().AppendChild(self.sourceXform.GetPrim().GetName()),
            self.sourceXform.GetPrim(),
            self.sourceXform.GetPrim().GetName(),
        )

        # When a valid name is passed, name should match that value
        refPrim = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim(), "CustomName")
        self.assertReferencePayload(
            refPrim,
            parent.GetPath().AppendChild("CustomName"),
            self.sourceXform.GetPrim(),
            "CustomName",
        )

        # When an invalid name is passed (spaces), should return invalid prim
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*not a valid prim name")]):
            refPrim = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim(), "Invalid Name")
        self.assertFalse(refPrim)

        # When empty string is passed, should return invalid prim
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*not a valid prim name")]):
            refPrim = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim(), "")
        self.assertFalse(refPrim)

        # When name starting with number is passed, should return invalid prim
        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*not a valid prim name")]):
            refPrim = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim(), "123InvalidStart")
        self.assertFalse(refPrim)

        self.assertIsValidUsd(stage)

    def testRepeatedCalls(self):
        self.validationEngine.enable_rule(omni.asset_validator.AnchoredAssetPathsChecker)
        self.validationEngine.enable_rule(omni.asset_validator.SupportedFileTypesChecker)

        # Test that repeated calls do a reasonable thing
        stage = self.createTestStage()
        parent = stage.GetDefaultPrim()

        # When None is passed (default), name should match source prim
        refPrim1 = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim())
        self.assertReferencePayload(
            refPrim1,
            parent.GetPath().AppendChild(self.sourceXform.GetPrim().GetName()),
            self.sourceXform.GetPrim(),
            self.sourceXform.GetPrim().GetName(),
        )

        # Repeated calls with the same source prim shouldn't add to the reference list (thanks to SdfListOp behavior)
        refPrim2 = self.defineReferencePayloadFunc(parent, self.sourceXform.GetPrim())
        self.assertReferencePayload(
            refPrim2,
            parent.GetPath().AppendChild(self.sourceXform.GetPrim().GetName()),
            self.sourceXform.GetPrim(),
            self.sourceXform.GetPrim().GetName(),
        )

        # Create another source prim and add another reference to the prim
        sourcePrimNameB = "SourceXformB"
        sourceXformB = usdex.core.defineXform(self.sourceXform.GetPrim().GetParent(), sourcePrimNameB)
        refPrim3 = self.defineReferencePayloadFunc(parent, sourceXformB.GetPrim(), self.sourcePrimName)

        self.assertReferencePayload(
            refPrim3,
            parent.GetPath().AppendChild(self.sourcePrimName),
            sourceXformB.GetPrim(),
            self.sourcePrimName,
            listIndex=1,
        )

        # Create a source prim of a different type and add another reference to the prim
        sourceScopeNameC = "SourceScopeC"
        sourceScopeC = usdex.core.defineScope(self.sourceXform.GetPrim().GetStage().GetPseudoRoot(), sourceScopeNameC)
        refPrim4 = self.defineReferencePayloadFunc(parent, sourceScopeC.GetPrim(), self.sourcePrimName)

        self.assertReferencePayload(
            refPrim4,
            parent.GetPath().AppendChild(self.sourcePrimName),
            sourceScopeC.GetPrim(),
            self.sourcePrimName,
            listIndex=2,
        )

    def testUnicodeIdentifiers(self):
        sourceStageIdentifier = self.subDirTmpFile(subdirs=["🚀"], name="👽", ext="usda")
        sourceStage = usdex.core.createStage(
            sourceStageIdentifier,
            self.sourcePrimName,
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        sourceXform = usdex.core.defineXform(sourceStage.GetPseudoRoot(), self.sourcePrimName)
        stage = self.createTestStage()
        parent = stage.GetDefaultPrim()
        refPrim = self.defineReferencePayloadFunc(parent, sourceXform.GetPrim())
        self.assertReferencePayload(
            refPrim,
            parent.GetPath().AppendChild(sourceXform.GetPrim().GetName()),
            sourceXform.GetPrim(),
            sourceXform.GetPrim().GetName(),
        )

    @unittest.skip("Disabled because we can't generate stages on different mounts in the test environment")
    def testNoRelativePath(self):
        sourceStageIdentifier = "X:/tmp/source_asdf.usda"
        sourceStage = usdex.core.createStage(
            sourceStageIdentifier,
            self.sourcePrimName,
            self.defaultUpAxis,
            self.defaultLinearUnits,
            self.defaultAuthoringMetadata,
        )
        sourceXform = usdex.core.defineXform(sourceStage.GetPseudoRoot(), self.sourcePrimName)
        stage = self.createTestStage()
        parent = stage.GetDefaultPrim()
        refPrim = self.defineReferencePayloadFunc(parent, sourceXform.GetPrim())
        self.assertReferencePayload(
            refPrim,
            parent.GetPath().AppendChild(sourceXform.GetPrim().GetName()),
            sourceXform.GetPrim(),
            sourceXform.GetPrim().GetName(),
        )

    def testSameLocalPath(self):
        # Test when a stage identifier is a relative path in the current working directory
        with TemporaryDirectoryChange(self.tmpBaseDir()):
            sourceStageIdentifier = "source.usda"
            sourceStage = usdex.core.createStage(
                sourceStageIdentifier,
                self.sourcePrimName,
                self.defaultUpAxis,
                self.defaultLinearUnits,
                self.defaultAuthoringMetadata,
            )
            self.assertIsInstance(sourceStage, Usd.Stage)
            sourceXform = usdex.core.defineXform(sourceStage.GetDefaultPrim())

            refStageIdentifier = "ref.usda"
            refStage = usdex.core.createStage(
                refStageIdentifier,
                self.sourcePrimName,
                self.defaultUpAxis,
                self.defaultLinearUnits,
                self.defaultAuthoringMetadata,
            )
            self.assertIsInstance(refStage, Usd.Stage)

            refPrim = self.defineReferencePayloadFunc(refStage.GetDefaultPrim(), sourceStage.GetDefaultPrim())
            self.assertIsInstance(refPrim, Usd.Prim)
            self.assertReferencePayload(
                refPrim,
                refStage.GetDefaultPrim().GetPath().AppendChild(self.sourcePrimName),
                sourceXform.GetPrim(),
                self.sourcePrimName,
            )


class DefineReferenceTestCase(DefineReferencePayloadBase, usdex.test.DefineFunctionTestCase):

    defineReferencePayloadFunc = usdex.core.defineReference

    def getReferencePayloadList(self, prim):
        primSpec = prim.GetStage().GetEditTarget().GetLayer().GetPrimAtPath(prim.GetPath())
        return primSpec.referenceList.prependedItems


class DefinePayloadTestCase(DefineReferencePayloadBase, usdex.test.DefineFunctionTestCase):

    defineReferencePayloadFunc = usdex.core.definePayload

    def getReferencePayloadList(self, prim):
        primSpec = prim.GetStage().GetEditTarget().GetLayer().GetPrimAtPath(prim.GetPath())
        return primSpec.payloadList.prependedItems
