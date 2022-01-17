# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any, Callable, Optional, Tuple

class LoadSave():
    def load(self, path: str) -> Optional[Tuple[int, Callable, Any, Any]]:
        raise NotImplementedError

    def save(self, path: str, version: int, f: Callable, args: Any, kwargs: Any):
        raise NotImplementedError

class Saver():
    def __init__(self, path: str, ls: LoadSave, *, skip_args=0, skip_kwargs=set()):
        self._path = path
        self._ls = ls
        self._skip_args = skip_args
        self._skip_kwargs = skip_kwargs

        self._next_version = 0

    def run(*args, **kwargs):
        self = args[0]
        f = args[1]
        args = args[2:]

        ret = self._ls.load(self._path)
        if ret is None:
            version = -1
        else:
            version, f, saved_args, saved_kwargs = ret[0], ret[1], ret[2], ret[3]

            # Add back skipped args/kwargs.
            assert(len(args) >= self._skip_args)
            args = args[:self._skip_args] + saved_args
            for kw in self._skip_kwargs:
                if kw in kwargs:
                    saved_kwargs[kw] = kwargs[kw]
                elif kw in saved_kwargs:
                    del saved_kwargs[kw]
            kwargs = saved_kwargs
            del saved_args, saved_kwargs

        self._next_version = version + 1

        while True:
            ret = f(*args, **kwargs)
            if ret is None:
                break
            f, args, kwargs, options = ret

            # Remove skipped args/kwargs.
            assert(len(args) >= self._skip_args)
            saved_args = args[self._skip_args:]
            saved_kwargs = {}
            for kw in kwargs:
                if kw not in self._skip_kwargs:
                    saved_kwargs[kw] = kwargs[kw]

            if options.get('overwrite', False) and self._next_version > 0:
                self._next_version -= 1 # Overwrite previous version.

            self._ls.save(self._path, self._next_version, f, saved_args, saved_kwargs)
            self._next_version += 1

def call(*args, **kwargs):
    return args[0], args[1:], kwargs, {}

def call_overwrite(*args, **kwargs):
    return args[0], args[1:], kwargs, {'overwrite': True}
