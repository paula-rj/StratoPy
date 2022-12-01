#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

# =============================================================================
# IMPORTS
# =============================================================================

from unittest import mock

import diskcache

from stratopy.utils import cache

# =============================================================================
# TESTS
# =============================================================================


def test_get_default_cache():
    dcache = cache.get_default_cache()
    assert dcache is cache.get_default_cache()
    assert str(dcache.directory) == str(cache.DEFAULT_CACHE_DIR)


def test_from_cache():
    mock_cache = mock.MagicMock()
    mock_cache.__enter__.return_value = mock_cache
    mock_cache.get.return_value = diskcache.core.ENOVAL

    tag = "tag_xyz"

    result = cache.from_cache(
        mock_cache,
        tag=tag,
        function=lambda: 42,
        cache_expire=None,
        force=False,
    )

    expected_key = diskcache.core.args_to_key(
        base=("stratopy", tag), args=(), kwargs={}, typed=False, ignore=[]
    )

    assert result == 42
    mock_cache.get.assert_called_once_with(
        expected_key, default=diskcache.core.ENOVAL, retry=True
    )
    mock_cache.set.assert_called_once_with(
        expected_key, 42, expire=None, tag=tag, retry=True
    )
