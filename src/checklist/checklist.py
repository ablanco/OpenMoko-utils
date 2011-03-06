#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Checklist manager written in Python for the Neo Freerunner phone
#Copyright (C) 2009-2011 Alejandro Blanco Escudero

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

class Checklist:
    __configPath = os.environ['HOME'] + "/.pyChecklist/"
    __storePath = __configPath + "checklists/"
    __h = 32
    __last_active_text = None

    def __init__(self):
        # Read the store path from the config file, it may have been redefined
        # by the user
        if os.access(self.__configPath + "storePath.conf", os.F_OK):
            fich = open(self.__configPath + "storePath.conf", "r")
            data = fich.readlines()
            fich.close()
            sp = None
            if len(data) > 0:
                sp = data[0]
            if sp:
                if sp.endswith("\n"):
                    sp = sp.replace("\n", "")
                if not(sp.endswith("/")):
                    sp += "/"
                self.__storePath = sp
        # Check if store path exists, if not it will create it
        if not(os.access(self.__storePath, os.F_OK)):
            os.makedirs(self.__storePath)

        # Main window
        self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.__window.connect("destroy", self.destroy)
        self.__window.set_title("Checklist")
        self.__window.set_border_width(0)
        # Neo FreeRunner's screen resolution
        self.__window.set_size_request(480, 640)
        # Main box containing everything
        mainvbox = gtk.VBox(False, 3)
        self.__window.add(mainvbox)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(0)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vs_scrollbar = scrolled_window.get_vscrollbar()
        # I'll need the adjustment later to change which part of the checklist
        # is being showed after adding a new element
        self.__scroll_adj = scrolled_window.get_vadjustment()

        # Vertical box with the elements of the checklist
        self.__ppalvbox = gtk.VBox(False, 3)

        # Combobox for choosing the checklist
        combohbox = gtk.HBox(False, 3)
        self.__combo = gtk.combo_box_new_text()
        # Load the contents of the store path, here are the avaible checklists
        self.__loadCLists()
        self.__last_active_text = self.__combo.get_active_text()
        self.__combo.connect("changed", self.__callback_switch)
        self.__combo.set_size_request(-1, self.__h)
        # Create and delete checklist buttons
        buttonN = gtk.Button("New")
        buttonN.connect("clicked", self.__callback_dialog, True)
        buttonN.set_size_request(100, self.__h)
        buttonD = gtk.Button("Delete")
        buttonD.connect("clicked", self.__callback_dialog)
        buttonD.set_size_request(100, self.__h)
        combohbox.pack_start(self.__combo, True, True, 0)
        combohbox.pack_start(buttonN, False, False, 0)
        combohbox.pack_start(buttonD, False, False, 0)
        buttonN.show()
        buttonD.show()
        self.__combo.show()

        mainvbox.pack_start(combohbox, False, False, 0)
        scrolled_window.add_with_viewport(self.__ppalvbox)
        mainvbox.pack_start(scrolled_window, True, True, 0)

        # Load the checklist data
        self.__load()

        # Adding new elements and exit buttons
        hbox = gtk.HBox(True, 3)
        buttonA = gtk.Button("Add")
        buttonA.connect("clicked", self.__add)
        buttonA.set_size_request(-1, self.__h)
        buttonR = gtk.Button("Restore")
        buttonR.connect("clicked", self.__callback_restore)
        buttonR.set_size_request(-1, self.__h)
        buttonC = gtk.Button("Close")
        buttonC.connect("clicked", self.destroy)
        buttonC.set_size_request(-1, self.__h)
        hbox.add(buttonA)
        hbox.add(buttonR)
        hbox.add(buttonC)
        buttonA.show()
        buttonR.show()
        buttonC.show()

        mainvbox.pack_start(hbox, False, False, 0)

        combohbox.show()
        self.__ppalvbox.show()
        scrolled_window.show()
        hbox.show()
        mainvbox.show()

        self.__window.show()

    def __add(self, widget=None, text="", number=0):
        w = 40;
        hbox = gtk.HBox(False, 0)
        # Name of the element
        entry = gtk.Entry(100)
        adjustment = gtk.Adjustment(0, 0, 100000, 1, 10, 0)
        # Number of items of that element
        spinner = gtk.SpinButton(adjustment, 1, 0)
        spinner.set_size_request(70, -1)
        # Buttons
        butclos = gtk.Button("X")
        butclos.connect("clicked", self.__callback_destroy, hbox)
        butclos.set_size_request(w, self.__h)
        butplus = gtk.Button("+")
        butplus.connect("clicked", self.__callback_modifyValue, spinner, 1)
        butplus.set_size_request(w, self.__h)
        butminus = gtk.Button("-")
        butminus.connect("clicked", self.__callback_modifyValue, spinner, -1)
        butminus.set_size_request(w, self.__h)
        # Empty label as a spacer between the element and the scrollbar
        # It makes harder push a button for accident
        #invisible = gtk.Label()
        #invisible.set_size_request(15, self.__h)
        hbox.pack_start(butclos, False, False, 0)
        hbox.pack_start(entry, True, True, 0)
        hbox.pack_start(spinner, False, False, 0)
        hbox.pack_start(butplus, False, False, 0)
        hbox.pack_start(butminus, False, False, 0)
        #hbox.pack_start(invisible, False, False, 0)
        # Set the values of the element
        entry.set_text(text)
        spinner.set_value(number)
        # Show everything
        entry.show()
        spinner.show()
        butclos.show()
        butplus.show()
        butminus.show()
        #invisible.show()
        hbox.show()
        self.__ppalvbox.pack_start(hbox, False, False, 0)
        self.__scroll_adj.set_value(self.__scroll_adj.get_value() + 1000)
        #self.__scroll_adj.set_value(self.__scroll_adj.get_upper())

    # Destroy an element
    def __callback_destroy(self, widget, hbox):
        hbox.destroy()

    def __callback_modifyValue(self, widget, spinner, value):
        spinner.set_value(spinner.get_value_as_int() + value)

    # Shows the dialog, for both creating and deleting a checklist
    def __callback_dialog(self, widget, new=False):
        buttonA = gtk.Button("Accept")
        buttonC = gtk.Button("Cancel")
        # If it's the creating dialog
        if new:
            dialog_entry = gtk.Entry()
            label = gtk.Label("Name")
            dialog = gtk.Dialog("New checklist", self.__window, gtk.DIALOG_MODAL, None)
        # Deleting dialog
        else:
            label = gtk.Label("Are you sure you want to delete the active checklist?")
            label.set_line_wrap(True)
            label.set_justify(gtk.JUSTIFY_FILL)
            label.set_size_request(470, 50)
            dialog = gtk.Dialog("Delete confirmation", self.__window, gtk.DIALOG_MODAL, None)
        dialog.set_has_separator(False)
        dialog.set_size_request(480, 100)
        # Packing content into the dialog
        dialog.vbox.pack_start(label, False, False, 0)
        if new:
            dialog.vbox.pack_start(dialog_entry, False, False, 0)
        # Buttons: accept and cancel
        hbox = gtk.HBox(False, 3)
        hbox.pack_start(buttonA, False, False, 0)
        hbox.pack_start(buttonC, False, False, 0)
        dialog.vbox.pack_start(hbox, False, False, 0)
        # Different callback method in each case
        if new:
            buttonA.connect("clicked", self.__callback_create, dialog, dialog_entry)
            dialog_entry.show()
        else:
            buttonA.connect("clicked", self.__callback_delete, dialog)
        buttonC.connect("clicked", self.__callback_dialog_destroy, dialog)
        label.show()
        buttonA.show()
        buttonC.show()
        hbox.show()
        dialog.show()

    def __callback_dialog_destroy(self, widget, dialog):
        dialog.destroy()

    def __callback_create(self, widget, dialog, entry):
        if dialog:
            dialog.destroy()
        if entry.get_text() != "":
            # Creating the file of the new checklist
            fich = open(self.__storePath + entry.get_text(), "w")
            fich.write("")
            fich.close()
            # Adding the new checklist to the combo box
            self.__combo.insert_text(0, entry.get_text())
            self.__combo.set_active(0)
            self.__callback_switch(None)

    def __callback_delete(self, widget, dialog):
        # Selected checklist
        fname = self.__combo.get_active_text()
        # Deleting the file
        os.remove(self.__storePath + fname)
        self.__last_active_text = None
        # Removing the checklist from the combo box
        self.__combo.remove_text(self.__combo.get_active())
        # If it was the last checklist present
        clists = os.listdir(self.__storePath)
        if len(clists) <= 0:
            entry = gtk.Entry()
            entry.set_text("default")
            # This call will destroy the dialog for us
            self.__callback_create(None, dialog, entry)
        else:
            # If it was not
            dialog.destroy()
            self.__combo.set_active(0)
            self.__callback_switch(None)

    def __callback_switch(self, widget):
        self.__save()
        # Updating the reference to the last selected checklist
        self.__last_active_text = self.__combo.get_active_text()
        self.__clean()
        self.__load()

    def __callback_restore(self, widget):
        self.__clean();
        self.__load();

    def __save(self):
        if self.__last_active_text == None:
            return 0
        fich = open(self.__storePath + self.__last_active_text, "w")
        # For every element
        for h in self.__ppalvbox.get_children():
            children = h.get_children()
            entry = children[1]
            spinner = children[2]
            # Write the data into the file
            fich.write(entry.get_text())
            fich.write("\t")
            fich.write(str(spinner.get_value_as_int()))
            fich.write("\n")
        fich.close()

    def __load(self):
        if self.__combo.get_active_text() == None:
            return 0
        fich = open(self.__storePath + self.__combo.get_active_text(), "r")
        data = fich.readlines()
        data.sort()
        # For every line of the file
        for d in data:
            arr = d.split("\t")
            self.__add(None, arr[0], int(arr[1]))
        fich.close()

    def __loadCLists(self):
        clists = os.listdir(self.__storePath)

        # Check if the store path is empty
        if len(clists) <= 0:
            entry = gtk.Entry()
            entry.set_text("default")
            self.__callback_create(None, None, entry)
        else:
            clists.sort()
            # The lines of the store folder are the names of the checklists,
            # which are the options that appear at the combo box
            for s in clists:
                self.__combo.append_text(s)
            self.__combo.set_active(0)

    def __clean(self):
        # Empty the main elements container
        for c in self.__ppalvbox.get_children():
            self.__ppalvbox.remove(c)

    def main(self):
        gtk.main()
        return 0

    def destroy(self, widget):
        self.__save()
        gtk.main_quit()

# Python's ugliness :P
if __name__ == "__main__":
    cl = Checklist()
    cl.main()
