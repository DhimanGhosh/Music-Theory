from setuptools import setup, find_packages

setup(
    name='Music_Theory_Guide',
    version='3.0',
    long_description=open('README.md').read(),
    author='Dhiman Ghosh',
    url='https://github.com/DhimanGhosh/Music-Theory-Guide',
    author_email='dgkiitcsedual@gmail.com',
    description='Music Theory Guide',
    packages=find_packages(exclude='docs'),
    install_requires=open('requirements.txt').read()
)