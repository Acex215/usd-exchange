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
from pxr import Gf, Sdf, Tf, Usd, UsdGeom, Vt


class DefineCameraTestCase(usdex.test.DefineFunctionTestCase):

    # Configure the DefineFunctionTestCase
    defineFunc = usdex.core.defineCamera
    requiredArgs = tuple([Gf.Camera()])
    schema = UsdGeom.Camera
    typeName = "Camera"
    requiredPropertyNames = set(
        [
            UsdGeom.Tokens.projection,
            UsdGeom.Tokens.horizontalAperture,
            UsdGeom.Tokens.verticalAperture,
            UsdGeom.Tokens.horizontalApertureOffset,
            UsdGeom.Tokens.verticalApertureOffset,
            UsdGeom.Tokens.focalLength,
            UsdGeom.Tokens.clippingRange,
            UsdGeom.Tokens.clippingPlanes,
            UsdGeom.Tokens.fStop,
            UsdGeom.Tokens.focusDistance,
            # FUTURE: account for shutter, stereo, exposure
        ]
    )

    def assertCamerasEqual(self, camera: UsdGeom.Camera, cameraData: Gf.Camera):
        self.assertEqual(camera.GetLocalTransformation(), cameraData.transform)
        self.assertEqual(usdex.core.getLocalTransformMatrix(camera.GetPrim()), cameraData.transform)

        projection = camera.GetProjectionAttr().Get()
        if projection == "perspective":
            self.assertEqual(cameraData.projection, Gf.Camera.Perspective)
        elif projection == "orthographic":
            self.assertEqual(cameraData.projection, Gf.Camera.Orthographic)
        else:
            self.assertFalse(True, f"Camera has an invalid projection attr '{projection}'")

        self.assertEqual(camera.GetHorizontalApertureAttr().Get(), cameraData.horizontalAperture)
        self.assertEqual(camera.GetVerticalApertureAttr().Get(), cameraData.verticalAperture)
        self.assertEqual(camera.GetHorizontalApertureOffsetAttr().Get(), cameraData.horizontalApertureOffset)
        self.assertEqual(camera.GetVerticalApertureOffsetAttr().Get(), cameraData.verticalApertureOffset)
        self.assertEqual(camera.GetFocalLengthAttr().Get(), cameraData.focalLength)
        self.assertEqual(camera.GetClippingRangeAttr().Get(), Gf.Vec2f(cameraData.clippingRange.min, cameraData.clippingRange.max))

        self.assertEqual(camera.GetClippingPlanesAttr().Get(), Vt.Vec4fArray(cameraData.clippingPlanes))

        self.assertEqual(camera.GetFStopAttr().Get(), cameraData.fStop)
        self.assertEqual(camera.GetFocusDistanceAttr().Get(), cameraData.focusDistance)

    def testStrongerWeaker(self):
        # This differs from the implementation in DefineFunctionTestCase
        # A prim can be defined in a stronger sub layer but will fail to re-define in a weaker one.
        stage = self.createTestStage()

        path = Sdf.Path("/World/StrongerFirst")
        stage.SetEditTarget(Usd.EditTarget(self.strongerSubLayer))
        result = self.defineFunc(stage, path, *self.requiredArgs)
        self.assertDefineFunctionSuccess(result)
        self.assertIsValidUsd(result.GetPrim().GetStage())

        stage.SetEditTarget(Usd.EditTarget(self.weakerSubLayer))
        with usdex.test.ScopedDiagnosticChecker(
            self,
            [
                (Tf.TF_DIAGNOSTIC_RUNTIME_ERROR_TYPE, ".*opinions in the composed layer stack are stronger"),
                (Tf.TF_DIAGNOSTIC_WARNING_TYPE, "Could not clear xformOpOrder"),
            ],
        ):
            result = self.defineFunc(stage, path, *self.requiredArgs)
        self.assertDefineFunctionFailure(result)

    def testDefineDefaultCamera(self):
        stage = self.createTestStage()
        path = Sdf.Path("/World/Camera")
        cameraData = Gf.Camera()
        camera = usdex.core.defineCamera(stage, path, cameraData)
        self.assertDefineFunctionSuccess(camera)
        self.assertCamerasEqual(camera, cameraData)
        self.assertIsValidUsd(stage)

    def testDefineOrthoCamera(self):
        stage = self.createTestStage()
        path = Sdf.Path("/World/Camera")
        cameraData = Gf.Camera(projection=Gf.Camera.Orthographic)
        camera = usdex.core.defineCamera(stage, path, cameraData)
        self.assertDefineFunctionSuccess(camera)
        self.assertCamerasEqual(camera, cameraData)
        self.assertIsValidUsd(stage)

    def testDefineTransformedCamera(self):
        stage = self.createTestStage()
        path = Sdf.Path("/World/Camera")
        transform = Gf.Transform()
        transform.SetTranslation(Gf.Vec3d(10.0, 20.0, 30.0))
        transform.SetPivotPosition(Gf.Vec3d(10.0, 20.0, 30.0))
        transform.SetRotation(Gf.Rotation(Gf.Vec3d.XAxis(), 45.0))
        transform.SetScale(Gf.Vec3d(2.0, 2.0, 2.0))
        cameraData = Gf.Camera(transform=transform.GetMatrix())
        camera = usdex.core.defineCamera(stage, path, cameraData)
        self.assertDefineFunctionSuccess(camera)
        self.assertCamerasEqual(camera, cameraData)
        self.assertIsValidUsd(stage)
