// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//

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
