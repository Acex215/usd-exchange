# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import List, Tuple

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

    def testColorSpaceToken(self):
        self.assertEqual(usdex.core.getColorSpaceToken(usdex.core.ColorSpace.eAuto), "auto")
        self.assertEqual(usdex.core.getColorSpaceToken(usdex.core.ColorSpace.eRaw), "raw")
        self.assertEqual(usdex.core.getColorSpaceToken(usdex.core.ColorSpace.eSrgb), "sRGB")

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


class DefinePreviewMaterialTest(usdex.test.DefineFunctionTestCase):

    # Configure the DefineFunctionTestCase
    defineFunc = usdex.core.definePreviewMaterial
    requiredArgs = tuple([Gf.Vec3f(1.0, 1.0, 1.0)])
    typeName = "Material"
    schema = UsdShade.Material
    requiredPropertyNames = set()

    def assertIsSurfaceShader(self, material: UsdShade.Material, shader: UsdShade.Shader):
        surfaceOutput = material.GetSurfaceOutput()
        self.assertTrue(surfaceOutput.HasConnectedSource())
        surface = surfaceOutput.GetConnectedSource()[0]
        self.assertEqual(surface.GetOutput(UsdShade.Tokens.surface).GetAttr(), shader.GetOutput(UsdShade.Tokens.surface).GetAttr())

    def assertInvalidPreviewMaterialForTextureFunctions(self, parent: Usd.Prim, texture: Sdf.AssetPath):
        # an invalid material will error gracefully
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*first be defined using definePreviewMaterial")]):
            result = usdex.core.addDiffuseTextureToPreviewMaterial(UsdShade.Material(), texture)
        self.assertFalse(result)

        # an invalid surface shader will error gracefully
        badMaterial = UsdShade.Material.Define(parent.GetStage(), parent.GetPath().AppendChild("BadMaterial"))
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*first be defined using definePreviewMaterial")]):
            result = usdex.core.addDiffuseTextureToPreviewMaterial(badMaterial, texture)
        self.assertFalse(result)

        # a surface shader without an ID will error gracefully
        otherShader = UsdShade.Shader.Define(parent.GetStage(), badMaterial.GetPath().AppendChild("NoShaderId"))
        badMaterial.CreateSurfaceOutput().ConnectToSource(otherShader.CreateOutput(UsdShade.Tokens.surface, Sdf.ValueTypeNames.Token))
        self.assertIsSurfaceShader(badMaterial, otherShader)
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*first be defined using definePreviewMaterial")]):
            result = usdex.core.addDiffuseTextureToPreviewMaterial(badMaterial, texture)
        self.assertFalse(result)

        # an surface shader that is not a UPS will error gracefully
        otherShader.SetShaderId("UsdUvTexture")
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_WARNING_TYPE, ".*first be defined using definePreviewMaterial")]):
            result = usdex.core.addDiffuseTextureToPreviewMaterial(badMaterial, texture)
        self.assertFalse(result)

    def assertValidPreviewMaterialTextureNetwork(
        self,
        material: UsdShade.Material,
        texture: Sdf.AssetPath,
        textureReaderName: str,
        colorSpace: usdex.core.ColorSpace,
        fallbackColor: Gf.Vec3f,
        connectionInfo: List[Tuple[str, Sdf.ValueTypeName, str]],
    ):
        uvReader = UsdShade.Shader(material.GetPrim().GetChild("TexCoordReader"))
        self.assertTrue(uvReader)
        self.assertEqual(uvReader.GetShaderId(), "UsdPrimvarReader_float2")
        self.assertEqual(uvReader.GetInput("varname").GetAttr().Get(), UsdUtils.GetPrimaryUVSetName())

        textureReader = UsdShade.Shader(material.GetPrim().GetChild(textureReaderName))
        self.assertTrue(textureReader)
        self.assertEqual(textureReader.GetShaderId(), "UsdUVTexture")
        self.assertEqual(textureReader.GetInput("file").GetAttr().Get().path, texture)
        self.assertEqual(textureReader.GetInput("sourceColorSpace").GetAttr().Get(), usdex.core.getColorSpaceToken(colorSpace))
        # fallback is a float4 with a solid alpha channel
        self.assertEqual(textureReader.GetInput("fallback").GetAttr().Get(), Gf.Vec4f(fallbackColor[0], fallbackColor[1], fallbackColor[2], 1.0))
        # tex coord input is driven by the tex coord reader
        self.assertTrue(textureReader.GetInput("st").HasConnectedSource())
        self.assertEqual(textureReader.GetInput("st").GetConnectedSource()[0].GetOutputs()[0].GetAttr(), uvReader.GetOutput("result").GetAttr())

        surface = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertTrue(surface)
        self.assertEqual(surface.GetPrim().GetName(), "PreviewSurface")
        self.assertEqual(surface.GetShaderId(), "UsdPreviewSurface")

        # verify the connectionInfo
        for inputName, inputTypeName, outputName in connectionInfo:
            self.assertTrue(surface.GetInput(inputName).HasConnectedSource())
            self.assertEqual(surface.GetInput(inputName).GetTypeName(), inputTypeName)
            source, sourceAttr, sourceType = surface.GetInput(inputName).GetConnectedSource()
            self.assertEqual(sourceType, UsdShade.AttributeType.Output)
            self.assertEqual(
                source.GetOutput(sourceAttr).GetAttr(),
                textureReader.GetOutput(outputName).GetAttr(),
                msg=f"Incorrect connection for {inputName} ({inputTypeName}) -> {outputName}",
            )

    def testPreviewMaterialShaders(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()

        # the material is created successfully
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.0, 0.5, 1.0), opacity=0.2, roughness=0.3, metallic=0.4)
        self.assertTrue(material)

        # the shader is now in place
        shader = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertTrue(shader)
        self.assertEqual(shader.GetPrim().GetName(), "PreviewSurface")
        self.assertEqual(shader.GetShaderId(), "UsdPreviewSurface")

        # the shader should include a Color named "diffuseColor" that has the effective specified value
        shaderInput = shader.GetInput("diffuseColor")
        self.assertTrue(shaderInput)
        self.assertEqual(shaderInput.GetTypeName(), Sdf.ValueTypeNames.Color3f)
        self.assertVecAlmostEqual(shaderInput.GetValueProducingAttributes()[0].Get(), Gf.Vec3f(0.0, 0.5, 1.0))

        # the shader should include a Float named "opacity" that has the effective specified value
        shaderInput = shader.GetInput("opacity")
        self.assertTrue(shaderInput)
        self.assertEqual(shaderInput.GetTypeName(), Sdf.ValueTypeNames.Float)
        self.assertAlmostEqual(shaderInput.GetValueProducingAttributes()[0].Get(), 0.2)

        # the shader should include a Float named "roughness" that has the effective specified value
        shaderInput = shader.GetInput("roughness")
        self.assertTrue(shaderInput)
        self.assertEqual(shaderInput.GetTypeName(), Sdf.ValueTypeNames.Float)
        self.assertAlmostEqual(shaderInput.GetValueProducingAttributes()[0].Get(), 0.3)

        # the shader should include a Float named "metallic" that has the effective specified value
        shaderInput = shader.GetInput("metallic")
        self.assertTrue(shaderInput)
        self.assertEqual(shaderInput.GetTypeName(), Sdf.ValueTypeNames.Float)
        self.assertAlmostEqual(shaderInput.GetValueProducingAttributes()[0].Get(), 0.4)

        # the shader is driving the surface of the material for the universal render context
        self.assertIsSurfaceShader(material, shader)

        # the shader is driving the surface of the material for the universal render context
        displacementOutput = material.GetDisplacementOutput()
        self.assertTrue(displacementOutput.HasConnectedSource())
        displacement = displacementOutput.GetConnectedSource()[0]
        self.assertEqual(displacement.GetOutput(UsdShade.Tokens.displacement).GetAttr(), shader.GetOutput(UsdShade.Tokens.displacement).GetAttr())

        # the volume output was not setup as this is not a volumetric material
        volumeOutput = material.GetVolumeOutput()
        self.assertFalse(volumeOutput.HasConnectedSource())
        self.assertFalse(shader.GetOutput(UsdShade.Tokens.volume))

        # all authored data is valid
        self.assertIsValidUsd(stage)

    def testInvalidInputs(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()

        # An out-of-range opacity will prevent authoring a material
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*Opacity value -0.000001 is outside range")]):
            material = usdex.core.definePreviewMaterial(materials, "BadOpacity", Gf.Vec3f(1, 0, 0), opacity=-0.000001)
        self.assertFalse(material)
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*Opacity value 1.000001 is outside range")]):
            material = usdex.core.definePreviewMaterial(materials, "BadOpacity", Gf.Vec3f(1, 0, 0), opacity=1.000001)
        self.assertFalse(material)

        # An out-of-range roughness will prevent authoring a material
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*Roughness value -0.000001 is outside range")]):
            material = usdex.core.definePreviewMaterial(materials, "BadRoughness", Gf.Vec3f(1, 0, 0), roughness=-0.000001)
        self.assertFalse(material)
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*Roughness value 1.000001 is outside range")]):
            material = usdex.core.definePreviewMaterial(materials, "BadRoughness", Gf.Vec3f(1, 0, 0), roughness=1.000001)
        self.assertFalse(material)

        # An out-of-range metallic will prevent authoring a material
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*Metallic value -0.000001 is outside range")]):
            material = usdex.core.definePreviewMaterial(materials, "BadMetallic", Gf.Vec3f(1, 0, 0), metallic=-0.000001)
        self.assertFalse(material)
        with usdex.test.ScopedTfDiagnosticChecker(self, [(Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*Metallic value 1.000001 is outside range")]):
            material = usdex.core.definePreviewMaterial(materials, "BadMetallic", Gf.Vec3f(1, 0, 0), metallic=1.000001)
        self.assertFalse(material)

        material = usdex.core.definePreviewMaterial(materials, "LowestValidInputs", Gf.Vec3f(0, 0, 0), opacity=0, roughness=0, metallic=0)
        self.assertTrue(material)
        self.assertIsValidUsd(stage)

        material = usdex.core.definePreviewMaterial(materials, "HighestValidInputs", Gf.Vec3f(1, 1, 1), opacity=1, roughness=1, metallic=1)
        self.assertTrue(material)
        self.assertIsValidUsd(stage)

    def testAddDiffuseTexture(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        texture = Sdf.AssetPath(self.tmpFile(name="BaseColor", ext="png"))

        self.assertInvalidPreviewMaterialForTextureFunctions(parent=materials, texture=texture)

        # a valid preview material will successfully add a diffuse texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.0, 0.5, 1.0))
        result = usdex.core.addDiffuseTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="DiffuseTexture",
            colorSpace=usdex.core.ColorSpace.eAuto,
            fallbackColor=Gf.Vec3f(0.0, 0.5, 1.0),
            connectionInfo=[("diffuseColor", Sdf.ValueTypeNames.Color3f, "rgb")],
        )

    def testAddNormalTexture(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        texture = Sdf.AssetPath(self.tmpFile(name="N", ext="png"))

        self.assertInvalidPreviewMaterialForTextureFunctions(parent=materials, texture=texture)

        # a valid preview material will successfully add a normals texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.8, 0.8, 0.8))
        result = usdex.core.addNormalTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="NormalTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(0.0, 0.0, 1.0),
            connectionInfo=[("normal", Sdf.ValueTypeNames.Normal3f, "rgb")],
        )
        textureReader = UsdShade.Shader(material.GetPrim().GetChild("NormalTexture"))
        self.assertEqual(textureReader.GetInput("scale").GetAttr().Get(), Gf.Vec4f(2, 2, 2, 1))
        self.assertEqual(textureReader.GetInput("bias").GetAttr().Get(), Gf.Vec4f(-1, -1, -1, 0))

    def testAddOrmTexture(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        texture = Sdf.AssetPath(self.tmpFile(name="ORM", ext="png"))

        self.assertInvalidPreviewMaterialForTextureFunctions(parent=materials, texture=texture)

        # a valid preview material will successfully add a ORM texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.8, 0.8, 0.8))
        result = usdex.core.addOrmTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="ORMTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(1.0, 0.5, 0.0),
            connectionInfo=[
                ("occlusion", Sdf.ValueTypeNames.Float, "r"),
                ("roughness", Sdf.ValueTypeNames.Float, "g"),
                ("metallic", Sdf.ValueTypeNames.Float, "b"),
            ],
        )

        # the originally defined roughness and metallic values are used in the fallback (opacity is not relevant)
        material = usdex.core.definePreviewMaterial(materials, "InitialValues", Gf.Vec3f(0.8, 0.8, 0.8), opacity=0.8, roughness=0.25, metallic=0.9)
        result = usdex.core.addOrmTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="ORMTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(1.0, 0.25, 0.9),
            connectionInfo=[
                ("occlusion", Sdf.ValueTypeNames.Float, "r"),
                ("roughness", Sdf.ValueTypeNames.Float, "g"),
                ("metallic", Sdf.ValueTypeNames.Float, "b"),
            ],
        )

    def testAddRoughnessTexture(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        texture = Sdf.AssetPath(self.tmpFile(name="roughness", ext="png"))

        self.assertInvalidPreviewMaterialForTextureFunctions(parent=materials, texture=texture)

        # a valid preview material will successfully add a ORM texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.8, 0.8, 0.8))
        result = usdex.core.addRoughnessTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="RoughnessTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(0.5, 0.0, 0.0),
            connectionInfo=[("roughness", Sdf.ValueTypeNames.Float, "r")],
        )

        # the originally defined roughness value is used in the fallback
        material = usdex.core.definePreviewMaterial(materials, "InitialValues", Gf.Vec3f(0.8, 0.8, 0.8), roughness=0.1)
        result = usdex.core.addRoughnessTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="RoughnessTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(0.1, 0.0, 0.0),
            connectionInfo=[("roughness", Sdf.ValueTypeNames.Float, "r")],
        )

    def testAddMetallicTexture(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        texture = Sdf.AssetPath(self.tmpFile(name="metallic", ext="png"))

        self.assertInvalidPreviewMaterialForTextureFunctions(parent=materials, texture=texture)

        # a valid preview material will successfully add a ORM texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.8, 0.8, 0.8))
        result = usdex.core.addMetallicTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="MetallicTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(0.0, 0.0, 0.0),
            connectionInfo=[("metallic", Sdf.ValueTypeNames.Float, "r")],
        )

        # the originally defined metallic value is used in the fallback
        material = usdex.core.definePreviewMaterial(materials, "InitialValues", Gf.Vec3f(0.8, 0.8, 0.8), metallic=0.1)
        result = usdex.core.addMetallicTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="MetallicTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(0.1, 0.0, 0.0),
            connectionInfo=[("metallic", Sdf.ValueTypeNames.Float, "r")],
        )

    def testAddOpacityTexture(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        texture = Sdf.AssetPath(self.tmpFile(name="opacity", ext="png"))

        self.assertInvalidPreviewMaterialForTextureFunctions(parent=materials, texture=texture)

        # a valid preview material will successfully add a ORM texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.8, 0.8, 0.8))
        result = usdex.core.addOpacityTextureToPreviewMaterial(material, texture)
        self.assertTrue(result)
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            texture,
            textureReaderName="OpacityTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(1.0, 0.0, 0.0),
            connectionInfo=[("opacity", Sdf.ValueTypeNames.Float, "r")],
        )
        surface = usdex.core.computeEffectivePreviewSurfaceShader(material)
        self.assertEqual(surface.GetInput("ior").GetAttr().Get(), 1.0)
        # rather than try to assert the exact epsilon between c++ and python we
        # assert that the threshold is a very small non-zero number
        self.assertGreater(surface.GetInput("opacityThreshold").GetAttr().Get(), 0)
        self.assertLess(surface.GetInput("opacityThreshold").GetAttr().Get(), 1e-6)

    def testTexturesShareTexCoordReader(self):
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        materials = UsdGeom.Scope.Define(stage, stage.GetDefaultPrim().GetPath().AppendChild(UsdUtils.GetMaterialsScopeName())).GetPrim()
        diffuseTexture = Sdf.AssetPath(self.tmpFile(name="BaseColor", ext="png"))
        normalTexture = Sdf.AssetPath(self.tmpFile(name="N", ext="png"))

        # a valid preview material will successfully add a diffuse texture
        material = usdex.core.definePreviewMaterial(materials, "Test", Gf.Vec3f(0.0, 0.5, 1.0))
        result = usdex.core.addDiffuseTextureToPreviewMaterial(material, diffuseTexture)
        self.assertTrue(result)
        result = usdex.core.addNormalTextureToPreviewMaterial(material, normalTexture)
        self.assertTrue(result)

        # both inputs are driven by the expected textures
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            diffuseTexture,
            textureReaderName="DiffuseTexture",
            colorSpace=usdex.core.ColorSpace.eAuto,
            fallbackColor=Gf.Vec3f(0.0, 0.5, 1.0),
            connectionInfo=[("diffuseColor", Sdf.ValueTypeNames.Color3f, "rgb")],
        )
        self.assertValidPreviewMaterialTextureNetwork(
            material,
            normalTexture,
            textureReaderName="NormalTexture",
            colorSpace=usdex.core.ColorSpace.eRaw,
            fallbackColor=Gf.Vec3f(0.0, 0.0, 1.0),
            connectionInfo=[("normal", Sdf.ValueTypeNames.Normal3f, "rgb")],
        )

        # the primvar reader for tex coords is shared
        def findTextureReaders(stage):
            textureReaders = []
            for prim in stage.Traverse():
                shader = UsdShade.Shader(prim)
                if shader and shader.GetShaderId() == "UsdPrimvarReader_float2":
                    textureReaders.append(shader)
            return textureReaders

        textureReaders = findTextureReaders(stage)
        self.assertEqual(len(textureReaders), 1)
        # assertValidPreviewMaterialTextureNetwork will have already ensured both textures are driven by TexCoordReader
        self.assertEqual(textureReaders[0].GetPrim(), material.GetPrim().GetChild("TexCoordReader"))
