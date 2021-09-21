# #%%
# from core import CloudClass, read_hdf

# path = 'data/CloudSat/2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf'
# #pruebo que la clase funcione
# y = CloudClass(path)

# #pruebo que levantar los datos funcione
# data = read_hdf(path)
# # y.plot_statistics()

# #%%
# # testando algunas funcionalidades

# # print(dir(y))

# #%%
# from core import ftp_cloudsat

# ## Ejemplo 1
# # ftp = ftp_cloudsat()
# # ftp.cd("2B-GEOPROF.P1_R05/2015/001/")
# # ftp.download("2015001225704_46177_CS_2B-GEOPROF_GRANULE_P1_R05_E06_F00.hdf")

# #%%
# from core import ftp_cloudsat

# path = "2B-GEOPROF.P1_R05/2015/001/2015001225704_46177_CS_2B-GEOPROF_GRANULE_P1_R05_E06_F00.hdf"
# ftp = ftp_cloudsat(path)

# %%
# StratoPy/
import sys
sys.path.append('../stratopy')
import cloudsat
# from . import StratoPy.cloudsat as cloudsat

filename = cloudsat.CloudClass('../data/CloudSat/2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf')

hdf_file = filename.read_hdf()
print(hdf_file)
print(filename.day_night())
print(filename.cut())