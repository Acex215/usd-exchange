// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "usdex/core/StageAlgo.h"

#include "usdex/core/LayerAlgo.h"

#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/tokens.h>
#include <pxr/usd/usdUtils/authoring.h>

using namespace pxr;

namespace
{

// clang-format off
TF_DEFINE_PRIVATE_TOKENS(
    _tokens,
    ((y, "y"))
    ((z, "z"))
);
// clang-format on

bool validateStageMetrics(const TfToken& upAxis, const double linearUnits, std::string* reason)
{
    // Validate the up axis
    if (upAxis != UsdGeomTokens->z && upAxis != UsdGeomTokens->y)
    {
        // Also accept lower case "y" and "z" tokens
        // This avoid confusion for Python clients where TfToken is simply a string and it is common to confuse the required case
        if (upAxis != _tokens->z && upAxis != _tokens->y)
        {
            *reason = TfStringPrintf("Unsupported up axis value \"%s\"", upAxis.GetString().c_str());
            return false;
        }
    }

    // Validate the linear units
    if (linearUnits <= 0.0)
    {
        *reason = TfStringPrintf("Linear units value must be greater than zero, received %f", linearUnits);
        return false;
    }

    return true;
}

// Business logic for defining the default prim and setting stage metrics without validation
// This avoids duplicate validation when configuring the stage within a function that has already validated the arguments
bool uncheckedConfigureStage(
    UsdStagePtr stage,
    const std::string& defaultPrimName,
    const TfToken& upAxis,
    const double linearUnits,
    const std::string& authoringMetadata
)
{
    // Set stage metrics via the stage
    // The metadata will be authored on the root layer
    if (!UsdGeomSetStageMetersPerUnit(stage, linearUnits))
    {
        return false;
    }

    // If a lower case "y" or "z" token was provided resolve it to the expected upper case token
    TfToken resolvedUpAxis = upAxis;
    if (resolvedUpAxis == _tokens->z)
    {
        resolvedUpAxis = UsdGeomTokens->z;
    }
    if (resolvedUpAxis == _tokens->y)
    {
        resolvedUpAxis = UsdGeomTokens->y;
    }
    if (!UsdGeomSetStageUpAxis(stage, resolvedUpAxis))
    {
        return false;
    }

    const TfToken defaultPrimToken = TfToken(defaultPrimName);
    const SdfPath defaultPrimPath = SdfPath::AbsoluteRootPath().AppendChild(defaultPrimToken);

    // Define a prim of type "Scope" at the default prim path if there is not already a prim specified
    // The specifier and type name are not set on existing prim specs so that it is possible to use configureStage in cases where a "class" or "over"
    // specifier is desired, or the type name is intentionally undefined.
    SdfLayerHandle layer = stage->GetRootLayer();
    if (!layer->GetPrimAtPath(defaultPrimPath))
    {
        SdfPrimSpecHandle primSpec = SdfCreatePrimInLayer(layer, defaultPrimPath);
        primSpec->SetSpecifier(SdfSpecifierDef);
        primSpec->SetTypeName("Scope");
    }

    // Set the default prim on the root layer
    layer->SetDefaultPrim(defaultPrimToken);

    // Set the authoring metadata only if it hasn't been set before. This is to preserve the original provenance information
    if (!usdex::core::hasLayerAuthoringMetadata(layer))
    {
        usdex::core::setLayerAuthoringMetadata(layer, authoringMetadata);
    }

    return true;
}

} // namespace

UsdStageRefPtr usdex::core::createStage(
    const std::string& identifier,
    const std::string& defaultPrimName,
    const TfToken& upAxis,
    const double linearUnits,
    const std::string& authoringMetadata,
    const SdfLayer::FileFormatArguments& fileFormatArgs
)
{
    // Early out on an unsupported identifier
    if (identifier.empty() || !UsdStage::IsSupportedFile(identifier))
    {
        TF_WARN("Unable to create UsdStage at \"%s\" due to an invalid identifier", identifier.c_str());
        return nullptr;
    }

    // Early out on an invalid default prim name
    if (!SdfPath::IsValidIdentifier(defaultPrimName))
    {
        TF_WARN(
            "Unable to create UsdStage at \"%s\" due to an invalid default prim name: \"%s\" is not a valid identifier",
            identifier.c_str(),
            defaultPrimName.c_str()
        );
        return nullptr;
    }

    // Early out on invalid stage metrics
    std::string reason;
    if (!validateStageMetrics(upAxis, linearUnits, &reason))
    {
        TF_WARN("Unable to create UsdStage at \"%s\" due to invalid stage metrics: %s", identifier.c_str(), reason.c_str());
        return nullptr;
    }

    // Create the stage in memory to avoid adding the identifier to the registry in cases where failures occur
    UsdStageRefPtr stage = UsdStage::CreateInMemory(identifier);

    // Configure the stage
    if (!uncheckedConfigureStage(stage, defaultPrimName, upAxis, linearUnits, authoringMetadata))
    {
        return nullptr;
    }

    // Export the stage to the desired identifier
    const std::string comment = "";
    if (!stage->GetRootLayer()->Export(identifier, comment, fileFormatArgs))
    {
        return nullptr;
    }

    // If the layer is already loaded reload it and return a stage wrapping the layer
    // Without the reload the state of the layer will not reflect what was just exported
    if (SdfLayerHandle layer = SdfLayer::Find(identifier))
    {
        if (!layer->Reload(true))
        {
            return nullptr;
        }
        return UsdStage::Open(layer);
    }

    // Return a stage wrapping the exported layer
    return UsdStage::Open(identifier);
}

bool usdex::core::configureStage(
    UsdStagePtr stage,
    const std::string& defaultPrimName,
    const TfToken& upAxis,
    const double linearUnits,
    const std::string& authoringMetadata
)
{
    // Validate the default prim name
    if (!SdfPath::IsValidIdentifier(defaultPrimName))
    {
        TF_WARN(
            "Unable to configure UsdStage at \"%s\" due to an invalid default prim name: \"%s\" is not a valid identifier",
            stage->GetRootLayer()->GetIdentifier().c_str(),
            defaultPrimName.c_str()
        );
        return false;
    }

    std::string reason;
    if (!validateStageMetrics(upAxis, linearUnits, &reason))
    {
        TF_WARN(
            "Failed to configure UsdStage at \"%s\" due to invalid stage metrics: %s",
            stage->GetRootLayer()->GetIdentifier().c_str(),
            reason.c_str()
        );
        return false;
    }

    return uncheckedConfigureStage(stage, defaultPrimName, upAxis, linearUnits, authoringMetadata);
}

void usdex::core::saveStage(UsdStagePtr stage, const std::string& authoringMetadata, std::optional<std::string_view> comment)
{
    SdfLayerHandleVector dirtyLayers = UsdUtilsGetDirtyLayers(stage);
    for (auto& layer : dirtyLayers)
    {
        if (!layer->IsAnonymous() && !hasLayerAuthoringMetadata(layer))
        {
            setLayerAuthoringMetadata(layer, authoringMetadata);
        }
    }

    if (comment.has_value())
    {
        TF_STATUS("Saving \"%s\" with comment \"%s\"", UsdDescribe(stage).c_str(), comment.value().data());
        for (auto& layer : dirtyLayers)
        {
            if (!layer->IsAnonymous())
            {
                layer->SetComment(comment.value().data());
            }
        }
        stage->Save();
    }
    else
    {
        TF_STATUS("Saving \"%s\"", UsdDescribe(stage).c_str());
        stage->Save();
    }
}
