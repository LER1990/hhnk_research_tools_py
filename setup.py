from setuptools import setup, find_packages

setup(
    name='hhnk_threedi_tools',
    version='0.1.4',    
    description='HHNK tools for working with 3di',
    url='https://github.com/LER1990/hhnk_threedi_tools',
    author='Laure Ravier',
    author_email='L.Ravier@hhnk.nl',
    project_urls={
        "Bug Tracker": "https://github.com/LER1990/hhnk_threedi_tools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
	install_requires=[
   	'numpy>=1.19.1',
	'Shapely>=1.7.0',
	'gdal>=3.1.4',
    'pandas>=1.0.1',
    'geopandas>=0.7.0',
    'threedigrid>=1.0.25'
	]
)
