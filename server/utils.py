#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import re

from caliper.server.shared.utils import *
from caliper.server.shared import error
from caliper.server.shared import caliper_path
from caliper.server.shared.settings import settings

def get_target_exec_dir(target):
    try:
        target_arch = get_host_arch(target)
    except error.ServUnsupportedError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    except error.ServRunError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    target_execution_dir = os.path.abspath(
            os.path.join(caliper_path.GEN_DIR, target_arch))
    return target_execution_dir

def get_host_arch(host):
    try:
        arch_result = host.run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])

    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            if re.search('x86_64', output):
                return 'x86_64'
            elif re.search('i[36]86', output):
                return 'x86_32'
            elif re.search('aarch64', output):
                return 'arm_64'
            else:
                if re.search('arm_32', output) or re.search('armv7', output):
                    return 'arm_32'
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)


def get_host_name(host):
    try:
        arch_result = host.run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            try:
                machine_name = settings.get_value('Common', 'testtask_name', type=str)
            except:
                machine_name = output.split(" ")[1]
            return machine_name
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)

def get_local_machine_arch():
    try:
        arch_result = run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            if re.search('x86_64', output):
                return 'x86_64'
            elif re.search('i[36]86', output):
                return 'x86_32'
            elif re.search('aarch64', output):
                return 'arm_64'
            else:
                if re.search('arm_32', output) or re.search('armv7', output):
                    return 'arm_32'
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)



def sh_escape(command):
    """
    Escape special characters from a command so that it can be passed
    as a double quoted (" ") string in a (ba)sh command
    """
    command = command.replace("\\", "\\\\")
    command = command.replace("$", r'\$')
    command = command.replace('"', r'\"')
    command = command.replace('`', r'\`')
    return command


def get_server_dir():
    path = os.path.dirname(sys.modules['caliper.server.utils'].__file__)
    return os.path.abspath(path)


def scp_remote_escape(filename):
    """
    Escape special characters from a filename so that it can be passed
    to scp (within double quotes) as a remote file.

    Bis-quoting has to be used with scp for remote files, "bis-quoting"
    as in quoting x 2
    scp does not support a newline in the filename

    Args:
        filename: the filename string to escape.

    Returns:
        The escaped filename string. The required englobing double
        quotes are NOT added and so should be added at some point by
        the caller.
    """
    escape_chars = r' !"$&' "'" r'()*,:;<=>?[\]^`{|}'

    new_name = []
    for char in filename:
        if char in escape_chars:
            new_name.append("\\%s" % (char,))
        else:
            new_name.append(char)

    return sh_escape("".join(new_name))
