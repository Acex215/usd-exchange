# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
__all__ = ["createAssetPayload", "addAssetContent", "addAssetLibrary"]

from typing import Optional

from pxr import Ar, Sdf, Tf, Usd, UsdGeom

from ._StageAlgoBindings import createStage
from ._usdex_core import defineScope, getContentsToken, getLayerAuthoringMetadata, getLibraryToken, getPayloadToken, getValidPrimName


def createAssetPayload(stage: Usd.Stage, format: str = "usda", fileFormatArgs: Optional[dict] = None) -> Optional[Usd.Stage]:
    """
    Create an asset payload stage from an asset stage.

    The asset payload stage subLayers the different asset content stages (e.g., Geometry, Materials, etc.).
    This stage represents the root layer of the payload that the asset stage references through the "asset interface".

    Args:
        stage: The asset stage to create an asset payload stage from.
        format: The file format extension (default: "usda").
        fileFormatArgs: Additional file format-specific arguments to be supplied during stage creation.

    Returns:
        The newly created asset payload stage or None
    """
    # This function should mimic the behavior of the C++ function `usdex::core::createAssetPayload`.
    # It has been re-implemented here rather than bound to python using pybind11 due to issues with the transfer of ownership of the UsdStage object
    # from C++ to Python

    if not stage:
        Tf.Warn("Unable to create asset payload stage due to an invalid asset stage")
        return None

    if stage.GetRootLayer().anonymous:
        Tf.Warn("Unable to create asset payload stage due to an anonymous asset stage")
        return None

    resolver: Ar.Resolver = Ar.GetResolver()

    fileFormatArgs = fileFormatArgs or dict()

    payloadStage: Usd.Stage = createStage(
        resolver.CreateIdentifier(f"./{getPayloadToken()}/{getContentsToken()}.{format}", resolver.Resolve(stage.GetRootLayer().identifier)),
        defaultPrimName=stage.GetDefaultPrim().GetName(),
        upAxis=UsdGeom.GetStageUpAxis(stage),
        linearUnits=UsdGeom.GetStageMetersPerUnit(stage),
        authoringMetadata=getLayerAuthoringMetadata(stage.GetRootLayer()),
        fileFormatArgs=fileFormatArgs,
    )
    if not payloadStage:
        Tf.Warn("Unable to create asset payload stage")
        return None

    # Copy the asset stage's default prim to the asset payload stage
    success = Sdf.CopySpec(
        stage.GetRootLayer(),
        stage.GetDefaultPrim().GetPath(),
        payloadStage.GetRootLayer(),
        payloadStage.GetDefaultPrim().GetPath(),
    )
    if not success:
        Tf.Warn("Unable to copy the asset stage's default prim to the asset payload stage")
        return None

    return payloadStage


def addAssetLibrary(stage: Usd.Stage, name: str, format: str = "usdc", fileFormatArgs: Optional[dict] = None) -> Optional[Usd.Stage]:
    """
    Create a library layer from which the Asset Content stage can reference prims.

    This layer will contain a library of meshes, materials, prototypes for instances, or anything else that can be referenced by
    the asset content layers. It is not intended to be used as a standalone layer, the default prim will have a class specifier.

    Args:
        stage: The asset payload stage.
        name: The name of the library (e.g., "GeometryLibrary", "MaterialsLibrary").
        format: The file format extension (default: "usdc").
        fileFormatArgs: Additional file format-specific arguments to be supplied during stage creation.

    Returns:
        The newly created library stage, it will be named "nameLibrary.format" or None
    """
    # This function should mimic the behavior of the C++ function `usdex::core::addAssetLibrary`.
    # It has been re-implemented here rather than bound to python using pybind11 due to issues with the transfer of ownership of the UsdStage object
    # from C++ to Python

    if not stage:
        Tf.Warn("Unable to add asset library due to an invalid content stage")
        return None

    if stage.GetRootLayer().anonymous:
        Tf.Warn("Unable to add asset library due to an anonymous content stage")
        return None

    resolver: Ar.Resolver = Ar.GetResolver()
    relativeIdentifier = f"./{name}{getLibraryToken()}.{format}"
    identifier = resolver.CreateIdentifier(relativeIdentifier, resolver.Resolve(stage.GetRootLayer().identifier))

    fileFormatArgs = fileFormatArgs or dict()

    libraryStage: Usd.Stage = createStage(
        identifier,
        getValidPrimName(name),
        UsdGeom.GetStageUpAxis(stage),
        UsdGeom.GetStageMetersPerUnit(stage),
        getLayerAuthoringMetadata(stage.GetRootLayer()),
        fileFormatArgs=fileFormatArgs,
    )
    if not libraryStage:
        Tf.Warn("Unable to create a new stage for the asset library")
        return None

    # Create the asset library scope prim (with a class specifier)
    scope = defineScope(libraryStage.GetPseudoRoot(), name)
    if not scope:
        return None
    # Set the specifier to class
    scope.GetPrim().SetSpecifier(Sdf.SpecifierClass)
    return libraryStage


