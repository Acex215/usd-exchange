// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

#include "usdex/core/Settings.h"

#include "usdex/pybind/UsdBindings.h"

#include <pybind11/pybind11.h>

using namespace usdex::core;
using namespace pybind11;

namespace usdex::core::bindings
{

void bindSettings(module& m)
{
    m.attr("enableOmniTranscodingSetting") = USDEX_ENABLE_OMNI_TRANSCODING._name;
}

} // namespace usdex::core::bindings
