import datetime

from unittest import mock, TestCase

import dateutil

from stratopy.remote_access import goes


PATH_CHANNEL_13 = (
    "data/GOES16/"
    "OR_ABI-L2-CMIPF-M3C13_G16_s20190040600363_e20190040611141_"
    "c20190040611220.nc"
)

a_date = dateutil.parser.parse("june 25th 2022 18:00 UTC") 
names_ok = {"L1b-RadF": 'OR_L1b-RadF-M6C13_G16_s20221761800*',
    "ABI-L2-CMIPF" :'OR_ABI-L2-CMIPF-M6C13_G16_s20221761800*'

    }

def test_default_product_parser():
    #deberia ser mas extensivo este test capaz
    channel = 13
    mode = 6
    dtime = a_date
    names_ok = {"L1b-RadF": 

    }
    for ptype in goes.GOES16._PRODUCT_TYPES_PARSERS.keys(), names_ok.keys():
        assert goes._default_product_parser(ptype, mode, channel, dtime)