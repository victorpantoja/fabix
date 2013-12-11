import locale
import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)
readme_file = os.path.join(base_dir, 'README.rst')
requirements_file = os.path.join(base_dir, 'requirements.txt')

encoding = locale.getdefaultlocale()[1]

setup(
    name='fabix',
    version='0.0.5',
    description="Fabix is a serie of functions built on top of fabric and cuisine to easily deploy python web projects.",
    long_description=open(readme_file, 'rb').read().decode(encoding),
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
    install_requires=open(requirements_file, "rb").read().decode(encoding).split("\n"),
    package_dir={"fabix": "fabix"},
    package_data={'fabix': ["support_files/etc/init/*.conf"]}
)
