from setuptools import find_packages, setup


setup(
    name='omniscient',
    version='0.0.1',
    author='Peng Shi, Michael Azmy',
    description='Knowledge Graph Toolkits',
    url='https://github.com/Impavidity/Omniscient',
    license='MIT',
    install_requires=['spacy','pyjnius'],
    packages=find_packages(),
)
