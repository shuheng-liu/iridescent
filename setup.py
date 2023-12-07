from setuptools import setup, find_packages

with open("README.md") as f:
    long_desc = f.read()

with open("requirements.txt") as f:
    install_requires = [
        line.strip()
        for line in f.read().split('\n')
        if line.strip() != '' and not line.startswith("#")
    ]

setup(
    name="iridescent",
    version="0.1.0",
    author="Shuheng Liu",
    author_email="shuheng.liu@intersystems.com",
    description="A better terminal for InterSystems IRIS, with vim-modes and history search",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://bitbucketlb.iscinternal.com/users/shuliu/repos/iridescent/browse",
    # download_url="https://bitbucketlb.iscinternal.com/users/shuliu/repos/iridescent/archive/master.zip",
    keywords=["InterSystems IRIS", "Shell", "Terminal", "Vim"],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=install_requires,
    # license="MIT",
    entry_points={
        "console_scripts": [
            "iridescent = iridescent.iridescent:main",
        ]
    }
)
