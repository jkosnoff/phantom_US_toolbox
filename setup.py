import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='phantom_US_toolbox',
    version='0.0.10',
    author='Joshua Kosnoff',
    author_email='jkosnoff@andrew.cmu.edu',
    description='This is a toolbox for analyzing phantom tFUS experiments',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jkosnoff/phantom_US_toolbox",
    packages=['phantom_US_toolbox'],
    install_requires=['nptdms', "pandas", "numpy", "matplotlib",
                      "sklearn", "seaborn", "tk"]
)
