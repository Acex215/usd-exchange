// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/Settings.h"

using namespace pxr;

namespace usdex::core
{

TF_DEFINE_ENV_SETTING(
    USDEX_ENABLE_OMNI_TRANSCODING,
    true,
    "Use the omni::transcoding bootstring implementation when validating Prim and Property names"
);

} // namespace usdex::core
