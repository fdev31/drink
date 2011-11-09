.. Drink! documentation master file, created by
   sphinx-quickstart on Sat Apr  9 21:39:32 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Drink!'s documentation
=================================

.. note:: alpha software !

Drink looks like a lightweight & easy to install Web CMS. Under the ground this is only a simple test application for an in-progress rapid web framework for applications that have standard requirements.

Short description
*****************

With drink, without coding power, you get a simple to use & install CMS, a with nice javascript interface.

With python & javascript skill, you get a very simple API to develop your own website, with no SQL requirements and "builtin" objects storage, automatic but overridable edition & rendering of objects, etc... it comes with a bunch of useful classes you can hack and fork.

Technical description
*********************

100% written in python, WSGI compliant, exposing an object database (think about a tree of dict-derived classes).

On top of that, you have simple generic templates you can override if you prefer (instead of writing python).
Then, you profite from an important layer of javascript, using some of the client power to reduce bandwith usage. Json and plain-text are used for communication.


Site index
**********

.. toctree::
   :maxdepth: 2

   developpers
   api

Contact
*******

Email
-----

Use my email for bug-reporting, urgent requests, support, or anything.
My contact is fdev31 <AT> gmail <DOT> com.

Bug reporting
-------------

Use Bitbucket's `Bugtracker`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Bugtracker: https://github.com/fdev31/drink/issues

