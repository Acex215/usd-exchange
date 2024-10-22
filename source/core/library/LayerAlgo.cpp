// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/LayerAlgo.h"

#include <pxr/usd/usd/stage.h>

using namespace pxr;

namespace
{

static constexpr const char* g_authoringKey = "creator";

} // namespace

bool usdex::core::hasLayerAuthoringMetadata(pxr::SdfLayerHandle layer)
{
    VtDictionary data = layer->GetCustomLayerData();
    return data.find(g_authoringKey) != data.end();
}

void usdex::core::setLayerAuthoringMetadata(pxr::SdfLayerHandle layer, const std::string& value)
{
    VtDictionary data = layer->GetCustomLayerData();
    data[g_authoringKey] = value;
    layer->SetCustomLayerData(data);
}

bool usdex::core::saveLayer(pxr::SdfLayerHandle layer, std::optional<std::string_view> authoringMetadata, std::optional<std::string_view> comment)
{
    if (authoringMetadata.has_value())
    {
        setLayerAuthoringMetadata(layer, authoringMetadata.value().data());
    }

    bool success;
    if (comment.has_value())
    {
        TF_STATUS("Saving \"%s\" with comment \"%s\"", layer->GetIdentifier().c_str(), comment.value().data());
        layer->SetComment(comment.value().data());
        success = layer->Save();
    }
    else
    {
        TF_STATUS("Saving \"%s\"", layer->GetIdentifier().c_str());
        success = layer->Save();
    }

    return success;
}

bool usdex::core::exportLayer(
    SdfLayerHandle layer,
    const std::string& identifier,
    const std::string& authoringMetadata,
    std::optional<std::string_view> comment,
    const SdfLayer::FileFormatArguments& fileFormatArgs
)
{
    // Early out on an unsupported identifier
    if (identifier.empty() || !UsdStage::IsSupportedFile(identifier))
    {
        TF_WARN("Unable to export SdfLayer to \"%s\" due to an invalid identifier", identifier.c_str());
        return false;
    }

    // Ensure that layer authoring metadata exists.
    if (!hasLayerAuthoringMetadata(layer))
    {
        setLayerAuthoringMetadata(layer, authoringMetadata);
    }

    bool success;
    if (comment.has_value())
    {
        TF_STATUS("Exporting \"%s\" with comment \"%s\"", identifier.c_str(), comment.value().data());

        // Capture the existing comment in the layer so that it can be restored after export.
        // We do not want to modify the source layer, but equally we do not want to have to open the exported layer to make changes.
        const std::string& existingComment = layer->GetComment();
        layer->SetComment(comment.value().data());
        success = layer->Export(identifier, "", fileFormatArgs);
        // Restore the comment
        layer->SetComment(existingComment);
    }
    else
    {
        TF_STATUS("Exporting \"%s\"", identifier.c_str());
        success = layer->Export(identifier, "", fileFormatArgs);
    }

    return success;
}
