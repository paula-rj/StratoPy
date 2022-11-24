#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================

import functools
import os
import pickle
import pathlib

import diskcache as dcache

# =============================================================================
# CONSTANTS
# =============================================================================

#: Where carpyncho gonna store the entire data.
STRATOPY_DEFAULT_DATA_PATH = pathlib.Path(
    os.path.expanduser(os.path.join("~", "stratopy_data"))
)

#: The location of the cache database and files.
DEFAULT_CACHE_DIR = STRATOPY_DEFAULT_DATA_PATH / "_cache_"

# =============================================================================
# FUNCTIONS
# =============================================================================

@functools.lru_cache(maxsize=None)
def get_default_cache():
    """The default cache of stratopy.

    This functions always return the same cache.

    """
    return dcache.Cache(
        directory=DEFAULT_CACHE_DIR,
        default_pickle_protocol=pickle.DEFAULT_PROTOCOL,
    )


def from_cache(
    cache, tag, function, cache_expire, force=False, *args, **kwargs
):
    """Simplify cache orchestration.

    Parameters
    ----------
    tag: str
        Normally every function call the cache with their own tag.
        We sugest "module.function" or "module.Class.function"

    function: callable
        The function to be cached

    force: bool (default=False)
        If the vale of the cache must be ignored and re-execute the
        function.

    cache_expire: bool or None
        Time in seconds to expire the function call

    args and kwargs:
        All the parameters needed to execute the function.

    Returns
    -------
    The result of calling the function or the cached version of the same value.

    """
    # start the cache orchestration
    key = dcache.core.args_to_key(
        base=("stratopy", tag),
        args=args,
        kwargs=kwargs,
        typed=False,
        ignore=[],
    )

    with cache as c:
        c.expire()

        value = (
            dcache.core.ENOVAL
            if force
            else c.get(key, default=dcache.core.ENOVAL, retry=True)
        )

        if value is dcache.core.ENOVAL:
            value = function(*args, **kwargs)
            c.set(
                key,
                value,
                expire=cache_expire,
                tag=tag,
                retry=True,
            )

    return value
