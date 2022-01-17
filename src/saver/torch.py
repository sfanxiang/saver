# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from . import LoadSave as LoadSaveInterface
import os
import torch
from typing import Any, Callable, Optional, Tuple

class LoadSave(LoadSaveInterface):
    def __init__(self, prefix='saver'):
        assert('.' not in prefix)
        self._prefix = prefix

    def load(self, path: str) -> Optional[Tuple[int, Callable, Any, Any]]:
        saves = os.listdir(path)
        saves = [(int(x.split('.')[1]), x) for x in saves if x.startswith(f'{self._prefix}.')]
        saves.sort()

        if not saves:
            return None

        return (saves[-1][0], *torch.load(path + '/' + saves[-1][1]))

    def save(self, path: str, version: int, f: Callable, args: Any, kwargs: Any):
        torch.save((f, args, kwargs), f'{path}/{self._prefix}-tmp.pt')
        os.rename(f'{path}/{self._prefix}-tmp.pt', f'{path}/{self._prefix}.{version}.pt')

class LoadSaveWithoutVersion(LoadSaveInterface):
    def __init__(self, prefix='saver'):
        assert('.' not in prefix)
        self._prefix = prefix

    def load(self, path: str) -> Optional[Tuple[int, Callable, Any, Any]]:
        if not os.path.exists(f'{path}/{self._prefix}.pt'):
            return None
        return (0, *torch.load(f'{path}/{self._prefix}.pt'))

    def save(self, path: str, version: int, f: Callable, args: Any, kwargs: Any):
        torch.save((f, args, kwargs), f'{path}/{self._prefix}-tmp.pt')
        os.replace(f'{path}/{self._prefix}-tmp.pt', f'{path}/{self._prefix}.pt')
