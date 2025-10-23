# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="woosailibrary",
    version="1.1.0",
    author="WoosAI Team",
    author_email="contact@woos-ai.com",
    description="AI Output Token Optimizer - Reduce OpenAI API costs by up to 88%",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/woosai/woosailibrary",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.3.0",
        "tiktoken>=0.5.2",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
        ],
    },
    keywords=[
        "openai",
        "ai",
        "optimization",
        "cost-reduction",
        "token-optimization",
        "gpt",
        "chatgpt",
        "api",
        "caching",
        "statistics",
    ],
    project_urls={
        "Bug Reports": "https://github.com/woosai/woosailibrary/issues",
        "Documentation": "https://github.com/woosai/woosailibrary#readme",
        "Source": "https://github.com/woosai/woosailibrary",
        "Website": "https://woos-ai.com",
    },
)