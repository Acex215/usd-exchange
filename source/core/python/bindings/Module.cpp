// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//

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
