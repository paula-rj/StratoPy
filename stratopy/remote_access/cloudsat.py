#!/usr/bin/env python
# -*- coding: utf-8 -*-
# License: MIT (https://tldrlegal.com/license/mit-license)
# Copyright (c) 2022, Paula Romero Jure et al.
# All rights reserved.

from . import base


class CloudSat(base.ConnectorABC):

    _PRODUCT_TYPES_PARSERS = {"2B-CLDCLASS": None, "2B-CLDCLASS-LIDAR": None}

    def __init__(self, product_type):
        self.product_type = product_type

    def __repr__(self):
        return f"<CloudSat product_type={self.product_type!r}>"

    def get_endpoint(self):
        ...

    def _makequery(self, endpoint, date):
        # 2019009155049_67652_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf
        ...

    def _parse_result(self, result):
        ...
