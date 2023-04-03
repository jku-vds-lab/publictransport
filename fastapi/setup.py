from setuptools import setup

setup(
    name='publictransport',
    packages=['publictransport'],
    include_package_data=True,
    install_requires=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'geojson',
        'shapely',
        'pandas',
    ],
)