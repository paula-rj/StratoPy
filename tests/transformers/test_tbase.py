#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
import pytest

from stratopy.transformers import tbase


def test_raises():
    with pytest.raises(TypeError):
        tbase.TransformerABC()


def test_transformer_notimp():
    class FakeTransformer(tbase.TransformerABC):
        pass

    with pytest.raises(TypeError):  # no deberia ser not implemented?
        FakeTransformer()


def test_wrong_parameters():
    class FakeNewTransform(tbase.TransformerABC):
        _transformers_params = {"self", "param0"}

        def transform(self, param0):
            return param0

    tobj = FakeNewTransform()
    with pytest.raises(TypeError):
        tobj.transform()


def test_BinaryTransformer():
    class FakeBinTransform(tbase.BinaryTransformerABC):
        def transform(self, sat0, sat1):
            return [sat0, sat1]

    tobj = FakeBinTransform()
    response = tobj.transform(sat0="a", sat1="b")
    assert response[0] == "a"
    assert response[1] == "b"


def test_UnaryTransformer():
    class FakeUnaryTransform(tbase.UnaryTransformerABC):
        def transform(self, sat0):
            return sat0

    tobj = FakeUnaryTransform()
    response = tobj.transform(sat0="c")
    assert response == "c"
