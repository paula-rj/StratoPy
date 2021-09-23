from stratopy.cloudsat import CloudClass, read_hdf


def test_read():
    path = "data/CloudSat/\
2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
    # pruebo que la clase funcione
    y = CloudClass(path).read_hdf()

    # pruebo que levantar los datos funcione
    data = read_hdf(path)

    return data, y


if __name__ == "__main__":
    test_read()


# path = "2B-GEOPROF.P1_R05/2015/001/\
#     2015001225704_46177_CS_2B-GEOPROF_GRANULE_P1_R05_E06_F00.hdf"
# ftp = ftp_cloudsat(path)

# filename = CloudClass(
#     "../data/CloudSat/\
#         2019003151948_67564_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"
# )

# hdf_file = filename.read_hdf()
# print(hdf_file)
# print(filename.day_night())
# print(filename.cut())
