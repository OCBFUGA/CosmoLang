from setuptools import setup, find_packages

setup(
    name="cosmocore-lang",
    version="25.1.0",
    author="Janio Gomes Ribeiro",
    author_email="janio@example.com",
    description="CosmoCore AGI Swarm Language & Compiler (V25)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
    ],
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "cosmo=cosmolang.cli:main",
        ],
    },
)