def addAssetContent(
    stage: Usd.Stage,
    name: str,
    format: str = "usda",
    fileFormatArgs: Optional[dict] = None,
    prependLayer: bool = True,
    createScope: bool = True,
) -> Optional[Usd.Stage]:
    """
    Create a content-specific stage to be added as a sublayer to the payload stage.

    This stage can define the hierarchical structure of the asset prims. It can reference prims in the asset library layers and author transform
    opinions on xformable prims. It can also contain the prim data if library layers are not being used.

    Args:
        stage: The asset payload stage to add the content-specific stage to
        name: The name of the content-specific stage (e.g., "Geometry", "Materials")
        format: The file format extension (default: "usda").
        fileFormatArgs: Additional file format-specific arguments to be supplied during stage creation.
        prependLayer: Whether to prepend (or append) the layer to the sublayer list (default: True).
        createScope: Whether to create a scope in the content stage (default: True).

    Returns:
        The newly created content stage or None
    """
    # This function should mimic the behavior of the C++ function `usdex::core::addAssetContent`.
    # It has been re-implemented here rather than bound to python using pybind11 due to issues with the transfer of ownership of the UsdStage object
    # from C++ to Python

    if not stage:
        Tf.Warn("Unable to add asset content due to an invalid payload stage")
        return None

    if stage.GetRootLayer().anonymous:
        Tf.Warn("Unable to add asset content due to an anonymous payload stage")
        return None

    resolver: Ar.Resolver = Ar.GetResolver()
    relativeIdentifier = f"./{name}.{format}"
    identifier = resolver.CreateIdentifier(relativeIdentifier, resolver.Resolve(stage.GetRootLayer().identifier))

    defaultPrim = stage.GetDefaultPrim()
    if not defaultPrim:
        Tf.Warn("Unable to add asset content due to an invalid default prim")
        return None

    fileFormatArgs = fileFormatArgs or dict()

    contentStage: Usd.Stage = createStage(
        identifier,
        defaultPrimName=defaultPrim.GetName(),
        upAxis=UsdGeom.GetStageUpAxis(stage),
        linearUnits=UsdGeom.GetStageMetersPerUnit(stage),
        authoringMetadata=getLayerAuthoringMetadata(stage.GetRootLayer()),
        fileFormatArgs=fileFormatArgs,
    )
    if not contentStage:
        Tf.Warn("Unable to create a new stage for the asset content")
        return None

    subLayerPaths = stage.GetRootLayer().subLayerPaths
    if prependLayer:
        subLayerPaths.insert(0, relativeIdentifier)
    else:
        subLayerPaths.append(relativeIdentifier)

    success = Sdf.CopySpec(
        stage.GetRootLayer(),
        stage.GetDefaultPrim().GetPath(),
        contentStage.GetRootLayer(),
        contentStage.GetDefaultPrim().GetPath(),
    )
    if not success:
        Tf.Warn("Unable to copy the payload stage's default prim to the asset content stage")
        return None

    if createScope:
        scope = defineScope(contentStage.GetDefaultPrim(), name)
        if not scope:
            Tf.Warn("Unable to create a scope in the asset content stage")
            return None

    return contentStage
