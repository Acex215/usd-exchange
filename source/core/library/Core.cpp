// SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/Core.h"

#include "usdex/core/Feature.h"
#include "usdex/core/Version.h"

const char* usdex::core::version()
{
    return USDEX_BUILD_STRING;
}

bool usdex::core::withPython()
{
#if USDEX_WITH_PYTHON
    return true;
#else
    return false;
#endif
}
