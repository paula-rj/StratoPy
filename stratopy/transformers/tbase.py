#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.
r"""Module that defines the basic implementation for each transformer."""

# =============================================================================
# IMPORTS
# =============================================================================

import abc
import inspect


class TransformerABC(abc.ABC):
    """Transformers base class.

    Args
    ----
        cls (cls): class

    Raises
    ------
        TypeError: If satellites names are not given.
    """

    _transformers_params = None

    def __init_subclass__(cls):
        """Initialization class.

        Raises
        ------
            TypeError: If class dont have sats names or obj.
        """
        if cls.transformer is not TransformerABC.transformer:
            original_signature = cls._transformers_params
            new_signature = inspect.signature(cls.transformer)
            diff = original_signature.symmetric_difference(
                new_signature.parameters
            )
            if diff:
                cls_name = cls.__name__
                raise TypeError(
                    f"'{cls_name}.transformer() has an unexpected parameter/s: {diff}"
                )

    @abc.abstractmethod
    def transformer(self):
        """Abstract method to be implemented for any new transformer."""
        pass


class BinaryTransformerABC(TransformerABC):
    """Binary Transformer.

    Takes two satellites inputs and returns one merged object.
    """

    _transformers_params = {"self", "sat0", "sat1"}


class UnaryTransformerABC(TransformerABC):
    """Unary Transformer.

    Takes two satellites inputs and returns one merged object.
    """

    _transformers_params = {"self", "sat0"}
