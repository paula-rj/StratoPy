#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import pytest
from stratopy.transformers import tbase


def test_raises():
    with pytest.raises(TypeError):
        tobj = tbase.TransformerABC()


def test_BinaryTransformer():
    class FakeBinTransform(tbase.BinaryTransformerABC):
        def transformer(self, sat0, sat1):
            return [sat0, sat1]

    tobj = FakeBinTransform()
    response = tobj.transformer(sat0="a", sat1="b")
    assert response[0] == "a"
    assert response[1] == "b"


def test_UnaryTransformer():
    class FakeUnaryTransform(tbase.UnaryTransformerABC):
        def transformer(self, sat0):
            return sat0

    tobj = FakeUnaryTransform()
    response = tobj.transformer(sat0="c")
    assert response == "c"
