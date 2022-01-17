# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from . import LoadSave as LoadSaveInterface
import os
import torch
from typing import Any, Callable, Optional, Tuple

class LoadSave(LoadSaveInterface):
    def load(self, path: str) -> Optional[Tuple[int, Callable, Any, Any]]:
        saves = os.listdir(path)
        saves = [(int(x.replace('.', '_').split('_')[1]), x) for x in saves
                 if x.startswith('saver_')]
        saves.sort()

        if not saves:
            return None

        return (saves[-1][0], *torch.load(path + '/' + saves[-1][1]))

    def save(self, path: str, version: int, f: Callable, args: Any, kwargs: Any):
        torch.save((f, args, kwargs), f'{path}/saver-tmp.pt')
        os.rename(f'{path}/saver-tmp.pt', f'{path}/saver_{version}.pt')

class LoadSaveWithoutVersion(LoadSaveInterface):
    def load(self, path: str) -> Optional[Tuple[int, Callable, Any, Any]]:
        if not os.path.exists(f'{path}/saver.pt'):
            return None
        return (0, *torch.load(f'{path}/saver.pt'))

    def save(self, path: str, version: int, f: Callable, args: Any, kwargs: Any):
        torch.save((f, args, kwargs), f'{path}/saver-tmp.pt')
        os.replace(f'{path}/saver-tmp.pt', f'{path}/saver.pt')
