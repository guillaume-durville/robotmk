#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2020             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from robot.api import ExecutionResult
import tempfile
import os

f_tmpxml = tempfile.NamedTemporaryFile(delete=False)

def parse_robot(info):
    for line in info:
        f_tmpxml.write(line[0])
    f_tmpxml.close()
    return f_tmpxml.name

def inventory_robot(tmpxml_name):
    #result = ExecutionResult('/tmp/output.xml')
    result = ExecutionResult(tmpxml_name)
    for s in result.suite.suites:
        # each Suite name is a check, no default parameters (yet)
        yield s.name, None
        # print s.name
    # delete the tempfile
    os.remove(tmpxml_name)

def check_robot(item, params, info):
    warn, crit = params
    for line in info:
        if line[0] == item:
            power = saveint(line[1])
            # Some "RPS SpA" systems are not RFC conform in this value.
            # The values can get negative but should never be.
            if power < 0:
                power *= -1
            perfdata = [("power", power, warn, crit, 0)]
            infotext = "power: %dW (warn/crit at %dW/%dW)" % \
                (power, warn, crit)

            if power <= crit:
                return (2, infotext, perfdata)
            elif power <= warn:
                return (1, infotext, perfdata)
            return (0, infotext, perfdata)

    return (3, "Phase %s not found in SNMP output" % item)


#check_info = {}
check_info['robot'] = {
    "parse_function": parse_robot,
    "inventory_function": inventory_robot,
    "check_function": check_robot,
    "service_description": "Robot robot",
}
