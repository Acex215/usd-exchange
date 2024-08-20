// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "usdex/core/CameraAlgo.h"

#include "usdex/pybind/UsdBindings.h"

#include <pybind11/pybind11.h>

using namespace usdex::core;
using namespace pybind11;
using namespace pxr;

namespace usdex::core::bindings
{

void bindCameraAlgo(module& m)
{
    m.def(
        "defineCamera",
        overload_cast<UsdStagePtr, const SdfPath&, const GfCamera&>(&defineCamera),
        arg("stage"),
        arg("path"),
        arg("cameraData"),
        R"(
            Defines a basic 3d camera on the stage.

            Note that ``Gf.Camera`` is a simplified form of 3d camera data that does not account for time-sampled data, shutter window,
            stereo role, or exposure. If you need to author those properties, do so after defining the ``UsdGeom.Camera``.

            An invalid UsdGeomCamera will be returned if camera attributes could not be authored successfully.

            Parameters:
                - **stage** - The stage on which to define the camera
                - **path** - The absolute prim path at which to define the camera
                - **cameraData** - The camera data to set, including the world space transform matrix

            Returns:
                A ``UsdGeom.Camera`` schema wrapping the defined ``Usd.Prim``.

        )"
    );

    m.def(
        "defineCamera",
        overload_cast<UsdPrim, const std::string&, const GfCamera&>(&defineCamera),
        arg("parent"),
        arg("name"),
        arg("cameraData"),
        R"(
            Defines a basic 3d camera on the stage.

            This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.

            Parameters:
                - **parent** - Prim below which to define the camera
                - **name** - Name of the camera
                - **cameraData** - The camera data to set, including the world space transform matrix

            Returns:
                A ``UsdGeom.Camera`` schema wrapping the defined ``Usd.Prim``.

        )"
    );
}

} // namespace usdex::core::bindings
