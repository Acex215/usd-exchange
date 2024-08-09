# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import omni.transcoding
import usdex.core
import usdex.test
from pxr import Sdf, Usd, UsdGeom


class ValidPrimNamesTestCase(usdex.test.TestCase):
    def assertPropertyNameIsValid(self, name, msg=None):
        """Assert that the given name is valid for a UsdProperty"""
        path = Sdf.Path("/foo").AppendProperty(name)
        if msg is None:
            msg = f"Appending '{name}' as a property of an SdfPath produces an invalid path."
        self.assertTrue(path, msg=msg)

    def testGetValidPrimName(self):
        # An empty string will return the minimal valid name
        self.assertEqual(usdex.core.getValidPrimName(""), "tn__")

        # Illegal characters are correctly encoded
        self.assertEqual(usdex.core.getValidPrimName("/"), "tn__l0")
        self.assertEqual(usdex.core.getValidPrimName("#"), "tn__Z0")
        self.assertEqual(usdex.core.getValidPrimName(" "), "tn__W0")

        # Leading numerics are correctly encoded
        self.assertEqual(usdex.core.getValidPrimName("1"), "tn__1_")
        self.assertEqual(usdex.core.getValidPrimName("1_mesh"), "tn__1_mesh_")

        # A combination of illegal characters and leading numerics
        self.assertEqual(usdex.core.getValidPrimName("1 mesh"), "tn__1mesh_c5")

        # A valid name will return that same value
        self.assertEqual(usdex.core.getValidPrimName("_"), "_")
        self.assertEqual(usdex.core.getValidPrimName("_1"), "_1")
        self.assertEqual(usdex.core.getValidPrimName("mesh"), "mesh")

        # UTF-8 characters are correctly encoded and decoded.
        self.assertEqual(usdex.core.getValidPrimName("カーテンウォール"), "tn__sxB76l2Y5o0X16")
        self.assertEqual(omni.transcoding.decodeBootstringIdentifier(usdex.core.getValidPrimName("カーテンウォール")), "カーテンウォール")

        # ISO-8859-1 encoding will cause encoding to fail resulting in the fallback character substitution being used.
        # The fallback character substitution slightly differs from pxr::TfMakeValidIdentifier in how it handles leading numerics
        self.assertEqual(usdex.core.getValidPrimName("mesh_Ä".encode("latin-1")), "mesh__")
        self.assertEqual(usdex.core.getValidPrimName("1_Ä".encode("latin-1")), "_1__")

    def testGetValidPrimNames(self):
        def assertEqualPrimNames(inputNames, reservedNames, expectNames):
            self.assertEqual(usdex.core.getValidPrimNames(inputNames, reservedNames), expectNames)

        def assertDecoding(inputNames, expectNames):
            for inputName, expectName in zip(inputNames, expectNames):
                self.assertEqual(omni.transcoding.decodeBootstringIdentifier(inputName), expectName)

        # Basic tests
        assertEqualPrimNames(["cube", "cube_1", "sphere", "cube_3"], [], ["cube", "cube_1", "sphere", "cube_3"])

        # Invalid characters
        assertEqualPrimNames(
            ["123cube", "cube1", r"sphere%$%#ad@$1", "cube_3", "cube$3"],
            [],
            ["tn__123cube_", "cube1", "tn__spheread1_kAHAJ8jC", "cube_3", "tn__cube3_Y6"],
        )
        assertDecoding(
            ["tn__123cube_", "cube1", "tn__spheread1_kAHAJ8jC", "cube_3", "tn__cube3_Y6"],
            ["123cube", "cube1", r"sphere%$%#ad@$1", "cube_3", "cube$3"],
        )

        # Duplicated names in list
        assertEqualPrimNames(["cube", "sphere", "sphere", "cube_1", "cube_1"], [], ["cube", "sphere", "sphere_1", "cube_1", "cube_1_1"])

        # Reserved names
        assertEqualPrimNames(
            ["cube_1", "sphere", "sphere", "sphere_1", "cube_1"],
            ["cube_1", "cube_1_1", "cube_3", "sphere_1", "sphere_1_1"],
            ["cube_1_2", "sphere", "sphere_2", "sphere_1_2", "cube_1_3"],
        )

        # Double underscores
        assertEqualPrimNames(
            ["cube__1", "cube__1", "sphere", "sphere", "cube__1"],
            ["sphere_1"],
            ["cube__1", "cube__1_1", "sphere", "sphere_2", "cube__1_2"],
        )

        # Collisions created when making values valid
        assertEqualPrimNames(["100_mesh", "200_mesh", "300_mesh"], [], ["tn__100_mesh_", "tn__200_mesh_", "tn__300_mesh_"])

        # Empty string names
        assertEqualPrimNames(["", "", ""], [], ["tn__", "_1", "_2"])

        # Empty name
        assertEqualPrimNames([], [], [])

        # Return as many preferred names as possible
        assertEqualPrimNames(["sphere", "sphere", "sphere_1", "sphere", "sphere_2"], [], ["sphere", "sphere_3", "sphere_1", "sphere_4", "sphere_2"])

        # UTF-8 words
        assertEqualPrimNames(["カーテンウォール", "カーテンウォール"], [], ["tn__sxB76l2Y5o0X16", "tn___1_cvb0DAd4k7Z1p16"])
        assertDecoding(
            ["tn__sxB76l2Y5o0X16", "tn___1_cvb0DAd4k7Z1p16"],
            ["カーテンウォール", "カーテンウォール_1"],
        )

        # ISO-8859-1 encoding will cause encoding to fail resulting in the fallback character substitution being used.
        # This can increase the number of name collisions.
        assertEqualPrimNames(
            [x.encode("latin-1") for x in ["mesh_Ä", "mesh-Ä", "mesh/Ä", "mesh.Ä"]],
            [],
            ["mesh__", "mesh___1", "mesh___2", "mesh___3"],
        )

    def testGetValidChildName(self):
        # Define a prim for which we will get a valid child name
        stage = Usd.Stage.CreateInMemory()
        prim = UsdGeom.Xform.Define(stage, "/Root").GetPrim()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        self.assertIsValidUsd(stage)

        # Add a child with a "def" specifier
        UsdGeom.Xform.Define(stage, "/Root/cube")
        # Add a child with an "class" specifier
        stage.CreateClassPrim("/Root/cube_1")
        # Add a child with an "over" specifier
        UsdGeom.Xform.Define(stage, "/Root/cube_2")
        # Define and deactivate a child
        UsdGeom.Xform.Define(stage, "/Root/cube_3").GetPrim().SetActive(False)

        # Existing names on stage with inactivate prim
        self.assertEqual(usdex.core.getValidChildName(prim, "cube"), "cube_4")
        self.assertEqual(usdex.core.getValidChildName(prim, "cube_1"), "cube_1_1")
        self.assertEqual(usdex.core.getValidChildName(prim, "sphere"), "sphere")
        self.assertEqual(usdex.core.getValidChildName(prim, "cube_3"), "cube_3_1")

        # Illegal names
        self.assertEqual(usdex.core.getValidChildName(prim, "123cube"), "tn__123cube_")
        self.assertEqual(usdex.core.getValidChildName(prim, r"sphere%$%#ad@$1"), "tn__spheread1_kAHAJ8jC")
        self.assertEqual(usdex.core.getValidChildName(prim, "cube$3"), "tn__cube3_Y6")
        self.assertEqual(usdex.core.getValidChildName(prim, ""), "tn__")

    def testGetValidChildNames(self):
        # Define a prim for which we will get valid child names
        stage = Usd.Stage.CreateInMemory()
        prim = UsdGeom.Xform.Define(stage, "/Root").GetPrim()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        self.assertIsValidUsd(stage)

        # Add a child with a "def" specifier
        UsdGeom.Xform.Define(stage, "/Root/cube")
        # Add a child with an "class" specifier
        stage.CreateClassPrim("/Root/cube_1")
        # Add a child with an "over" specifier
        UsdGeom.Xform.Define(stage, "/Root/cube_2")
        # Define and deactivate a child
        UsdGeom.Xform.Define(stage, "/Root/cube_3").GetPrim().SetActive(False)

        def assertEqualPrimNames(inputNames, expectNames):
            self.assertEqual(usdex.core.getValidChildNames(prim, inputNames), expectNames)

        # Exist names on stage with inactivate prim
        assertEqualPrimNames(["cube", "cube_1", "sphere", "cube_3"], ["cube_4", "cube_1_1", "sphere", "cube_3_1"])

        # Exist names on stage with inactivate prim - invalid characters
        assertEqualPrimNames(
            ["123cube", "cube1", r"sphere%$%#ad@$1", "cube_3", "cube$3"],
            ["tn__123cube_", "cube1", "tn__spheread1_kAHAJ8jC", "cube_3_1", "tn__cube3_Y6"],
        )

        # Duplicated names in list
        assertEqualPrimNames(["cube", "sphere", "sphere", "cube_1"], ["cube_4", "sphere", "sphere_1", "cube_1_1"])

        # Conflicted names
        assertEqualPrimNames(["cube_1", "sphere", "sphere", "sphere_1", "cube_1"], ["cube_1_1", "sphere", "sphere_2", "sphere_1", "cube_1_2"])

        # Double underscores
        assertEqualPrimNames(["cube__1", "cube__1", "sphere", "sphere", "cube__1"], ["cube__1", "cube__1_1", "sphere", "sphere_1", "cube__1_2"])

        # Collisions created when making values valid
        assertEqualPrimNames(["100_mesh", "200_mesh", "300_mesh"], ["tn__100_mesh_", "tn__200_mesh_", "tn__300_mesh_"])

        # Empty string names
        assertEqualPrimNames(["", "", ""], ["tn__", "_1", "_2"])

        # Empty name
        assertEqualPrimNames([], [])

        # Return as many preferred names as possible
        assertEqualPrimNames(["sphere", "sphere", "sphere_1", "sphere", "sphere_2"], ["sphere", "sphere_3", "sphere_1", "sphere_4", "sphere_2"])

        self.assertIsValidUsd(stage)

    def testGetValidPropertyName(self):
        # Test cases for getValidPropertyName() where the values are (<name>, <result>)
        data = [
            # An empty string will return the minimal valid name
            ("", "tn__"),
            # Names containing only delimiters will imply an empty string before, after and between delimiters
            (":", "tn__:tn__"),
            ("::", "tn__:tn__:tn__"),
            # In the presence of valid names delimiters still imply a minimum of empty string before, after and between delimiters
            (":name", "tn__:name"),
            ("name:", "name:tn__"),
            ("name::name", "name:tn__:name"),
            ("name:name::", "name:name:tn__:tn__"),
            ("::name:name", "tn__:tn__:name:name"),
            # Illegal characters are correctly encoded, but encoding occurs within namespaces
            ("/", "tn__l0"),
            ("/:name:/", "tn__l0:name:tn__l0"),
            ("name:#:#", "name:tn__Z0:tn__Z0"),
            (" :%:", "tn__W0:tn__b0:tn__"),
            # Leading numerics are correctly encoded
            ("1", "tn__1_"),
            ("1:2:3", "tn__1_:tn__2_:tn__3_"),
            ("1_name", "tn__1_name_"),
            # A combination of illegal characters and leading numerics
            ("1 name", "tn__1name_c5"),
            # A property SdfPath will be encoded as it contains additional delimiters that a property name cannot support
            # These tests are included to assert our requirements that differ from the behavior of omni.transcoding.encodeBootstringPath()
            ("/foo/bar.property:name:space", "tn__foobarproperty_jLG4:name:space"),
            ("/foo/bar.property[/target].relAttr", "tn__foobarpropertytargetrelAttr_se0LU4Hhk0V2"),
            ("/foo/bar{var=sel}", "tn__foobarvarsel_rI4Z6dV0o0"),
            # A valid name will return that same value
            ("_", "_"),
            ("_1", "_1"),
            ("name", "name"),
            ("primvars:my:color", "primvars:my:color"),
            # UTF-8 characters are correctly encoded.
            ("カーテンウォール", "tn__sxB76l2Y5o0X16"),
            ("カーテンウォール:Bäcker", "tn__sxB76l2Y5o0X16:tn__Bcker_ah0"),
        ]

        # Assert that each test returns the expected result and that the name is in fact a valid property name.
        # FUTURE: Add an assertion about decoding once that is supported.
        for name, expected in data:
            returned = usdex.core.getValidPropertyName(name)
            self.assertEqual(returned, expected, msg=f"Unexpected result calling getValidPropertyName('{name}')")
            self.assertPropertyNameIsValid(returned)

    def testGetValidPropertyNames(self):
        # Test cases for getValidPropertyNames() where the values are (<names>, <reservedNames>, <result>)
        data = [
            # An empty list is supported
            ([], [], []),
            # Empty values are supported via encoding, when empty values collide the numeric suffix alone is legal and will not be encoded
            ([""], [], ["tn__"]),
            (["", ""], [], ["tn__", "_1"]),
            # Valid names are supported and will have a numeric suffix added when they collide
            (["foo", "bar"], [], ["foo", "bar"]),
            (["foo", "foo"], [], ["foo", "foo_1"]),
            (["foo", "foo"], ["foo"], ["foo_1", "foo_2"]),
            # The supplied name will be used for any index if possible, even if another collision would generate that name
            (["foo", "foo", "foo_1"], [], ["foo", "foo_2", "foo_1"]),
            (["foo", "foo_1"], ["foo"], ["foo_2", "foo_1"]),
            # When namespaced property names collide the last token will have a numeric suffix added
            # The same rules about using requested names where possible apply
            (["foo:bar", "foo:bar"], [], ["foo:bar", "foo:bar_1"]),
            (["foo:bar", "foo:bar", "foo:bar_1"], [], ["foo:bar", "foo:bar_2", "foo:bar_1"]),
            # Names with illegal characters (from a property name POV) will be encoded, the encoding will happen within each namespace
            (["foo bar", "1_foo", "foo/bar", "foo.bar"], [], ["tn__foobar_f6", "tn__1_foo_", "tn__foobar_r9", "tn__foobar_k9"]),
            (["foo bar:1_foo", "foo/bar:foo.bar"], [], ["tn__foobar_f6:tn__1_foo_", "tn__foobar_r9:tn__foobar_k9"]),
            # UTF-8 characters will be encoded and collisions will be resolved before encoding
            (["カーテンウォール", "Bäcker"], [], ["tn__sxB76l2Y5o0X16", "tn__Bcker_ah0"]),
            (["fooØ:münich", "fooØ:münich"], [], ["tn__foo_zQ:tn__mnich_ul0", "tn__foo_zQ:tn__mnich_1_XX1"]),
            # When an encoded names collides with a reserved or requested name, the numeric suffix appears to be added happen
            ([""], ["tn__"], ["_1"]),
            # NOTE: This is an unexpected result, but is probably of little concern
            # I would prefer the result to be ["_1", "tn__", "tn___1"] so that;
            # - the 1st value is made unique by adding a suffix before encoding.
            # - the 2nd value is retained because it can be.
            # - the 3rd value is made unique by adding a suffix.
            (["", "tn__", "tn__"], [], ["tn__", "tn___1", "tn___2"]),
        ]

        # FUTURE: Add an assertion about decoding once that is supported.
        for names, reservedNames, expected in data:
            returned = usdex.core.getValidPropertyNames(names, reservedNames=reservedNames)

            # There should always be the same number of values in the return as the number of names supplied.
            msg = f"Unexpected result count calling getValidPropertyName({str(names)}, reservedNames={str(reservedNames)})"
            self.assertEqual(len(names), len(returned), msg=msg)

            # There should never be any duplicates in the return
            msg = f"Duplicate names produced calling getValidPropertyName({str(names)}, reservedNames={str(reservedNames)})"
            self.assertTrue((len(returned) == len(set(returned))), msg=msg)

            # The result should match
            msg = f"Unexpected result calling getValidPropertyName({str(names)}, reservedNames={str(reservedNames)})"
            self.assertEqual(returned, expected, msg=msg)

            # None of the reserved names should have been returned
            for name in reservedNames:
                msg = f"Reserved name returned when calling getValidPropertyName({str(names)}, reservedNames={str(reservedNames)})"
                self.assertNotIn(name, returned, msg=msg)

            # Each name returned should be valid for a property name
            for name in returned:
                msg = f"Invalid property name '{name}' returned when calling getValidPropertyName({str(names)}, reservedNames={str(reservedNames)})"
                self.assertPropertyNameIsValid(name, msg=msg)

    def testGetValidPropertyNamesForMultiApplySchema(self):
        # The getValidPropertyNames() function can be used to get valid and unique names that can be used with multi-apply schema

        def getAllCollectionNames(prim):
            return [x.GetName() for x in Usd.CollectionAPI.GetAllCollections(prim)]

        # Define a prim on which to apply some collections
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        prim = stage.GetPrimAtPath("/Root")

        # Apply some that we know are valid
        Usd.CollectionAPI.Apply(prim, "foo")
        Usd.CollectionAPI.Apply(prim, "bar")

        # Assert the expected collection names
        self.assertEqual(set(getAllCollectionNames(prim)), set(["foo", "bar"]))

        # With the existing collection names reserved apply the same named collections again
        # The names will be made unique and valid and the new collections will not collide
        names = ["foo", "bar"]
        for name in usdex.core.getValidPropertyNames(names, reservedNames=getAllCollectionNames(prim)):
            Usd.CollectionAPI.Apply(prim, name)

        # Assert the expected collection names
        self.assertEqual(set(getAllCollectionNames(prim)), set(["foo", "bar", "foo_1", "bar_1"]))

        # Apply some collections with names that are illegal for properties
        names = ["😍.😸", "Bäcker", "foo bar"]
        for name in usdex.core.getValidPropertyNames(names, reservedNames=getAllCollectionNames(prim)):
            Usd.CollectionAPI.Apply(prim, name)

        # Assert the expected collection names
        self.assertEqual(set(getAllCollectionNames(prim)), set(["foo", "bar", "foo_1", "bar_1", "tn__foobar_f6", "tn__Bcker_ah0", "tn__k0zfn7c3"]))


