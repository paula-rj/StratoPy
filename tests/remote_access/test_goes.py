import datetime

from unittest import mock, TestCase

import dateutil

from stratopy.remote_access import goes


PATH_CHANNEL_13 = (
    "s3://noaa-goes16/L1b-RadF"
    "OR_L1b-RadF-M6C13_G16_s20221761800*"
)

a_date = dateutil.parser.parse("june 25th 2022 18:00 UTC") 
names_ok = {"L1b-RadF": 'OR_L1b-RadF-M6C13_G16_s20221761800*',
    "ABI-L2-CMIPF" :'OR_ABI-L2-CMIPF-M6C13_G16_s20221761800*',
    "ABI-L2-MCMIPF": 'OR_ABI-L2-MCMIPF-M6_G16_s20221761800*',
    "ABI-L2-ACHTF": 'OR_ABI-L2-ACHTF-M6_G16_s20221761800*'
    }

def test_get_endpoint():
    #deberia ser mas extensivo este test capaz
    for ptype in goes.GOES16._PRODUCT_TYPES_PARSERS.keys():
        goes_obj = goes.GOES16(ptype)
        assert goes_obj.get_endpoint() == f"s3://noaa-goes16/{ptype}"

@mock.patch("s3fs.S3FileSystem.glob")
def test_fetch_goes():
    with mock.patch("io.BytesIO") as mock_io: #, return_value=[la query]
        goes_obj = goes.GOES16("L1b-RadF")
        goes_file = goes_obj.fetch("june 25th 2022 18")
        mock_io.assert_called_with(PATH_CHANNEL_13)

  
    
