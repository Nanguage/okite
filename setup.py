from setuptools import setup, find_packages
import re


classifiers = [
    "Development Status :: 3 - Alpha",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
]


keywords = [
    'RPC', 'Network'
]


URL = "https://github.com/Nanguage/okite"


def get_version():
    with open("okite/__init__.py") as f:
        for line in f.readlines():
            m = re.match("__version__ = '([^']+)'", line)
            if m:
                return m.group(1)
        raise IOError("Version information can not found.")


def get_long_description():
    return f"See {URL}"


def get_install_requires():
    requirements = ["cloudpickle", "fire"]
    return requirements


requires_test = ['pytest', 'pytest-cov', 'flake8', 'mypy']


setup(
    name='okite',
    author='Weize Xu',
    author_email='vet.xwz@gmail.com',
    version=get_version(),
    license='MIT',
    description='A Pythonic RPC package.',
    long_description=get_long_description(),
    keywords=keywords,
    url=URL,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=get_install_requires(),
    extras_require={
        'test': requires_test,
    },
    python_requires='>=3.7, <4',
)
