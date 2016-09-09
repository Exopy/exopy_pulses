.. _context

.. include:: ../substitutions.sub

Context and pulse sequence compilation
======================================

# XXX

.. contents::

Compilation process
-------------------



Creating a new context
----------------------

Creating a new shape is a three step process :

- first the shape itself which holds the logic must be created.
- to allow a user to correctly parametrize the shape a dedicated widget or view
  should also be created.
- finally the shape must be declared in the manifest of the plugin contributing
  it.


Implementing the logic
^^^^^^^^^^^^^^^^^^^^^^
