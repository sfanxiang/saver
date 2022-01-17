# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from . import LoadSave as LoadSaveInterface
import numpy as np
import os
import random
import torch
from typing import Any, Callable, Optional, Tuple

class LoadSave(LoadSaveInterface):
    def __init__(self, prefix='saver', *, version=True, cpu_rng_state=True):
        assert('.' not in prefix)
        self._prefix = prefix
        self._version = version
        self._cpu_rng_state = cpu_rng_state

    def _get_load_version_and_filename(self, path):
        if self._version:
            saves = os.listdir(path)
            saves = [(int(x.split('.')[1]), x) for x in saves if x.startswith(f'{self._prefix}.')]
            saves.sort()
            if not saves:
                return None
            return (saves[-1][0], path + '/' + saves[-1][1])
        else:
            if not os.path.exists(f'{path}/{self._prefix}.pt'):
                return None
            return (0, f'{path}/{self._prefix}.pt')

    def _get_save_filenames(self, path, version):
        if self._version:
            tmp = f'{path}/{self._prefix}-tmp.pt'
            save = f'{path}/{self._prefix}.{version}.pt'
        else:
            tmp = f'{path}/{self._prefix}-tmp.pt'
            save = f'{path}/{self._prefix}.pt'
        return tmp, save

    def load(self, path: str) -> Optional[Tuple[int, Callable, Any, Any]]:
        ret = self._get_load_version_and_filename(path)
        if ret is None:
            return None
        version, filename = ret

        save, options = torch.load(filename)
        if self._cpu_rng_state:
            py_rng, pt_rng, np_rng = options['cpu_rng_state']
            random.setstate(py_rng)
            torch.set_rng_state(pt_rng)
            np.random.set_state(np_rng)

        return (version, *save)

    def save(self, path: str, version: int, f: Callable, args: Any, kwargs: Any):
        save = (f, args, kwargs)
        options = {}
        if self._cpu_rng_state:
            options['cpu_rng_state'] = \
                (random.getstate(), torch.get_rng_state(), np.random.get_state())

        tmp_filename, save_filename = self._get_save_filenames(path, version)

        torch.save((save, options), tmp_filename)
        os.replace(tmp_filename, save_filename)
