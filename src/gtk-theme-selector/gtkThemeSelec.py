#!/usr/bin/env python
# -*- coding: utf-8 -*-

#A GTK theme selector written in Python for the Neo Freerunner phone
#Copyright (C) 2009-2011  Alejandro Blanco Escudero

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import pygtk
pygtk.require('2.0')
import os

class ThemeSelector:
    # GTK configuration file
    __gtkrc = "/etc/gtk-2.0/gtkrc"
    # GTK themes folder
    __themes = "/usr/share/themes/"
    __h = 50

    def __init__(self):
        # Main window
        self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.__window.connect("destroy", self.destroy)
        self.__window.set_title("GTK Theme Selector")
        self.__window.set_border_width(0)
        # Neo FreeRunner's screen resolution
        self.__window.set_size_request(480, 640)

        # Main packing vertical box
        mainvbox = gtk.VBox(False, 3)
        self.__window.add(mainvbox)

        # Combobox and button for choosing the theme to apply
        combohbox = gtk.HBox(False, 3)
        self.__combo = gtk.combo_box_new_text()
        self.__combo.set_size_request(-1, self.__h)
        buttonA = gtk.Button("Apply")
        buttonA.set_size_request(100, self.__h)
        buttonA.connect("clicked", self.__apply)
        combohbox.pack_start(self.__combo, True, True, 0)
        combohbox.pack_start(buttonA, False, False, 0)
        self.__combo.show()
        buttonA.show()
        combohbox.show()
        mainvbox.pack_start(combohbox, False, False, 0)

        # Log scrolled text area
        textarea = gtk.TextView()
        textarea.set_editable(False)
        self.__log = textarea.get_buffer()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(3)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(textarea)
        mainvbox.pack_start(scrolled_window, True, True, 0)
        textarea.show()
        scrolled_window.show()

        # Load initial information
        self.__showCurrent()
        self.__loadThemes()

        mainvbox.show()
        self.__window.show()

    def __loadThemes(self):
        # List the themes present
        tlist = os.listdir(self.__themes)
        # If there aren't themes
        if len(tlist) <= 0:
            iter = self.__log.get_end_iter()
            self.__log.insert(iter, "Error: There aren't themes to load\nat " +
                                self.__themes + "\n\n")
        else:
            tlist.sort()
            # Show the themes at the combobox
            for t in tlist:
                self.__combo.append_text(t)
            self.__combo.set_active(0)

    def __showCurrent(self):
        # Read current theme
        fich = open(self.__gtkrc, "r")
        data = fich.readlines()
        fich.close()
        ready = False
        # Search for the theme name
        for line in data:
            if line.startswith("gtk-theme-name"):
                s = line.split("\"")
                if len(s) <= 1:
                    s = line.split("'")
                if len(s) > 1:
                    ready = True
        # Show the result at the log area
        iter = self.__log.get_end_iter()
        if ready:
            self.__log.insert(iter, "You are using now this theme: \n" + s[1] + "\n\n")
        else:
            self.__log.insert(iter, "There is a problem with your\n" +
                                    self.__gtkrc + ", you will\n" +
                                    "have to manually edit it\n\n")

    def __apply(self, widget):
        # If there isn't a theme chosen, abort
        if self.__combo.get_active_text() == None:
            return 0
        # Load previous content of the gtkrc file
        fich = open(self.__gtkrc, "r")
        data = fich.readlines()
        fich.close()
        i = 0
        done = False
        # Search the line to modify
        for line in data:
            if line.startswith("gtk-theme-name"):
                data[i] = "gtk-theme-name = '" + self.__combo.get_active_text() + "'\n"
                done = True
            i = i + 1
        # Write the (modified) content to the file
        fich = open(self.__gtkrc, "w")
        fich.writelines(data)
        fich.close()
        # Update the log
        iter = self.__log.get_end_iter()
        if done:
            self.__log.insert(iter, "Theme applied succesfully, please restart\n" +
                                    "your GTK applications\n\n")
            self.__showCurrent()
        else:
            self.__log.insert(iter, "An error happend, you will have to\n" +
                                    "manually edit " + self.__gtkrc + "\n\n")

    def main(self):
        gtk.main()
        return 0

    def destroy(self, widget):
        gtk.main_quit()

# Python's ugliness :P
if __name__ == "__main__":
    ts = ThemeSelector()
    ts.main()
