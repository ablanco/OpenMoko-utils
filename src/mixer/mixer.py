#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Alsa mixer written in Python for the Neo Freerunner phone
#Copyright (C) 2009  Alejandro Blanco Escudero

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
import alsaaudio

class Mixer:
    __h = 40
    __home = os.environ['HOME'] + "/.pyMixer/"
    __activeFile = __home + "channels"
    __phoneCallFile = "/usr/share/shr/scenarii/gsmhandset.state"
    #__phoneCallFile = "./gsmhandset.state" # For testing with a copy of the file
    __channels = ['PCM', 'Headphone'] # Default channels

    def __init__(self):
        # Check that the folder and channels file exists
        if not(os.access(self.__home, os.F_OK)):
            os.makedirs(self.__home)
        if not(os.access(self.__activeFile, os.F_OK)):
            fich = open(self.__activeFile, "w")
            for c in self.__channels:
                fich.write(c)
                fich.write("\n")
            fich.close()

        # Read the active channels from the file
        self.__load_channels()

        # Main window
        self.__window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.__window.connect("destroy", self.destroy)
        self.__window.set_title("Alsa Mixer")
        self.__window.set_border_width(0)
        # Neo FreeRunner's screen resolution
        self.__window.set_size_request(480, 640)

        # Scroll area for the sliders or the channels
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(0)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.show()

        # Main packing vertical box
        mainvbox = gtk.VBox(False, 3)
        self.__window.add(mainvbox)
        mainvbox.pack_start(scrolled_window, True, True, 0)

        # Sliders packing vertical box
        self.__sldvbox = gtk.VBox(False, 3)
        scrolled_window.add_with_viewport(self.__sldvbox)
        self.__sldvbox.show()
        self.__init_sliders()

        # Options and exit buttons
        bhbox = gtk.HBox(True, 3)
        self.__buttonO = gtk.Button("Channels")
        self.__buttonO.connect("clicked", self.__callback_options)
        self.__buttonO.set_size_request(-1, self.__h)
        self.__buttonC = gtk.Button("Cancel")
        self.__buttonC.connect("clicked", self.__callback_cancel_options)
        self.__buttonC.set_size_request(-1, self.__h)
        self.__buttonE = gtk.Button("Exit")
        self.__buttonE.connect("clicked", self.destroy)
        self.__buttonE.set_size_request(-1, self.__h)
        self.__buttonS = gtk.Button("Save")
        self.__buttonS.connect("clicked", self.__callback_save_options)
        self.__buttonS.set_size_request(-1, self.__h)
        bhbox.add(self.__buttonO)
        bhbox.add(self.__buttonS)
        bhbox.add(self.__buttonC)
        bhbox.add(self.__buttonE)
        mainvbox.pack_start(bhbox, False, False, 0)
        # Not all the buttons are visible all the time
        self.__buttonO.show()
        self.__buttonE.show()
        bhbox.show()
        mainvbox.show()
        self.__window.show()

    def __init_sliders(self):
        # If the config file is present and accessible
        if os.access(self.__phoneCallFile, os.F_OK):
            label = gtk.Label("Phone Call")
            self.__sldvbox.pack_start(label, False, False, 0)
            label.show()
            volume = self.__getPhoneCallVolume()
            adjustment = gtk.Adjustment(volume, 0, 127, 1)
            # Phone call volume slider, always present
            phoneCallSlider = gtk.HScale(adjustment)
            phoneCallSlider.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
            phoneCallSlider.set_value_pos(gtk.POS_RIGHT)
            phoneCallSlider.connect("value_changed", self.__on_slider_change,
                                    "phoneCall", phoneCallSlider)
            self.__sldvbox.pack_start(phoneCallSlider, False, True, 0)
            phoneCallSlider.show()

        # Create the sliders for the selected alsa channels
        for c in self.__channels:
            c = c.replace("\n", "") # Trim the name of the channel
            label = gtk.Label(c)
            self.__sldvbox.pack_start(label, False, False, 0)
            label.show()
            mixer = alsaaudio.Mixer(c) # The channel controller
            # There are two values for each channel, here I asume both are
            # the same. Each slider controls both, right and left subchannels
            volume = float(mixer.getvolume()[0])
            adjustment = gtk.Adjustment(volume, 0, 100, 1)
            slider = gtk.HScale(adjustment)
            slider.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
            slider.set_value_pos(gtk.POS_RIGHT)
            slider.connect("value_changed", self.__on_slider_change, c, slider)
            self.__sldvbox.pack_start(slider, False, True, 0)
            slider.show()

    # This method sets the new values as soon as the user release the slider
    def __on_slider_change(self, widget, channel, slider):
        # It saves the int (truncate) value of the slider
        if channel == "phoneCall":
            # Special case
            self.__setPoneCallVolume(int(slider.get_adjustment().get_value()))
        else:
            mixer = alsaaudio.Mixer(channel)
            mixer.setvolume(int(slider.get_adjustment().get_value()))

    def __getPhoneCallVolume(self):
        # The file must be accessible, or the method wouldn't been called
        fich = open(self.__phoneCallFile, "r")
        data = fich.readlines()
        i = 0
        # Search for the info, heavily dependent on the format of the file
        for l in data:
            if l.count("control.4") > 0:
                return float(data[i + 7].split(" ")[1])
            i = i + 1
        fich.close()

    def __setPoneCallVolume(self, vol):
        # The file must be accessible, or the method wouldn't been called
        fich = open(self.__phoneCallFile, "r")
        data = fich.readlines()
        fich.close()
        i = 0
        # Search for the info, heavily dependent on the format of the file
        for l in data:
            if l.count("control.4") > 0:
                data[i + 7] = "\t\tvalue.0 " + str(vol) + "\n"
                data[i + 8] = "\t\tvalue.1 " + str(vol) + "\n"
                break
            i = i + 1
        fich = open(self.__phoneCallFile, "w")
        fich.writelines(data)
        fich.close()

    def __load_channels(self):
        if os.access(self.__activeFile, os.F_OK):
            # It reads the selected channels by the user
            fich = open(self.__activeFile, "r")
            self.__channels = fich.readlines()
            fich.close()

    def __clean(self):
        # Empty the main elements container
        for c in self.__sldvbox.get_children():
            self.__sldvbox.remove(c)

    def __callback_options(self, widget):
        self.__clean()
        mixers = alsaaudio.mixers() # List of channels
        for m in mixers:
            cb = gtk.CheckButton(m)
            active = self.__channels.count(m + "\n") > 0
            cb.set_active(active)
            # TODO make the tick boxes bigger
            self.__sldvbox.pack_start(cb, False, True, 0)
            cb.show()
        # Change which buttons are visible
        self.__buttonE.hide()
        self.__buttonO.hide()
        self.__buttonS.show()
        self.__buttonC.show()

    def __callback_save_options(self, widget):
        fich = open(self.__activeFile, "w")
        self.__channels = [] # Reset the selected list
        for cb in self.__sldvbox.get_children():
            if cb.get_active(): # If the check box is ticked
                fich.write(cb.get_label())
                fich.write("\n")
                self.__channels.append(cb.get_label() + "\n")
        fich.close()
        self.__callback_cancel_options() # Reload the sliders

    def __callback_cancel_options(self, widget=None):
        self.__clean()
        # Change which buttons are visible
        self.__init_sliders()
        self.__buttonS.hide()
        self.__buttonC.hide()
        self.__buttonE.show()
        self.__buttonO.show()

    def main(self):
        gtk.main()
        return 0

    def destroy(self, widget):
        gtk.main_quit()

# Python's ugliness :P
if __name__ == "__main__":
    mx = Mixer()
    mx.main()
