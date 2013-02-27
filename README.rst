fabix
=====

Fabix is a serie of functions built on top of fabric and cuisine to easily
deploy python web projects. It includes tasks to manage a Django installation,
compile python, install libs, etc.

Supported OSs
-------------

Currently, only Ubuntu is supported but patches supporting other OS/distros are
welcome :).

Requirements
------------

 * Fabric_ 1.4.2
 * cuisine_ 0.2.6
 * Boto_ 2.7.0

Roadmap
-------

- Support framework installations (Django, Tornado, CherryPy, etc.)
- Add support for RPM-based distros

Contributing
------------

Just do the usual thing: fork & send a pull request. Please, respect the coding
style around you and try to respect `PEP 8`_ guidelines.

License
-------

This project is licensed under MIT license. For details, please see file MIT-LICENSE.


.. _Fabric: http://docs.fabfile.org/en/1.4.2/index.html
.. _Boto: https://github.com/boto/boto
.. _cuisine: https://github.com/sebastien/cuisine
.. _`PEP 8`: http://www.python.org/dev/peps/pep-0008/
