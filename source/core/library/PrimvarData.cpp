// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/PrimvarData.h"

namespace usdex::core
{

// explicitly instantiate each of the types we defined in the public header.
template class PrimvarData<float>;
template class PrimvarData<int64_t>;
template class PrimvarData<int>;
template class PrimvarData<std::string>;
template class PrimvarData<pxr::TfToken>;
template class PrimvarData<pxr::GfVec2f>;
template class PrimvarData<pxr::GfVec3f>;

} // namespace usdex::core
