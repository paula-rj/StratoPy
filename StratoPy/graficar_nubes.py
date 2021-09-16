#%%


def plot_cloud(path, ROI=range(12346, 12446), var="CloudLayerType", *args, **kwargs):
    from pyhdf.SD import SD, SDC
    from pyhdf.HDF import HDF, HC
    from pyhdf.VS import VS
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import numpy as np

    # metadata
    hdf_file = HDF(path, HC.READ)
    vs = hdf_file.vstart()
    lat = vs.attach("Latitude", write=0)[:]
    lon = vs.attach("Longitude", write=0)[:]
    latitude = np.array(lat).flatten()
    longitude = np.array(lon).flatten()

    file = SD(path, SDC.READ)
    data = file.select(var)[:]

    if ROI == None:
        plot_data = data.T
    else:
        plot_data = data[ROI, :].T

    print(plot_data.shape)
    # colors = ['m','r','orange','y','lime','skyblue','blue','indigo','white']
    colors = ["black", "indigo", "blue", "skyblue", "lime", "y", "orange", "r", "m"]
    # labels = ['Deep', 'Ns', 'Cu', 'Sc', 'St', 'Ac', 'As', 'High', 'Missing']
    labels = ["Missing", "Ci", "As", "Ac", "St", "Sc", "Cu", "Ns", "DC"]
    cmap = ListedColormap(colors)
    ax = plt.subplot(111)
    psm = ax.imshow(
        plot_data,
        origin="lower",
        cmap=cmap,
        aspect="auto",
        vmin=0,
        vmax=10,
        extent=[0, plot_data.shape[1], 0, 9],
        interpolation="none",
        *args,
        *kwargs,
    )

    cb = plt.colorbar(psm, orientation="horizontal", ax=ax)
    loc = np.arange(0.5, len(labels) + 1, 10 / 9)
    cb.set_ticks(loc)
    cb.set_ticklabels(labels)
    ax.set_ylabel("Layer")
    ax.set_xlabel("Latitude")
    nticks = 5
    ax.set_xticks([plot_data.shape[1] * i / nticks for i in range(nticks)])
    ax.set_xticklabels(
        [f"{latitude[int(i * plot_data.shape[1] / nticks)]:.2f}" for i in range(nticks)]
    )
    ax.set_yticks(np.arange(0, 10, 1))
    plt.grid(axis="y")
    return psm


# test

import matplotlib.pyplot as plt

files = [
    "2019002175851_67551",
    "2019003052836_67558",
    "2019003151948_67564",
    "2019003165820_67565",
    "2019003183652_67566",
]

file_to_plot = files[3]

path = f"data/CloudSat/{file_to_plot}_CS_2B-CLDCLASS_GRANULE_P1_R05_E08_F03.hdf"

plt.figure(figsize=(7, 5))
plot_cloud(path, ROI=range(15000, 25000), var="CloudLayerType")
plt.show()

# %%
