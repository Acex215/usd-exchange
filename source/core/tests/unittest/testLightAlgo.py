# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import pathlib

import usdex.core
import usdex.test
from pxr import Sdf, Tf, Usd, UsdGeom, UsdLux, UsdShade


class LightAlgoTest(usdex.test.TestCase):
    def _createTestStage(self):
        layer = self.tmpLayer(name="test")
        stage = Usd.Stage.Open(layer)
        self.defaultPrimName = "World"
        UsdGeom.Xform.Define(stage, "/World").GetPrim()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        self.assertIsValidUsd(stage)
        return stage

    def _checkDomeLightAttrs(self, light, intensity, texturePath=None, textureType=None):
        api = UsdLux.LightAPI(light)

        # check intensity
        intensityAttr = api.GetIntensityAttr()
        self.assertTrue(intensityAttr.IsAuthored())
        self.assertAlmostEqual(intensityAttr.Get(), intensity, 5)

        # if texture path was specified it and texture format should be authored
        if texturePath is not None:

            if textureType is None:
                textureType = UsdLux.Tokens.automatic

            texFileAttr = usdex.core.getLightAttr(light.GetTextureFileAttr())
            self.assertTrue(texFileAttr.IsAuthored())
            self.assertEqual(texFileAttr.Get().path, texturePath)

            texFormatAttr = usdex.core.getLightAttr(light.GetTextureFormatAttr())
            self.assertTrue(texFormatAttr.IsAuthored())
            self.assertEqual(texFormatAttr.Get(), textureType)

    def _checkRectLightAttrs(self, light, width, height, intensity, texturePath=None):
        # check width, height & intensity
        widthAttr = light.GetWidthAttr()
        self.assertTrue(widthAttr.IsAuthored())
        self.assertAlmostEqual(widthAttr.Get(), width, 5)

        heightAttr = light.GetHeightAttr()
        self.assertTrue(heightAttr.IsAuthored())
        self.assertAlmostEqual(heightAttr.Get(), height, 5)

        intensityAttr = light.GetIntensityAttr()
        self.assertTrue(intensityAttr.IsAuthored())
        self.assertAlmostEqual(intensityAttr.Get(), intensity, 5)

        # check texture path if supplied
        if texturePath is not None:
            texPathAttr = usdex.core.getLightAttr(light.GetTextureFileAttr())
            self.assertAlmostEqual(texPathAttr.Get().path, texturePath)

    def testDefineDomeLight(self):
        stage = self._createTestStage()
        textureFile = self.tmpFile(name="dome", ext="png")
        relTextureFile = f"./{pathlib.Path(textureFile).name}"

        dome_light_no_texture = usdex.core.defineDomeLight(stage, Sdf.Path("/World/domeLightNoTexture"), 0.77)
        dome_light_auto = usdex.core.defineDomeLight(stage, Sdf.Path("/World/domeLightAuto"), 0.88, relTextureFile)
        dome_light_lat_long = usdex.core.defineDomeLight(stage, Sdf.Path("/World/domeLightLatLong"), 0.99, relTextureFile, UsdLux.Tokens.latlong)

        self._checkDomeLightAttrs(dome_light_no_texture, 0.77)
        self._checkDomeLightAttrs(dome_light_auto, 0.88, relTextureFile)
        self._checkDomeLightAttrs(dome_light_lat_long, 0.99, relTextureFile, UsdLux.Tokens.latlong)

        with usdex.test.ScopedDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*is not a valid texture format token")]):
            dome_light_invalid_format = usdex.core.defineDomeLight(stage, Sdf.Path("/World/invalid"), 0.11, relTextureFile, UsdLux.Tokens.geometry)
            self.assertFalse(dome_light_invalid_format)

        self.assertIsValidUsd(stage)

    def testDefineRectLight(self):
        stage = self._createTestStage()
        textureFile = self.tmpFile(name="rect", ext="png")
        relTextureFile = f"./{pathlib.Path(textureFile).name}"

        rect_light_no_texture = usdex.core.defineRectLight(stage, Sdf.Path("/World/rectLightNoTexture"), 19, 93, 0.77)
        rect_light_textured = usdex.core.defineRectLight(stage, Sdf.Path("/World/rectLight"), 19.93, 39.91, 0.88, relTextureFile)
        self._checkRectLightAttrs(rect_light_no_texture, 19, 93, 0.77)
        self._checkRectLightAttrs(rect_light_textured, 19.93, 39.91, 0.88, relTextureFile)
        self.assertIsValidUsd(stage)

    def testIsLight(self):
        stage = self._createTestStage()
        cylinderLight = UsdLux.CylinderLight.Define(stage, "/World/cylinderLight")
        diskLight = UsdLux.DiskLight.Define(stage, "/World/diskLight")
        distantLight = UsdLux.DistantLight.Define(stage, "/World/distantLight")
        domeLight = UsdLux.DomeLight.Define(stage, "/World/domeLight")
        sphereLight = UsdLux.SphereLight.Define(stage, "/World/sphereLight")
        rectLight = UsdLux.RectLight.Define(stage, "/World/rectLight")
        xform = UsdGeom.Xform.Define(stage, "/World")
        cube = UsdGeom.Cube.Define(stage, "/World/cube")
        camera = UsdGeom.Camera.Define(stage, "/World/camera")
        material = UsdShade.Material.Define(stage, "/World/material")
        shader = UsdShade.Shader.Define(stage, "/World/shader")

        # ensure that isLight returns true for lights and false for all else
        self.assertTrue(usdex.core.isLight(cylinderLight.GetPrim()))
        self.assertTrue(usdex.core.isLight(diskLight.GetPrim()))
        self.assertTrue(usdex.core.isLight(distantLight.GetPrim()))
        self.assertTrue(usdex.core.isLight(domeLight.GetPrim()))
        self.assertTrue(usdex.core.isLight(sphereLight.GetPrim()))
        self.assertTrue(usdex.core.isLight(rectLight.GetPrim()))
        # geom
        self.assertFalse(usdex.core.isLight(cube.GetPrim()))
        # camera
        self.assertFalse(usdex.core.isLight(camera.GetPrim()))
        # xform
        self.assertFalse(usdex.core.isLight(xform.GetPrim()))
        # shader
        self.assertFalse(usdex.core.isLight(shader.GetPrim()))
        # shadeMaterial
        self.assertFalse(usdex.core.isLight(material.GetPrim()))
        # geom with LightAPI applied
        UsdLux.LightAPI.Apply(cube.GetPrim())
        self.assertTrue(usdex.core.isLight(cube.GetPrim()))

    def testGetLightAttr(self):
        # This test will only work in USD versions after the UsdLuxLights schema added "inputs:" to attribute names
        stage = self._createTestStage()
        distantLight = UsdLux.DistantLight.Define(stage, "/World/distantLight")

        # nothing authored
        self.assertEqual(usdex.core.getLightAttr(distantLight.GetAngleAttr()).Get(), distantLight.GetAngleAttr().Get())

        # old attribute name authored (no inputs:)
        distantLight.GetPrim().CreateAttribute("angle", Sdf.ValueTypeNames.Float, custom=False).Set(0.1)
        self.assertAlmostEqual(usdex.core.getLightAttr(distantLight.GetAngleAttr()).Get(), 0.1)

        # both old and new names authored
        distantLight.CreateAngleAttr().Set(0.5)
        self.assertEqual(usdex.core.getLightAttr(distantLight.GetAngleAttr()).Get(), distantLight.GetAngleAttr().Get())

        # just new name authored
        distantLight.GetPrim().RemoveProperty("angle")
        self.assertEqual(len(distantLight.GetPrim().GetAuthoredAttributes()), 1)
        self.assertEqual(usdex.core.getLightAttr(distantLight.GetAngleAttr()).Get(), distantLight.GetAngleAttr().Get())


class DefineDomeLightTestCase(usdex.test.DefineFunctionTestCase):

    # Configure the DefineFunctionTestCase
    defineFunc = usdex.core.defineDomeLight
    requiredArgs = tuple([1.0])
    typeName = "DomeLight"
    schema = UsdLux.DomeLight
    requiredPropertyNames = set(
        [
            "inputs:intensity",
        ]
    )


class DefineRectLightTestCase(usdex.test.DefineFunctionTestCase):

    # Configure the DefineFunctionTestCase
    defineFunc = usdex.core.defineRectLight
    requiredArgs = tuple([1.0, 2.0, 3.0])
    typeName = "RectLight"
    schema = UsdLux.RectLight
    requiredPropertyNames = set(
        [
            "inputs:height",
            "inputs:intensity",
            "inputs:width",
            UsdGeom.Tokens.extent,
        ]
    )
