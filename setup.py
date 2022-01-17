# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from setuptools import find_packages, setup

setup(
    name='saver',
    version='0.0.2',
    packages=find_packages(where='src'),
    package_dir={'': 'build', 'saver': 'src/saver'},
)