class ValidChildNameCacheTestCase(usdex.test.TestCase):
    """Assert the expected behavior of the ValidNameCache class"""

    def testGetValidChildNames(self):
        # Define a prim for which we will get valid child names
        stage = Usd.Stage.CreateInMemory()
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)
        prim = usdex.core.defineXform(stage, "/Root").GetPrim()
        self.assertIsValidUsd(stage)

        validChildNameCache = usdex.core.ValidChildNameCache()

        # When there are no child prims the names preferred names are returned
        names = validChildNameCache.getValidChildNames(prim, ["foo", "bar"])
        self.assertEqual(names, ["foo", "bar"])

        # When called a second time the names will have a suffix to make them unique
        # This is true even if the previous names were not used to define children
        names = validChildNameCache.getValidChildNames(prim, ["foo", "bar"])
        self.assertEqual(names, ["foo_1", "bar_1"])

        # If a child is defined after a name cache has been constructed then they are not in the cache and may be returned
        # It is the callers responsibility to decide when to update or clear the cache
        usdex.core.defineXform(stage, "/Root/foo")
        usdex.core.defineXform(stage, "/Root/foo_1")
        usdex.core.defineXform(stage, "/Root/foo_2")
        names = validChildNameCache.getValidChildNames(prim, ["foo", "bar"])
        self.assertEqual(names, ["foo_2", "bar_2"])

        # The cache can be updated to include existing child names without clearing the reserved names
        usdex.core.defineXform(stage, "/Root/foo_3")
        usdex.core.defineXform(stage, "/Root/foo_4")
        validChildNameCache.update(prim)
        names = validChildNameCache.getValidChildNames(prim, ["foo", "bar"])
        self.assertEqual(names, ["foo_5", "bar_3"])

        # The cache can be cleared. This clears all reserved names and the next request for names will initialize with the existing child names
        validChildNameCache.clear(prim)
        names = validChildNameCache.getValidChildNames(prim, ["foo", "bar"])
        self.assertEqual(names, ["foo_5", "bar"])


