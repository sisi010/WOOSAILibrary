from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="woosailibrary",
    version="1.0.0",
    author="WoosAI Team",
    author_email="support@woosai.com",
    description="AI cost optimization library - Save up to 61% on OpenAI API costs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/woosai/woosailibrary",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.3.0",
        "tiktoken>=0.5.2",
        "python-dotenv>=1.0.0",
    ],
    keywords="ai, openai, cost-optimization, gpt, chatgpt, api, token, savings",
)
