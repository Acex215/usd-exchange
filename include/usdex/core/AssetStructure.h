// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//

#pragma once

//! @file usdex/core/AssetStructure.h
//! @brief Utility functions to create atomic models based on sound asset structure principles

#include "Api.h"

#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/scope.h>

#include <optional>
#include <string>
#include <string_view>

namespace usdex::core
{

//! @defgroup assetStructure Asset Structure
//!
//! Utility functions for creating Assets following NVIDIA's
//! [Principles of Scalable Asset Structure](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html).
//!
//! An asset is a named, versioned, and structured container of one or more resources which may include composable OpenUSD layers, textures,
//! volumetric data, and more.
//!
//! This module aims to codify asset structures that have been proven scalable and have broad import compatibility across a wide range of OpenUSD
//! enabled applications, while guiding and simplifying the development process for new OpenUSD Exporters.
//!
//! # Atomic Models #
//!
//! Atomic models are entirely self contained, have no external dependencies, and are usually
//! [Components](https://openusd.org/release/glossary.html?highlight=kind#usdglossary-component) in the
//! [Model Hierarchy](https://openusd.org/release/glossary.html?highlight=kind#usdglossary-modelhierarchy).
//!
//! The following diagram shows the file, directory, layer, and reference structure of an atomic model:
//!
//! @code{.unparsed}
//!
//! +---------------------------+     +-----------------------------+
//! | Asset Stage w/ Interface  |     | Asset Content Layer         |
//! +---------------------------+     +-----------------------------+
//! | Flower                    | +---> Physics.usda                |
//! |  {                        | |   |  {                          |
//! |   defaultPrim=/Flower     | |   |   defaultPrim=/Flower       |
//! |  }                        | |   |  }                          |
//! |                           | |   |                             |
//! |  Xform Flower             | |   |  Xform Flower               |
//! |   payloads[               | |   |   Scope Geometry            |
//! |    ./Payload/Contents.usda| |   |    # physics attrs applied  |
//! |   ]           |           | |   |    # to prims               |
//! +---------------+-----------+ |   |   Scope Materials           |
//!                 |             |   |    Material PhysicsMaterial |
//!                 |             |   +-----------------------------+
//!                 |             |
//!                 |             |   +-----------------------------+
//! +---------------v-----------+ |   | Asset Content Layer         |
//! | Asset Payload Stage       | |   +-----------------------------+
//! +---------------------------+ | +-> Materials.usda              |+------------------------+
//! | Contents.usda             | | | |  {                          || Asset Library Layer    |
//! |  {                        | | | |   defaultPrim=/Flower       |+------------------------+
//! |   defaultPrim=/Flower     | | | |  }                          || MaterialsLibrary.usdc  |
//! |   sublayers[              | | | |                             ||  {                     |
//! |    ./Physics.usda---------+-+ | |  Xform Flower               ||  defaultPrim=/Materials|
//! |    ./Materials.usda-------+---+ |   Scope Materials           ||  }                     |
//! |    ./Geometry.usda--------+--+  | +->Material Clay            ||                        |
//! |  }                        |  |  | |   reference[              ||  Scope Materials       |
//! |                           |  |  | |    ./MaterialsLibrary.usdc++-->Material Clay        |
//! |  Xform Flower             |  |  | |   ]                       ||   Material GreenStem   |
//! +---------------------------+  |  | | over Geometry             ||   Material PinkPetal   |
//!                                |  | |  over Planter {           |+------------------------+
//!                                |  | +----material:binding=Clay  |
//!                                |  |    }                        |
//!                                |  +-----------------------------+
//!                                |
//!                                |  +-----------------------------+
//!                                |  | Asset Content Layer         |
//!                                |  +-----------------------------+
//!                                +--> Geometry.usda               |+------------------------+
//!                                   |  {                          || Asset Library Layer    |
//!                                   |   defaultPrim=/Flower       |+------------------------+
//!                                   |  }                          || GeometryLibrary.usdc   |
//!                                   |                             ||  {                     |
//!                                   |  Xform Flower               ||   defaultPrim=/Geometry|
//!                                   |   Scope Geometry            ||  }                     |
//!                                   |    Mesh Planter             ||                        |
//!                                   |     reference[              ||  Scope Geometry        |
//!                                   |      ./GeometryLibrary.usdc-++-->Mesh Planter         |
//!                                   |     ]                       ||   Mesh Stem            |
//!                                   |    ...                      ||   Mesh Petals          |
//!                                   +-----------------------------++------------------------+
//! @endcode
//!
//! ## Authoring an Atomic Model ##
//!
//! An example sequence for authoring the Flower atomic asset:
//! 1. Create an asset stage using `usdex::core::createStage()`, setting the defaultPrim to `/Flower`
//! 2. Create an asset payload stage using `usdex::core::createAssetPayload(assetStage)`
//! 3. Add a geometry library using `usdex::core::addAssetLibrary(payloadStage, "Geometry")`
//!   - Add planter, stem, and petals meshes to the geometry library
//! 4. Add a materials library using `usdex::core::addAssetLibrary(payloadStage, "Materials")`
//!   - Add clay, green stem, and pink petals materials to the materials library
//! 5. Add a geometry content layer using `usdex::core::addAssetContent(payloadStage, "Geometry")`
//!   - Add planter, stem, and petals references that contain xformOps
//! 6. Add a materials content layer using `usdex::core::addAssetContent(payloadStage, "Materials")`
//!   - Add clay, green stem, and pink petals references and bind them to the geometry
//! 7. Add the asset interface to the asset stage using `usdex::core::addAssetInterface(assetStage, payloadStage)`
//!
//! # Principles of Scalable Asset Structure #
//!
//! When developing an asset structure, the following principles can guide toward a scalable structure:
//!
//! - Legibility:
//!   - Use descriptive names for stages, scopes, and prims. This might mean using a name like `LargeCardboardBox` or `ID-2023_5678`,
//!     depending on the context.
//!   - The tokens used in this module for files, directories, scopes, and layer names can make things clear and consistent.
//! - Modularity:
//!   - The structure should facilitate iterative improvement of reusable content.
//!   - The functions in this module use relative paths to allow for asset relocation.
//!   - The asset library layer concept allows for the reuse of content within an asset.
//! - Performance:
//!   - The structure should accelerate content read and write speeds for users and processes.
//!   - This could refer to an individual working within an asset or the ability to render millions of preview instances.
//!   - This module creates a payload (allowing for deactivation) with extents hints so that the asset can be used in a larger scene.
//!   - This module allows the use of text USDA files for lightweight layers and binary USDC files for complex library data.
//! - Navigability:
//!   - The structure should facilitate discovery of elements while retaining flexibility.
//!   - The assets should be structured around multiple hierarchical paths (file, directory, prim paths, model hierarchy, etc.).
//!   - This module offers functions to generate consistent asset structures.
//!
//! @note These asset structure functions are highly opinionated and implement best practices following NVIDIA's
//! [Principles of Scalable Asset Structure](https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html).
//! They provide broad import compatibility across a wide range of OpenUSD enabled applications. However, if you require more
//! flexibility to suit one specific application, renderer, or custom pipeline, these functions may serve you better as a sample implementation
//! rather than something you call directly.
//!
//! @{

//! Get the Asset token
//!
//! @returns The Asset token
USDEX_API const pxr::TfToken& getAssetToken();

//! Get the token for the Contents stage
//!
//! @returns The token for the Contents stage
USDEX_API const pxr::TfToken& getContentsToken();

//! Get the token for the Geometry stage and scope
//!
//! @returns The token for the Geometry stage and scope
USDEX_API const pxr::TfToken& getGeometryToken();

//! Get the token for the Library stage
//!
//! @returns The token for the Library stage
USDEX_API const pxr::TfToken& getLibraryToken();

//! Get the token for the Materials stage and scope
//!
//! @returns The token for the Materials stage and scope
USDEX_API const pxr::TfToken& getMaterialsToken();

//! Get the token for the Payload directory
//!
//! @returns The token for the Payload directory
USDEX_API const pxr::TfToken& getPayloadToken();

//! Get the token for the Physics stage and scope
//!
//! @returns The token for the Physics stage and scope
USDEX_API const pxr::TfToken& getPhysicsToken();

//! Get the token for the Textures directory
//!
//! @returns The token for the Textures directory
USDEX_API const pxr::TfToken& getTexturesToken();

//! Defines a scope on the stage.
//!
//! A scope is a simple grouping primitive that is useful for organizing prims in a scene.
//!
//! @param stage The stage on which to define the scope
//! @param path The absolute prim path at which to define the scope
//!
//! @returns UsdGeomScope schema wrapping the defined UsdPrim. Returns an invalid schema on error.
USDEX_API pxr::UsdGeomScope defineScope(pxr::UsdStagePtr stage, const pxr::SdfPath& path);

//! Defines a scope on the stage.
//!
//! This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.
//!
//! @param parent Prim below which to define the scope
//! @param name Name of the scope
//!
//! @returns UsdGeomScope schema wrapping the defined UsdPrim. Returns an invalid schema on error.
USDEX_API pxr::UsdGeomScope defineScope(pxr::UsdPrim parent, const std::string& name);

//! Defines a scope from an existing prim.
//!
//! This converts an existing prim to a Scope type.
//!
//! @param prim The existing prim to convert to a scope
//!
//! @returns UsdGeomScope schema wrapping the defined UsdPrim. Returns an invalid schema on error.
USDEX_API pxr::UsdGeomScope defineScope(pxr::UsdPrim prim);

//! Define a reference to a prim
//!
//! This creates a reference prim that targets a prim in another layer (external reference) or the same layer (internal reference).
//! The reference's assetPath will be set to the relative identifier between the stage's edit target and the source's stage if it's
//! an external reference with a valid relative path.
//!
//! For more information, see:
//! - https://openusd.org/release/glossary.html#usdglossary-references
//! - https://openusd.org/release/api/class_usd_references.html#details
//!
//! @param stage The stage on which to define the reference
//! @param path The absolute prim path at which to define the reference
//! @param source The prim to reference
//!
//! @returns The newly created reference prim. Returns an invalid prim on error.
USDEX_API pxr::UsdPrim defineReference(pxr::UsdStagePtr stage, const pxr::SdfPath& path, const pxr::UsdPrim& source);

//! Define a reference to a prim as a child of the `parent` prim
//!
//! This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.
//!
//! @param parent The parent prim to add the reference to
//! @param source The prim to reference
//! @param name The name of the reference. If not provided, uses the source prim's name
//!
//! @returns The newly created reference prim. Returns an invalid prim on error.
USDEX_API pxr::UsdPrim defineReference(pxr::UsdPrim parent, const pxr::UsdPrim& source, std::optional<std::string_view> name = std::nullopt);

//! Define a payload to a prim
//!
//! This creates a payload prim that targets a prim in another layer (external payload) or the same layer (internal payload)
//! The payload's assetPath will be set to the relative identifier between the stage's edit target and the source's stage if it's
//! an external payload with a valid relative path.
//!
//! For more information, see:
//! - https://openusd.org/release/glossary.html#usdglossary-payload
//! - https://openusd.org/release/api/class_usd_payloads.html#details
//!
//! @param stage The stage on which to define the payload
//! @param path The absolute prim path at which to define the payload
//! @param source The payload to add
//!
//! @returns The newly created payload prim. Returns an invalid prim on error.
USDEX_API pxr::UsdPrim definePayload(pxr::UsdStagePtr stage, const pxr::SdfPath& path, const pxr::UsdPrim& source);

//! Define a payload to a prim as a child of the `parent` prim
//!
//! This is an overloaded member function, provided for convenience. It differs from the above function only in what arguments it accepts.
//!
//! @param parent The parent prim to add the payload to
//! @param source The payload to add
//! @param name The name of the payload. If not provided, uses the source prim's name
//!
//! @returns The newly created payload prim. Returns an invalid prim on error.
USDEX_API pxr::UsdPrim definePayload(pxr::UsdPrim parent, const pxr::UsdPrim& source, std::optional<std::string_view> name = std::nullopt);

//! Create a payload stage for an asset interface stage to reference.
//!
//! The payload stage subLayers the different asset content stages (e.g., Geometry, Materials, etc.).
//! This stage represents the root layer of the payload that the asset interface stage references.
//! This function does not create the actual payload, that is done by the `usdex::core::addAssetInterface()` function.
//!
//! @param stage The asset stage to create an asset payload stage from
//! @param format The file format extension (default: "usda")
//! @param fileFormatArgs Additional file format-specific arguments to be supplied during stage creation.
//! @returns The newly created asset payload stage
USDEX_API pxr::UsdStageRefPtr createAssetPayload(
    pxr::UsdStagePtr stage,
    const std::string& format = "usda",
    const pxr::SdfLayer::FileFormatArguments& fileFormatArgs = pxr::SdfLayer::FileFormatArguments()
);

//! Create a library layer from which the Asset Content stage can reference prims
//!
//! This layer will contain a library of meshes, materials, prototypes for instances, or anything else that can be referenced by
//! the asset content layers. It is not intended to be used as a standalone layer, the default prim will have a class specifier.
//!
//! @param stage The asset payload stage
//! @param name The name of the library (e.g., "Geometry", "Materials")
//! @param format The file format extension (default: "usdc")
//! @param fileFormatArgs Additional file format-specific arguments to be supplied during stage creation.
//! @returns The newly created library stage, it will be named "nameLibrary.format"
USDEX_API pxr::UsdStageRefPtr addAssetLibrary(
    pxr::UsdStagePtr stage,
    const std::string& name,
    const std::string& format = "usdc",
    const pxr::SdfLayer::FileFormatArguments& fileFormatArgs = pxr::SdfLayer::FileFormatArguments()
);

//! Create a content-specific stage to be added as a sublayer to the payload stage
//!
//! This stage can define the hierarchical structure of the asset prims. It can reference prims in the asset library layers and author transform
//! opinions on xformable prims. It can also contain the prim data if library layers are not being used.
//!
//! @param stage The asset payload stage to add the content-specific stage to
//! @param name The name of the content-specific stage (e.g., "Geometry", "Materials")
//! @param format The file format extension (default: "usda")
//! @param fileFormatArgs Additional file format-specific arguments to be supplied during stage creation.
//! @param prependLayer Whether to prepend (or append) the layer to the sublayer list (default: true)
//! @param createScope Whether to create a scope in the content stage (default: true)
//! @returns The newly created asset content stage
USDEX_API pxr::UsdStageRefPtr addAssetContent(
    pxr::UsdStagePtr stage,
    const std::string& name,
    const std::string& format = "usda",
    const pxr::SdfLayer::FileFormatArguments& fileFormatArgs = pxr::SdfLayer::FileFormatArguments(),
    bool prependLayer = true,
    bool createScope = true
);

//! Add an asset interface to a stage from a source stage
//!
//! This function configures the stage with the source stage's metadata, copies the defaultPrim from the source stage, and
//! annotates the asset interface with USD model metadata including component kind, asset name, and extents hint.
//!
//! @param stage The stage to add the asset interface to
//! @param source The stage that the interface will reference
//! @returns True if the asset interface was added successfully, false otherwise
USDEX_API bool addAssetInterface(pxr::UsdStagePtr stage, const pxr::UsdStagePtr source);

//! @}

} // namespace usdex::core
