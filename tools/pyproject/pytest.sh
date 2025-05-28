#!/bin/bash

set -e

# Setup the build environment
VENV=./_build/tests/venv
echo "Building: $VENV"
if [ -d $VENV ]; then
    rm -rf $VENV
fi
./_build/target-deps/python/python3 -m venv "$VENV"
source "$VENV/bin/activate"
python -m pip install _build/packages/*.whl

# copy the test dependencies into the env
TEST_ROOT=$1
echo "Copy test deps from: ${TEST_ROOT}"
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[-1])")
echo "Copy test deps to: ${SITE_PACKAGES}"
cp -r ${TEST_ROOT}/python/usdex/test ${SITE_PACKAGES}/usdex/test
mkdir ${SITE_PACKAGES}/omni
cp -r ${TEST_ROOT}/python/omni/asset_validator ${SITE_PACKAGES}/omni/asset_validator
cp -r ${TEST_ROOT}/python/omni/capabilities ${SITE_PACKAGES}/omni/capabilities

# Run the tests
python -m unittest discover -v -s source/core/tests/unittest
