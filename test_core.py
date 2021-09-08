from core import CloudClass

y = CloudClass(
    'data/CloudSat/2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf'
)

data = y.read()
print(y.plot_statistics())
