from setuptools import setup, find_packages
from fabix import __version__

setup(
    name='fabix',
    version=__version__,
    description="Fabix is a serie of functions built on top of fabric and cuisine to easily deploy python web projects.",
    long_description=open('README.md', 'rb').read(),
    keywords=['fabric', 'cuisine'],
    author='Rodrigo Machado',
    author_email='rcmachado@gmail.com',
    url='http://github.com/quatix/fabix',
    license='MIT',
    classifiers=['Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'License :: OSI Approved',
                'Natural Language :: English',
                'Operating System :: POSIX :: Linux',
                'Programming Language :: Python :: 2.7',
                'Topic :: Software Development :: Libraries :: Application Frameworks',
                ],
    packages=find_packages(),
    package_dir={"fabix": "fabix"},
    install_requires = open("requirements.txt").read().split("\n"),
    include_package_data=True,
)