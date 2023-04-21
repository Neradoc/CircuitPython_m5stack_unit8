Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-m5stack-unit8/badge/?version=latest
    :target: https://circuitpython-m5stack-unit8.readthedocs.io/
    :alt: Documentation Status



.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/Neradoc/CircuitPython_m5stack_unit8/workflows/Build%20CI/badge.svg
    :target: https://github.com/Neradoc/CircuitPython_m5stack_unit8/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Library for M5Stack's Unit8 Encoder and Unit8 Angle breakouts.

NOTE: for Circuitpython use in particular, there are no pull-up resistors on those boards, you will need to add them in the circuit.

.. image:: images/m5stack_unit8.jpg
    :alt: Picture of M5Stack Unit8 Angle and Encoder

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install m5stack_unit8

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-m5stack-unit8.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/Neradoc/CircuitPython_m5stack_unit8/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
