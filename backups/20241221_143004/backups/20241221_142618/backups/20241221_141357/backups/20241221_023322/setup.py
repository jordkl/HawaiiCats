from setuptools import setup, find_packages

setup(
    name="cat_simulation",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        'Flask>=2.3.3',
        'h3>=3.7.6',
        'numpy>=1.24.3',
        'pandas>=2.0.3',
    ],
)
