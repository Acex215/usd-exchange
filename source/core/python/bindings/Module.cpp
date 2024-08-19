// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "CameraAlgoBindings.h"
#include "CoreBindings.h"
#include "CurvesAlgoBindings.h"
#include "DiagnosticsBindings.h"
#include "LayerAlgoBindings.h"
#include "LightAlgoBindings.h"
#include "MaterialAlgoBindings.h"
#include "MeshAlgoBindings.h"
#include "NameAlgoBindings.h"
#include "PointsAlgoBindings.h"
#include "PrimvarDataBindings.h"
#include "SettingsBindings.h"
#include "StageAlgoBindings.h"
#include "XformAlgoBindings.h"

using namespace usdex::core::bindings;
using namespace pybind11;

namespace
{

PYBIND11_MODULE(_usdex_core, m)
{
    bindCore(m);
    bindSettings(m);
    bindDiagnostics(m);
    bindLayerAlgo(m);
    bindStageAlgo(m);
    bindNameAlgo(m);
    bindXformAlgo(m);
    bindPrimvarData(m);
    bindPointsAlgo(m);
    bindMeshAlgo(m);
    bindCurvesAlgo(m);
    bindCameraAlgo(m);
    bindLightAlgo(m);
    bindMaterialAlgo(m);
}

} // namespace
