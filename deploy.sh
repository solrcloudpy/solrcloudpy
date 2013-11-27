#!/bin/sh

set -e

# Deploy the module to PyPI
echo "Deploying solrcloudpy to PyPI."
python setup.py sdist upload
