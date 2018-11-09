#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Baseboard abstraction for USB4butia
#
# Copyright (c) 2012-2015 Alan Aguiar alanjas@hotmail.com
# Copyright (c) 2012-2015 Butiá Team butia@fing.edu.uy
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


NULL_BYTE = 0x00

DEFAULT_PACKET_SIZE               = 0x04
GET_USER_MODULES_SIZE_COMMAND     = 0x05
GET_USER_MODULE_LINE_COMMAND      = 0x06
GET_HANDLER_SIZE_COMMAND          = 0x0A
GET_HANDLER_TYPE_COMMAND          = 0x0B
ADMIN_HANDLER_SEND_COMMAND        = 0x00
CLOSEALL_COMMAND                  = 0x07
CLOSEALL_RESPONSE_PACKET_SIZE     = 0x05
SWITCH_TO_BOOT_BASE_BOARD_COMMAND = 0x09
RESET_BASE_BOARD_COMMAND          = 0xFF
GET_USER_MODULE_LINE_PACKET_SIZE  = 0x05
GET_LINES_RESPONSE_PACKET_SIZE    = 0x05
GET_LINE_RESPONSE_PACKET_SIZE     = 0x0C
GET_HANDLER_TYPE_PACKET_SIZE      = 0x05
GET_HANDLER_RESPONSE_PACKET_SIZE  = 0x05

ERROR = -1

class Baseboard():

    def __init__(self, dev, debug=False):
        self.dev = dev
        self.debug = debug
        self.listi = {}
        self.devices = {}
        self.openables_loaded = []
        self.hack_states = {}
        for i in range(1, 9):
            self.hack_states[i] = 1

    def _debug(self, message, err=''):
        if self.debug:
            print message, err

    def open_baseboard(self):
        """
        Open the baseboard
        """
        self.dev.open_device()

    def close_baseboard(self):
        """
        Close the baseboard
        """
        self.dev.close_device()

    def get_info(self):
        """
        Get baseboard info: manufacture..
        """
        return self.dev.get_info()

    def add_device(self, handler, device):
        """
        Add a device with handler of the dictionary
        """
        self.devices[handler] = device
        if device.openable:
            if not(device.name in self.openables_loaded):
                self.openables_loaded.append(device.name)

    def remove_device(self, handler):
        """
        Remove a device with handler of the dictionary
        """
        if self.devices.has_key(handler):
            dev = self.devices.pop(handler)
            if dev.openable:
                if dev.name in self.openables_loaded:
                    self.openables_loaded.remove(dev.name)

    def reset_device_list(self):
        """
        Cleans the device dictionary
        """
        self.devices = {}

    def get_openables_loaded(self):
        """
        Get the list of modules that was openened (no pnp)
        """
        return self.openables_loaded

    def reset_openables_loaded(self):
        """
        Reset the list of openables modules
        """
        self.openables_loaded = []

    def get_listi(self, force=False):
        """
        Get the listi: the list of modules present in the board that can be
        opened (or pnp module opens)
        """
        if (self.listi == {}) or force:
            self._generate_listi()
        return self.listi

    def _generate_listi(self):
        """
        Generate the listi: the list of modules present in the board that can be
        opened (or pnp module opens)
        """
        self.listi = {}
        try:
            s = self.get_user_modules_size()
            for m in range(s):
                self.listi[m] = self.get_user_module_line(m)
        except:
            self.listi = {}
            self._debug('ERROR:baseboard listi')

    def set_hack_state(self, hack, state):
        if hack in self.hack_states:
            self.hack_states[hack] = state

    def get_hack_state(self, hack):
        if hack in self.hack_states:
            return self.hack_states[hack]

    def get_device_handler(self, name):
        """
        Get the handler of device with name: name
        """
        for e in self.devices:
            if self.devices[e].name == name:
                return e
        return ERROR

    def get_device_name(self, handler):
        """
        Get the name of device with handler: handler
        """
        if self.devices.has_key(handler):
            return self.devices[handler].name
        else:
            return ''

    def get_user_modules_size(self):
        """
        Get the size of the list of user modules (listi)
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, DEFAULT_PACKET_SIZE, NULL_BYTE]
        w.append(GET_USER_MODULES_SIZE_COMMAND)
        self.dev.write(w)
        raw = self.dev.read(GET_USER_MODULE_LINE_PACKET_SIZE)
        self._debug('baseboard:get_user_modules_size', raw)
        return raw[4]

    def get_user_module_line(self, index):
        """
        Get the name of device with index: index (listi)
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, GET_USER_MODULE_LINE_PACKET_SIZE, NULL_BYTE]
        w.append(GET_USER_MODULE_LINE_COMMAND)
        w.append(index)
        self.dev.write(w)
        raw = self.dev.read(GET_LINE_RESPONSE_PACKET_SIZE)
        self._debug('baseboard:get_user_module_line', raw)
        c = raw[4:len(raw)]
        t = ''
        for e in c:
            if not(e == NULL_BYTE):
                t = t + chr(e)
        return t

    def get_handler_size(self):
        """
        Get the number of handlers opened
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, DEFAULT_PACKET_SIZE, NULL_BYTE]
        w.append(GET_HANDLER_SIZE_COMMAND)
        self.dev.write(w)
        raw = self.dev.read(GET_HANDLER_RESPONSE_PACKET_SIZE)
        self._debug('baseboard:get_handler_size', raw)
        return raw[4]

    def get_handler_type(self, index):
        """
        Get the type of the handler: index (return listi index)
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, GET_HANDLER_TYPE_PACKET_SIZE, NULL_BYTE]
        w.append(GET_HANDLER_TYPE_COMMAND)
        w.append(index)
        self.dev.write(w)
        raw = self.dev.read(GET_HANDLER_RESPONSE_PACKET_SIZE)
        self._debug('baseboard:get_handler_type', raw)
        return raw[4]

    def switch_to_bootloader(self):
        """
        Admin module command to switch to bootloader
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, DEFAULT_PACKET_SIZE, NULL_BYTE]
        w.append(SWITCH_TO_BOOT_BASE_BOARD_COMMAND)
        self.dev.write(w)

    def reset(self):
        """
        Admin module command to reset the board
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, DEFAULT_PACKET_SIZE, NULL_BYTE]
        w.append(RESET_BASE_BOARD_COMMAND)
        self.dev.write(w)

    def force_close_all(self):
        """
        Admin module command to force close all opened modules
        """
        w = [ADMIN_HANDLER_SEND_COMMAND, DEFAULT_PACKET_SIZE, NULL_BYTE]
        w.append(CLOSEALL_COMMAND)
        self.dev.write(w)
        raw = self.dev.read(CLOSEALL_RESPONSE_PACKET_SIZE)
        self._debug('baseboard:force_close_all', raw)
        return raw[4]

