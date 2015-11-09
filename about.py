#!/usr/bin/env python
"""Helper functions about application
"""


class AboutHelper(object):

    @classmethod
    def version(cls):
        """Returns the version contained by the file VERSION
        """
        version_file = open('VERSION', 'r')
        version = version_file.readline()

        return version

    @classmethod
    def funny_title(cls):
        return "           _           _                             \n"\
            "          (_)         | |                            \n"\
            " _ __ ___  _ _ __  ___| |_ ___  _ __ __ _  __ _  ___ \n"\
            "| '_ ` _ \\| | '_ \\/ __| __/ _ \\| '__/ _` |/ _` |/ _ \\\n"\
            "| | | | | | | | | \\__ \\ || (_) | | | (_| | (_| |  __/\n"\
            "|_| |_| |_|_|_| |_|___/\\__\\___/|_|  \\__,_|\\__, |\\___|\n"\
            "                                           __/ |     \n"\
            "                                          |___/      \n\n"

    @classmethod
    def license(cls):
        return "This program is free software: you can redistribute it and/or modify\n"\
            "it under the terms of the GNU General Public License as published by\n"\
            "the Free Software Foundation, either version 3 of the License, or\n"\
            "(at your option) any later version.\n\n"\
            "This program is distributed in the hope that it will be useful,\n"\
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"\
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"\
            "GNU General Public License for more details.\n\n"\
            "You should have received a copy of the GNU General Public License\n"\
            "along with this program.  If not, see <http://www.gnu.org/licenses/>.\n\n"


    @classmethod
    def help_info(cls, default_port):
        """
        Returns the help information about this module
        """
        msg = cls.funny_title()
        msg += "minstore {!s}. Storage engine API with mirroring support.\n"\
            .format(cls.version())
        msg += "by Jaume Mila <jaume@westial.com>\n\n"\

        msg += cls.license()

        msg += "Usage: python api.py SERVERS_LIST_PATH BASE_PATH [PORT]\n\n"
        msg += "\tSERVERS_LIST_PATH: path to the file with the list of servers.\n"
        msg += "\t\t\tThe servers.list file is required, although the file can\n"
        msg += "\t\t\tbe an empty file. When the file is empty, it assumes that\n"
        msg += "\t\t\tthere are no mirrors. List the mirror servers one by one\n"
        msg += "\t\t\tseparated by line break. http/s and port are required.\n"
        msg += "\t\t\tExample: http://127.0.0.1:8002\n"
        msg += "\tBASE_PATH: path to the directory for the storage files.\n"
        msg += "\tPORT: Port to use. Default port is {:d}.\n\n"\
            .format(default_port)

        msg += "Example: \n"
        msg += "\t/usr/bin/python /opt/minstore/api.py \\\n"
        msg += "\t/etc/minstore/servers.list /var/lib/minstore/storage 8001\n\n"

        return msg
