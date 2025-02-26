from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flet-staticserver",
    version="0.1.0",
    author="Julián Perez",
    author_email="mordecaaii@gmail.com",
    description="A simple static file server for Flet apps, perfect for mobile debugging.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/flet-staticserver",  # URL del repositorio
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "flet",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)