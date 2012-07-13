from setuptools import setup, find_packages
from fabix import __version__

setup(
    name='fabix',
    version=__version__,
    description="Fabix is a serie of functions built on top of fabric and cuisine to easily deploy python web projects.",
    long_description=open('README.md', 'rb').read(),
    keywords=['fabric', 'cuisine', 'fabix'],
    author='Rodrigo Machado',
    author_email='rcmachado@gmail.com',
    url='http://github.com/quatix/fabix',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
    ],
    packages=find_packages(),
    install_requires=open("requirements.txt").read().split("\n"),
    package_dir={"fabix": "fabix"}
)
