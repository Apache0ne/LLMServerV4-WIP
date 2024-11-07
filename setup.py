from setuptools import setup, find_packages

setup(
    name="llmserver",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "prompt-toolkit",
        "pyyaml",
        "groq",
        "ollama",
        "cerebras-cloud-sdk",
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "llmserver=main:main",
        ],
    },
)