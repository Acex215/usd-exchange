# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import usdex.core
import usdex.test
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, UsdShade, UsdUtils


class MaterialAlgoTest(usdex.test.TestCase):

    def testCreateMaterial(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()

        material = usdex.core.createMaterial(parent=materials, name="foo")
        self.assertTrue(material.GetPrim())
        self.assertIsValidUsd(stage)

        # An invalid parent will result in an invalid Material schema being returned
        invalid_parent = stage.GetPrimAtPath("/Root/InvalidPath")
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid location")]):
            material = usdex.core.createMaterial(invalid_parent, "InvalidMaterial")
        self.assertFalse(material)

        # An invalid name will result in an invalid Material schema being returned
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid location")]):
            material = usdex.core.createMaterial(materials, "")
        self.assertFalse(material)

        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*invalid location")]):
            material = usdex.core.createMaterial(materials, "1_Material")
        self.assertFalse(material)

    def testBindMaterial(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        geometry = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild("Geometry")).GetPrim()  # common convention
        cube = UsdGeom.Cube.Define(stage, geometry.GetPath().AppendChild("Cube")).GetPrim()
        cube2 = UsdGeom.Cube.Define(stage, geometry.GetPath().AppendChild("Cube2")).GetPrim()

        material = usdex.core.createMaterial(materials, "Material")
        self.assertTrue(material)

        result = usdex.core.bindMaterial(cube, material)
        self.assertTrue(result)
        self.assertTrue(cube.HasAPI(UsdShade.MaterialBindingAPI))
        self.assertIsValidUsd(stage)

        # An invalid material will fail to bind
        invalidMaterial = UsdShade.Material(materials.GetChild("InvalidPath"))
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, "UsdShadeMaterial.*is not valid, cannot bind material")]):
            result = usdex.core.bindMaterial(cube2, invalidMaterial)
        self.assertFalse(result)
        self.assertFalse(cube2.HasAPI(UsdShade.MaterialBindingAPI))

        # An invalid target prim will fail to be bound
        invalidTarget = UsdGeom.Cube(geometry.GetChild("InvalidPath")).GetPrim()
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, "UsdPrim.*is not valid, cannot bind material")]):
            result = usdex.core.bindMaterial(invalidTarget, material)
        self.assertFalse(result)

        # If both are invalid it cannot bind either
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*are not valid, cannot bind material")]):
            result = usdex.core.bindMaterial(invalidTarget, invalidMaterial)
        self.assertFalse(result)

    def testComputeEffectiveSurfaceShader(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()

        # An un-initialized Material will result in an invalid shader schema being returned
        material = UsdShade.Material()
        shader = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertFalse(shader)

        # An invalid UsdShade.Material will result in an invalid shader schema being returned
        material = UsdShade.Material(stage.GetPrimAtPath("/Root"))
        self.assertFalse(material)
        shader = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertFalse(shader)

        # A Material with no connected shaders will result in an invalid shader schema being returned
        material = usdex.core.createMaterial(materials, "Material")
        self.assertTrue(material)
        shader = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertFalse(shader)

        # A connected surface shader will be returned
        previewShader = UsdShade.Shader.Define(stage, material.GetPrim().GetPath().AppendChild("PreviewSurface"))
        self.assertTrue(previewShader)
        output = previewShader.CreateOutput("out", Sdf.ValueTypeNames.Token)
        material.CreateSurfaceOutput().ConnectToSource(output)
        shader = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertTrue(shader)
        self.assertEqual(shader.GetPrim(), previewShader.GetPrim())

        # Even with another render context connected, the shader for the universal context is returned
        otherShader = UsdShade.Shader.Define(stage, material.GetPrim().GetPath().AppendChild("foo"))
        self.assertTrue(otherShader)
        output = otherShader.CreateOutput("out", Sdf.ValueTypeNames.Token)
        material.CreateSurfaceOutput("fancy").ConnectToSource(output)
        shader = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertTrue(shader)
        self.assertNotEqual(shader.GetPrim(), otherShader.GetPrim())
        self.assertEqual(shader.GetPrim(), previewShader.GetPrim())

    def testColorSpaceConversions(self):
        greySrgb = Gf.Vec3f(0.5, 0.5, 0.5)
        darkRedSrgb = Gf.Vec3f(0.33, 0.1, 0.1)
        lightGreenSrgb = Gf.Vec3f(0.67, 0.97, 0.67)
        purpleSrgb = Gf.Vec3f(0.45, 0.2, 0.6)
        blackSrgb = Gf.Vec3f(0.03, 0.03, 0.03)

        greyLinear = Gf.Vec3f(0.21404114, 0.21404114, 0.21404114)
        darkRedLinear = Gf.Vec3f(0.0889815256, 0.01002282, 0.01002282)
        lightGreenLinear = Gf.Vec3f(0.406448301, 0.93310684, 0.406448301)
        purpleLinear = Gf.Vec3f(0.17064493, 0.033104767, 0.3185467781)
        blackLinear = Gf.Vec3f(0.0023219814, 0.0023219814, 0.0023219814)

        convertedGreyLinear = usdex.core.sRgbToLinear(greySrgb)
        convertedDarkRedLinear = usdex.core.sRgbToLinear(darkRedSrgb)
        convertedLightGreenLinear = usdex.core.sRgbToLinear(lightGreenSrgb)
        convertedPurpleLinear = usdex.core.sRgbToLinear(purpleSrgb)
        convertedBlackLinear = usdex.core.sRgbToLinear(blackSrgb)

        convertedGreySrgb = usdex.core.linearToSrgb(greyLinear)
        convertedDarkRedSrgb = usdex.core.linearToSrgb(darkRedLinear)
        convertedLightGreenSrgb = usdex.core.linearToSrgb(lightGreenLinear)
        convertedPurpleSrgb = usdex.core.linearToSrgb(purpleLinear)
        convertedBlackSrgb = usdex.core.linearToSrgb(blackLinear)

        roundTripGreySrgb = usdex.core.linearToSrgb(convertedGreyLinear)
        roundTripRedSrgb = usdex.core.linearToSrgb(convertedDarkRedLinear)
        roundTripGreenSrgb = usdex.core.linearToSrgb(convertedLightGreenLinear)
        roundTripPurpleSrgb = usdex.core.linearToSrgb(convertedPurpleLinear)
        roundTripBlackSrgb = usdex.core.linearToSrgb(convertedBlackLinear)

        roundTripGreyLinear = usdex.core.sRgbToLinear(convertedGreySrgb)
        roundTripRedLinear = usdex.core.sRgbToLinear(convertedDarkRedSrgb)
        roundTripGreenLinear = usdex.core.sRgbToLinear(convertedLightGreenSrgb)
        roundTripPurpleLinear = usdex.core.sRgbToLinear(convertedPurpleSrgb)
        roundTripBlackLinear = usdex.core.sRgbToLinear(convertedBlackSrgb)

        self.assertVecAlmostEqual(convertedGreyLinear, greyLinear, places=6)
        self.assertVecAlmostEqual(convertedDarkRedLinear, darkRedLinear, places=6)
        self.assertVecAlmostEqual(convertedLightGreenLinear, lightGreenLinear, places=6)
        self.assertVecAlmostEqual(convertedPurpleLinear, purpleLinear, places=6)
        self.assertVecAlmostEqual(convertedBlackLinear, blackLinear, places=6)

        self.assertVecAlmostEqual(convertedGreySrgb, greySrgb, places=6)
        self.assertVecAlmostEqual(convertedDarkRedSrgb, darkRedSrgb, places=6)
        self.assertVecAlmostEqual(convertedLightGreenSrgb, lightGreenSrgb, places=6)
        self.assertVecAlmostEqual(convertedPurpleSrgb, purpleSrgb, places=6)
        self.assertVecAlmostEqual(convertedBlackSrgb, blackSrgb, places=6)

        self.assertVecAlmostEqual(roundTripGreyLinear, greyLinear, places=6)
        self.assertVecAlmostEqual(roundTripRedLinear, darkRedLinear, places=6)
        self.assertVecAlmostEqual(roundTripGreenLinear, lightGreenLinear, places=6)
        self.assertVecAlmostEqual(roundTripPurpleLinear, purpleLinear, places=6)
        self.assertVecAlmostEqual(roundTripBlackLinear, blackLinear, places=6)

        self.assertVecAlmostEqual(roundTripGreySrgb, greySrgb, places=6)
        self.assertVecAlmostEqual(roundTripRedSrgb, darkRedSrgb, places=6)
        self.assertVecAlmostEqual(roundTripGreenSrgb, lightGreenSrgb, places=6)
        self.assertVecAlmostEqual(roundTripPurpleSrgb, purpleSrgb, places=6)
        self.assertVecAlmostEqual(roundTripBlackSrgb, blackSrgb, places=6)