class DisplayNameTestCase(usdex.test.TestCase):

    def testDisplayName(self):
        # Build a layered stage that allows us to change the edit target
        weakerLayer = self.tmpLayer(name="Weaker")
        strongerLayer = self.tmpLayer(name="Stronger")

        layer = Sdf.Layer.CreateAnonymous()
        layer.subLayerPaths.append(strongerLayer.identifier)
        layer.subLayerPaths.append(weakerLayer.identifier)

        stage = Usd.Stage.Open(layer)
        usdex.core.configureStage(stage, self.defaultPrimName, self.defaultUpAxis, self.defaultLinearUnits, self.defaultAuthoringMetadata)

        # Define the prim in the weaker layer
        stage.SetEditTarget(Usd.EditTarget(weakerLayer))
        prim = stage.DefinePrim("/Root")

        # The newly created prim will have an empty display name and the computed value will match the prim name
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, "")

        result = usdex.core.computeEffectiveDisplayName(prim)
        self.assertEqual(result, prim.GetName())

        # Setting the display name in the weaker layer will produce a success result
        stage.SetEditTarget(Usd.EditTarget(weakerLayer))

        weakerValue = "Weaker Display Name"
        self.assertTrue(usdex.core.setDisplayName(prim, weakerValue))

        # The new value will be reflected in the get and compute functions
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, weakerValue)

        result = usdex.core.computeEffectiveDisplayName(prim)
        self.assertEqual(result, weakerValue)

        # Setting the display name in the stronger layer will produce a success result
        stage.SetEditTarget(Usd.EditTarget(strongerLayer))

        strongerValue = "Stronger Display Name"
        self.assertTrue(usdex.core.setDisplayName(prim, strongerValue))

        # The new value will be reflected in the get and compute functions
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, strongerValue)

        result = usdex.core.computeEffectiveDisplayName(prim)
        self.assertEqual(result, strongerValue)

        # Clearing the display name in the stronger layer will produce a success result
        self.assertTrue(usdex.core.clearDisplayName(prim))

        # The weaker value will now be reflected in the get and compute functions
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, weakerValue)

        result = usdex.core.computeEffectiveDisplayName(prim)
        self.assertEqual(result, weakerValue)

        # Blocking the display name in the stronger layer will produce a success result
        self.assertTrue(usdex.core.blockDisplayName(prim))

        # The prim will now have an empty display name and the computed value will match the prim name
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, "")

        result = usdex.core.computeEffectiveDisplayName(prim)
        self.assertEqual(result, prim.GetName())

        # Setting the bytes string as the display name
        rocket_emoji = "🚀"
        rocket_bytes_string = b"\xF0\x9F\x9A\x80"
        self.assertTrue(usdex.core.setDisplayName(prim, rocket_bytes_string))
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, rocket_emoji)

        # Clear display name and setting rocket emoji character as the display name
        self.assertTrue(usdex.core.clearDisplayName(prim))
        self.assertEqual(weakerValue, usdex.core.getDisplayName(prim))
        self.assertTrue(usdex.core.setDisplayName(prim, rocket_emoji))
        result = usdex.core.getDisplayName(prim)
        self.assertEqual(result, rocket_emoji)

        self.assertIsValidUsd(stage)
