import re

from setuptools import find_packages, setup

with open("README.rst", "r") as f:
    long_description = f.read()


def get_version():
    return re.search(
        r"""__version__\s+=\s+(?P<quote>['"])(?P<version>.+?)(?P=quote)""",
        open("solrcloudpy/__init__.py").read(),
    ).group("version")


setup(
    name="solrcloudpy",
    version=get_version(),
    author="Didier Deshommes, Robert Elwell",
    author_email="dfdeshom@gmail.com, robert.elwell@gmail.com",
    packages=find_packages(exclude=["ez_setup"]),
    url="https://github.com/solrcloudpy/solrcloudpy",
    license="LICENSE.txt",
    keywords="solr solrcloud",
    description="python library for interacting with SolrCloud ",
    long_description=long_description,
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    install_requires=["requests >= 2.11.1", "semver", "pathlib2", "future"],
)
