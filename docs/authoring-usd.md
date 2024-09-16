# Authoring USD Data

The OpenUSD Exchange SDK helps developers implement their own USD I/O solutions that produce consistent and correct USD assets across diverse 3D ecosystems.

It provides higher-level convenience functions on top of lower-level USD concepts, so developers can quickly adopt OpenUSD best practices when mapping their native data sources to OpenUSD-legible data models.

The goal is not to abstract the USD authoring process, but instead to simplify it, by providing convenience functions that cover common use cases and avoid common stumbling blocks.

Each of the subsections below describes a common challenge with OpenUSD and links to the relevant functions and classes in OpenUSD Exchange that aim simplify these problems.

## Layers and Stages

Whenever you are authoring OpenUSD data, ultimately, your data will need to be stored in a [SdfLayer](https://openusd.org/release/api/class_sdf_layer.html), whether it is in-memory, in a local or shared filesystem, or in cloud storage.

While you can author data directly via OpenUSD's [Sdf library](https://openusd.org/release/api/sdf_page_front.html), it is often more intuitive and convenient to author the layer via a [UsdStage](https://openusd.org/release/api/class_usd_stage.html) instead, so you can make use of higher level [schemas](https://openusd.org/release/api/class_usd_schema_base.html#details).

In either approach, your Layers should contain particular metadata to ensure they will load correctly across diverse 3D ecosystems. It is very common to forget (or misconfigure) this metadata. We provide [SdfLayer authoring](../api/group__layers.rebreather_rst) and [UsdStage Configuration](../api/group__stage__metadata.rebreather_rst) functions to assist & prevent common mistakes.

When authoring [UsdPrims](https://openusd.org/release/api/class_usd_prim.html) to a Stage, you will need to specify an [SdfPath](https://openusd.org/release/api/class_sdf_path.html) that identifies a unique location for the Prim. The nature of OpenUSD's [composition algorithm](https://openusd.org/release/glossary.html#composition) (know as "LIVRPS") makes it fairly complex to determine whether your chosen location is valid for authoring. We provide [UsdStage Prim Hierarchy](../api/group__stage__hierarchy.rebreather_rst) functions to assist.

## Valid and Unique Names

OpenUsd has strict requirements on what names are valid for a `UsdObject`, which includes both `UsdPrim` and `UsdProperty` objects.

An [identifier is valid](https://openusd.org/release/api/group__group__tf___string.html#gaa129b294af3f68d01477d430b70d40c8) if it follows
the C/Python identifier convention; that is, it must be at least one character long, must start with a letter or underscore, and must contain
only letters, underscores, and numerals.

Additionally the names of sibling Objects must be unique so that the `SdfPath` that identifies them is unique within the `UsdStage`.

### Ascii and UTF-8 Support

In some current OpenUSD runtimes, valid characters within identifiers are restricted to the minimal ascii characters `[A-Za-z0-9_]`. The name of a `UsdProperty` can contain `:` delimiters for namespaces, however the values within each namespace must be a valid identifier.

```{eval-rst}
.. note::
  In OpenUSD v24.03 and beyond, XID identifiers are natively supported, but some reserved characters remain illegal (e.g. `/`, `@`).
```

For many data sources, native items will not conform to these requirements and the names will need to be made valid in order to be used in USD.

The [Prim and Property Names](../api/group__names.rebreather_rst) functions can be used to produce valid `UsdObject` names for any OpenUSD runtime
that we support.

## Defining Prims

OpenUsd provides Schema classes for authoring typed Prims, however in order to author a complete and correct Prim it is often necessary to call
multiple functions. It is common for some of these functions to be over looked, or have mismatched data supplied.

The OpenUSD Exchange SDK provides "define" functions to address this problem. The "define" functions are the primary entry point for authoring 3D data to USD.

The role of a "define" function is to:
- Ensure that a complete Prim definition is authored via a single function call
- Perform validation on the supplied data _before authoring the Prim_.
  - If any of the supplied data is invalid, then the Prim will not be authored. This up front validation avoids partial authoring of Prims.
- Ensure all opinions that contribute to the Prim's definition will be explicitly authored in a single Layer.

To learn about each of the "define" functions in more detail, see the specific documentation:
- [Xforms](../api/group__xform.rebreather_rst) (specific placement prims)
- [Polygon Meshes](../api/group__mesh.rebreather_rst)
- [Point Clouds / Particles](../api/group__points.rebreather_rst)
- [Lines and Curves](../api/group__curves.rebreather_rst)
- [Cameras](../api/group__cameras.rebreather_rst)
- [Lights](../api/group__lights.rebreather_rst)
- [Preview Materials and Shaders](../api/group__materials.rebreather_rst)
- [RTX Materials and Shaders](../api/group__rtx__materials.rebreather_rst) (optionally included via `usdex_rtx`)

### Defining Primvars

All [UsdGeomPointBased](https://openusd.org/release/api/class_usd_geom_point_based.html) prims can optionally have geometric surface varying variables called [UsdGeomPrimvars](https://openusd.org/release/api/class_usd_geom_primvar.html) (primitive variables or simply "primvars") which interpolate across a primitive's topology, and can override shader inputs. In addition, any `UsdPrim` can have constant primvars, which are inherited down prim hierarchy to provide a convenient set-once-affect-many workflow within a hierarchy.

`UsdGeomPrimvars` are often used when authoring `UsdGeomPointBased` prims (e.g meshes, curves, and point clouds) to describe surface varying
properties such as normals, widths, displayColor, and displayOpacity. They can also be used to describe completely bespoke user properties that can affect how a prim is rendered, or to drive a surface deformation.

However, `UsdGeomPrimvar` data can be quite intricate to use, especially with respect to indexed vs non-indexed primvars, element size, the
complexities of `VtArray` detach (copy-on-write) semantics, and the ambiguity of "native" attributes vs primvar attributes (e.g. mesh normals).

We provide a templated [`PrimvarData` class](../api/group__primvars.rebreather_rst) to encapsulate all this data as a single object without risk of detaching (copying) arrays, and to provide simpler entry points to avoid common mistakes with respect to `UsdGeomPrimvar` data handling.

All of our USD authoring "define" functions for `UsdGeomPointBased` prims accept optional `PrimvarData` to define e.g normals, display colors, etc.

The `PrimvarData` class also supports reading from (and authoring to) any existing `UsdGeomPrimvar`, which may have been created via OpenUSD's [UsdGeomPrimvarsAPI](https://openusd.org/release/api/class_usd_geom_primvars_a_p_i.html).

## Working with 3D Transformation

The [UsdGeomXformable](https://openusd.org/release/api/usd_geom_page_front.html#UsdGeom_Xformable) schema supports a rich set of transform operations
from which a resulting matrix can be computed.

The flexibility of this system adds complexity to the code required for authoring and retrieving transform information. The `usdex_core` library provides the [3D Transformation](../api/group__xformable.rebreather_rst) functions to help with this.

## Diagnostic Logs

OpenUSD's [Tf library](https://openusd.org/release/api/tf_page_front.html) provides various [diagnostic logging facilities](https://openusd.org/release/api/page_tf__diagnostic.html) which are useful for communicating errors, warnings, and status information to end users or system logs.

However, the default diagnostic output is somewhat engineer-centric. Fortunately, it provides the ability to override the default message handler, with one or more custom diagnostic delegates.

We provide one such [diagnostic delegate](../api/group__diagnostics.rebreather_rst) with some more controllable options (like level filtering), which you are welcome to use directly, or to use as inspiration for your own diagnostic delegate implementation.

Debug logs are emitted via OpenUSD's `TfDebug` mechanism, which is separate from the other diagnostics. See our [Debugging guide](./getting-started.md#debugging) for more information.

## Runtime Settings

Some OpenUSD Exchange behaviors (such as name transcoding) are controllable via global static [runtime settings](../api/group__settings.rebreather_rst), using OpenUSD’s `TfEnvSetting` mechanism, which relies on setting Environment Variables before the USD libraries are loaded into an application.
