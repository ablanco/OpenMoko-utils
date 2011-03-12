==============
OpenMoko-utils
==============

OpenMoko-utils is a collection of applications that I developed with the
Neo Freerunner phone in mind, actually for the SHR stack.

There are three apps right now:

    * Checklist Manager
    * Alsa Mixer
    * GTK Theme Selector

The three of them are written in Python.

OpenMoko Platform
=================

    * OpenMoko:
        http://wiki.openmoko.org
    * SHR project:
        http://shr-project.org
    * OPKG.org:
        http://www.opkg.org

============
Applications
============

Checklist Manager
=================

A very simple checklists manager. It's written on python using GTK.
It manages several checklists, which are stored in plain text files.

By default the store folder is::

    $HOME/.pyChecklist/checklists/

But it can be defined by the user creating this file::

    $HOME/.pyChecklist/storePath.conf

and writing in the first line the wanted path.

Opkg.org entry: http://www.opkg.org/package_251.html

Alsa Mixer
==========

It's a very simple Alsa mixer. The user can choose which Alsa
channels want to be shown, and modify their volume.
It uses the **python-pyalsaaudio** package.

If the */usr/share/shr/scenarii/gsmhandset.state* file is present,
it will show an extra slider for changing the phone calls volume.

Opkg.org entry: http://www.opkg.org/package_288.html

GTK Theme Selector
==================

It shows on a combobox the themes present at */usr/share/themes/*,
and modify the */etc/gtk-2.0/gtkrc* file changing the theme for the
one the user chose.

Opkg.org entry: http://www.opkg.org/package_272.html

