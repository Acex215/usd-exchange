// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "usdex/core/NameAlgo.h"

#include "usdex/pybind/UsdBindings.h"

#include <pybind11/pybind11.h>

using namespace usdex::core;
using namespace pybind11;

namespace usdex::core::bindings
{

void bindNameAlgo(module& m)
{
    m.def(
        "getValidPrimName",
        &getValidPrimName,
        arg("name"),
        R"(
            Produce a valid prim name from the input name

            Args:
                name: The input name

            Returns:
                A string that is considered valid for use as a prim name.
        )"
    );

    m.def(
        "getValidPrimNames",
        &getValidPrimNames,
        arg("names"),
        arg("reservedNames") = list(),
        R"(
            Take a vector of the preferred names and return a matching vector of valid and unique names.

            Args:
                names: A vector of preferred prim names.
                reservedNames: A vector of reserved prim names. Names in the vector will not be included in the returns.

            Returns:
                A vector of valid and unique names.
        )"
    );

    m.def(
        "getValidChildName",
        &getValidChildName,
        arg("prim"),
        arg("name"),
        R"(
            Take a prim and a preferred name. Return a valid and unique name as the child name of the given prim.

            Args:
                prim: The USD prim where the given prim name should live under.
                names: A preferred prim name.

            Returns:
                A valid and unique name.
        )"
    );

    m.def(
        "getValidChildNames",
        &getValidChildNames,
        arg("prim"),
        arg("names"),
        R"(
            Take a prim and a vector of the preferred names. Return a matching vector of valid and unique names as the child names of the given prim.

            Args:
                prim: The USD prim where the given prim names should live under.
                names: A vector of preferred prim names.

            Returns:
                A vector of valid and unique names.
        )"
    );

    m.def(
        "getValidPropertyName",
        &getValidPropertyName,
        arg("name"),
        R"(
            Produce a valid property name using the Bootstring algorithm.

            Args:
                name: The input name

            Returns:
                A string that is considered valid for use as a property name.
        )"
    );

    m.def(
        "getValidPropertyNames",
        &getValidPropertyNames,
        arg("names"),
        arg("reservedNames") = list(),
        R"(
            Take a vector of the preferred names and return a matching vector of valid and unique names.

            Args:
                names: A vector of preferred property names.
                reservedNames: A vector of reserved prim names. Names in the vector will not be included in the return.

            Returns:
                A vector of valid and unique names.
        )"
    );

    ::class_<ValidChildNameCache>(
        m,
        "ValidChildNameCache",
        R"(
            A caching mechanism for valid and unique child prim names.

            For best performance, this object should be reused for multiple name requests.

            It is not valid to request child names from prims from multiple stages as only the prim path is used as the cache key.

            Warning:

                This class does not automatically invalidate cached values based on changes to the stage from which values were cached.
                Additionally, a separate instance of this class should be used per-thread, calling methods from multiple threads is not safe.
        )"
    )

        .def(::init())

        .def(
            "getValidChildNames",
            &ValidChildNameCache::getValidChildNames,
            arg("prim"),
            arg("names"),
            R"(
                Take a prim and a vector of the preferred names. Return a matching vector of valid and unique names as the child names of the given prim.

                Args:

                    prim: The USD prim where the given prim names should live under.
                    names: A vector of preferred prim names.

                Returns:
                    A vector of valid and unique names.
            )"
        )

        .def(
            "getValidChildName",
            &ValidChildNameCache::getValidChildName,
            arg("prim"),
            arg("name"),
            R"(

                Take a prim and a preferred name. Return a valid and unique name for use as the child name of the given prim.

                Args:
                    prim: The prim that the child name should be valid for.
                    names: Preferred prim name.

                Returns:
                    Valid and unique name.
            )"
        )

        .def(
            "update",
            &ValidChildNameCache::update,
            arg("prim"),
            R"(
            Update the name cache for a Prim to include all existing children.

            This does not clear the cache, so any names that have been previously returned will still be reserved.

            Args:
                prim: The prim that child names should be updated for.
        )"
        )

        .def(
            "clear",
            &ValidChildNameCache::clear,
            arg("clear"),
            R"(
            Clear the name cache for a Prim.

            Args:
                prim: The prim that child names should be cleared for.
        )"
        );

    m.def(
        "getDisplayName",
        &getDisplayName,
        arg("prim"),
        R"(
            Return this prim's display name (metadata).

            Args:
                prim: The prim to get the display name from

            Returns:
                Authored value, or an empty string if no display name has been set.

        )"
    );
    m.def(
        "setDisplayName",
        &setDisplayName,
        arg("prim"),
        arg("name"),
        R"(
            Sets this prim's display name (metadata)

            DisplayName is meant to be a descriptive label, not necessarily an alternate identifier; therefore there is no restriction on which
            characters can appear in it

            Args:
                prim: The prim to set the display name for
                name: The value to set

            Returns:
                True on success, otherwise false

        )"
    );
    m.def(
        "clearDisplayName",
        &clearDisplayName,
        arg("prim"),
        R"(
            Clears this prim's display name (metadata) in the current EditTarget (only)

            Args:
                prim: The prim to clear the display name for

            Returns:
                True on success, otherwise false

        )"
    );
    m.def(
        "blockDisplayName",
        &blockDisplayName,
        arg("prim"),
        R"(
            Block this prim's display name (metadata)

            The fallback value will be explicitly authored to cause the value to resolve as if there were no authored value opinions in weaker layers

            Args:
                prim: The prim to block the display name for

            Returns:
                True on success, otherwise false

        )"
    );
    m.def(
        "computeEffectiveDisplayName",
        &computeEffectiveDisplayName,
        arg("prim"),
        R"(
            Calculate the effective display name of this prim

            If the display name is un-authored or empty then the prim's name is returned

            Args:
                prim: The prim to compute the display name for

            Returns:
                The effective display name

        )"
    );
}

} // namespace usdex::core::bindings
