#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: 2016 IBM.
# Author: Jayarama<jsomalra@linux.vnet.ibm.com>

# Based on code by
#   Author: Abdul Haleem <abdhalee@linux.vnet.ibm.com>

import os
import fnmatch

from avocado import Test
from avocado import main

from avocado.utils import archive
from avocado.utils import build
from avocado.utils import process

from avocado.utils.software_manager import SoftwareManager


class Binutils(Test):
    """
    This testcase make use of testsuite provided by the
    source package, performs functional test for all binary tools
    source file is downloaded and compiled.
    """

    def check_install(self, package):
        """
        Appends package to `self._needed_deps` when not able to install it
        """
        if (not self._sm.check_installed(package) and
                not self._sm.install(package)):
            self._needed_deps.append(package)

    def setUp(self):
        # Check for basic utilities
        self._sm = SoftwareManager()

        # Install required tools and resolve dependencies
        self._needed_deps = []

        self.check_install('rpmbuild')
        self.check_install('elfutils')
        self.check_install('build')
        self.check_install('autoconf')
        self.check_install('automake')
        self.check_install('binutils-devel')
        self.check_install('djangu')
        self.check_install('libtool')
        self.check_install('glibc-static')
        self.check_install('zlib-static')

        if len(self._needed_deps) > 0:
            self.log.warn('Please install these dependencies %s'
                          % self._needed_deps)

        # Extract - binutils
        # Source: https://ftp.gnu.org/gnu/binutils/binutils-2.26.tar.bz2
        locations = ['https://ftp.gnu.org/gnu/binutils/binutils-2.26.tar.bz2',
                     "ftp://ftp.fi.muni.cz/pub/gnu/gnu/binutils/"
                     "binutils-2.26.tar.bz2"]
        tarball = self.fetch_asset("binutils-2.26.tar.bz2",
                                   locations=locations)
        archive.extract(tarball, self.srcdir)

        bintools_version = os.path.basename(tarball.split('.tar.')[0])
        self.src_dir = os.path.join(self.srcdir, bintools_version)

        # Compile the binutils
        os.chdir(self.src_dir)
        process.run('./configure')
        build.make(self.src_dir)

    def test(self):
        """
        Runs the binutils `make check`
        """
        ret = build.make(self.src_dir, extra_args='check', ignore_status=True)

        errors = 0
        for root, _, filenames in os.walk(self.src_dir):
            for filename in fnmatch.filter(filenames, '*.log'):
                filename = os.path.join(root, filename)
                logfile = filename[:-4] + ".log"
                os.system('cp ' + logfile + ' ' + self.logdir)
                with open(logfile) as result:
                    for line in result.readlines():
                        if line.startswith('FAIL'):
                            errors += 1
                            self.log.error(line)
        if errors:
            self.fail("%s test(s) failed, check the log for details." % errors)
        elif ret:
            self.fail("'make check' finished with %s, but no FAIL lines were "
                      "found." % ret)


if __name__ == "__main__":
    main()
