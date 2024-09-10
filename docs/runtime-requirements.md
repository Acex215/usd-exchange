# Runtime Requirements

When building an application, plugin, or container that uses OpenUSD Exchange libraries and modules, there are a few considerations:

- The shared libraries can be placed anywhere, so long as they can be dynamically loaded at runtime using standard procedures on your operating system (e.g on the `PATH` or `LD_LIBRARY_PATH` environment variables).
- The OpenUSD Plugins (i.e. `plugInfo.json` files) **must** be placed relative to the OpenUSD shared libraries.
- If you are using python, the `pxr` and `usdex` python modules can be placed anywhere, so long as they are configured appropriately for `sys.path` at runtime.

## Example runtime file layouts

For clarity, below are some suggested file layouts for our both default and "minimal" builds on Linux and Windows.

```{eval-rst}
.. note::
  As suggested above, if you need to use alternate paths for some or all of the normal shared libraries or python modules, that is fine. These are just default suggestions, which match the `install_usdex` defaults.
```

```{eval-rst}
.. include::
  runtime-tree.rst
```
