import os
from setuptools import setup, find_packages

# Read the long description from README (optional, but nice for PyPI)
this_directory = os.path.abspath(os.path.dirname(__file__))
long_description = ""
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    pass

setup(
    name="skainnotate",                  # Package name
    version="0.1.0",                     # Version number
    description="SKAInnotate: An annotation tool by InstaDeep.",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    author="InstaDeep",
    author_email="info@instadeep.com",
    url="https://github.com/instadeepai/SKAInnotate",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.111.0",
        "google-api-core>=2.19.0",
        "google-api-python-client>=2.134.0",
        "google-auth>=2.30.0",
        "google-cloud-core>=2.4.1",
        "google-cloud-storage>=2.17.0",
        "gunicorn>=22.0.0",
        "itsdangerous>=2.2.0",
        "SQLAlchemy>=2.0.30",
        "typer>=0.12.3",
        "uvicorn>=0.30.1",
        ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "skainnotate=deployment_setup.backend.app.main:run_app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
