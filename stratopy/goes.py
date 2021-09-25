from datetime import datetime

from netCDF4 import Dataset

import numpy as np

from pyorbital import astronomy

from pyspectral.near_infrared_reflectance import Calculator

from scipy import interpolate

#%%
class DayMicrophysics:
    def __init__(self, file_path, latlon_extent):
        self.file_path = file_path
        start_date = [
            self.band_path[0].split("s20", 1)[1].split("_", 1)[0]
            for band_path in file_path
        ]

        assert all(
            date == start_date[0] for date in start_date
        ), "Start date's from all files should be the same."

        # guarda desde el nivel L1 o L2
        # file_name = self.file_path.split("OR_ABI-")[1]
        self.julian_date = start_date[0][:5]
        self.sam_date = (
            datetime.strptime(self.julian_date, "%y%j")
            .date()
            .strftime("%d-%m-%y")
        )
        self.utc_hour = start_date[5:9]

    def __repr__(self):
        return f"GOES obj. Date: {self.sam_date}; {self.utc_hour} UTC "

    def recorte(
        self, filas=1440, columnas=1440, x0=-555469.8930323641, y0=0.0
    ):

        # lat =  0. -> y0
        # lon = -80. -> x0
        """
        Funcion que recorta una imagen tipo CMI de GOES.
        Parameters
        ----------
        data_path: str.
        Direccion de los datos GOES.
        filas: int.
        Cantidad de filas de pixeles (largo) que tendrá la imagen recortada
        columnas: int.
        Cantidad de columnas de pixeles (ancho) que tendrá la imagen recortada
        x0: float.
        Coordenada x en sistema geoestacionario GOES del limite superior
        izquierdo en m.
        y0: float.
        Coordenada y en sistema geoestacionario GOES del limite superior
        izquierdo en m.

        Returns
        -------
        im_rec: matriz con los elementos del recorte

        """
        psize = 2000
        N = 5424  # esc da 1
        esc = 1  # Fijate pau que es esto!!
        data = Dataset(self.file_path)  # Abro el archivo netcdf
        metadato = data.variables  # Extraigo todas las variables
        banda = metadato["band_id"][:].data[0]  # Extraigo el nro de banda
        # Extraigo la imagen y la guardo en un array de np
        image = np.array(metadato["CMI"][:].data)

        if int(banda) == 3:
            x = range(0, 10848)
            y = range(0, 10848)
            f = interpolate.interp2d(x, y, image, kind="cubic")
            xnew = np.arange(x[0], x[-1], (x[1] - x[0]) / esc)
            ynew = np.arange(y[0], y[-1], (y[1] - y[0]) / esc)
            image = f(xnew, ynew)

        img_extentr = [
            x0,
            x0 + columnas * psize,
            y0 - filas * psize,
            y0,
        ]  # tamaño del recorte en proyeccion goes
        print("extent rec en proyeccion goes:", img_extentr)

        esc = int(N / image.shape[0])
        Nx = int(columnas / esc)  # numero de puntos del recorte en x
        Ny = int(filas / esc)  # numero de puntos del recorte en x
        f0 = int(
            (-y0 / psize + N / 2 - 1.5) / esc
        )  # fila del angulo superior izquierdo
        # columna del angulo superior izquierdo
        c0 = int((x0 / psize + N / 2 + 0.5) / esc)
        f1 = int(f0 + Ny)  # fila del angulo inferior derecho
        c1 = int(c0 + Nx)  # columna del angulo inferior derecho
        print("coordenadas filas, col: ", f0, c0, f1, c1)

        im_rec = image[f0:f1, c0:c1]
        return im_rec

    def solar_7(self, ch7, ch13, latlon_extent):
        """ "
        Función que realiza la corrección según ángulo
        del zenith para la banda 7.
        Esta corrección es necesaria para imagenes de día
        Parameters
        ----------
        ch7: matriz (recortada) del canal 7
        ch13: matriz (recortada) del canal 13
        latlon_extent: list
        Lista [x1,y1,x2,y2] de los bordes de la imagen
        en latitud, longitud donde
            x1=longitud de más al oeste
            y1=latitud de más al sur (punto y inferior)
            x2 = longitud de más al este
            y2=latitud de más al norte (punto y superior)

        Returns
        -------
        data2b: matriz con el cálculo de zenith pixel a pixel
        """
        # Calculo del ángulo del sol para banda 7
        # NOTAR que esto está mal. Está calulando una latitud
        # y longitud equiespaciadas.
        # Tengo el codigo para hacerlo bien, ya lo voy a subir.
        lat = np.linspace(
            self.latlon_extent[3], self.latlon_extent[1], ch7.shape[0]
        )
        lon = np.linspace(
            self.latlon_extent[0], self.latlon_extent[2], ch7.shape[1]
        )
        print(lat.shape)
        print(lon.shape)

        zenith = np.zeros((ch7.shape[0], ch7.shape[1]))
        # Calculate the solar zenith angle
        utc_time = datetime(2019, 1, 2, 18, 00)
        for x in range(len(lat)):
            for y in range(len(lon)):
                zenith[x, y] = astronomy.sun_zenith_angle(
                    utc_time, lon[y], lat[x]
                )
        refl39 = Calculator(
            platform_name="GOES-16", instrument="abi", band="ch7"
        )
        data2b = refl39.reflectance_from_tbs(zenith, ch7, ch13)
        return data2b

    def day_microphysicsRGB(self, rec03, rec07, rec13):
        """
        Función que arma una imagen RGB que representa microfísica
        de día según la guía de la pagina de GOES.

        Parameters
        ----------
        rec03: numpy array
        imágen correctamente procesada de la banda 3
        rec07b: numpy array
        imágen correctamente procesada de la banda 7
        rec13: numpy array
        imágen correctamente procesada de la banda 13

        Returns
        -------
        RGB: numpy array
        Imagen RGB de microfísica de día
        """

        # Correccion del zenith
        lat = np.linspace(
            self.latlon_extent[3], self.latlon_extent[1], rec07.shape[0]
        )
        lon = np.linspace(
            self.latlon_extent[0], self.latlon_extent[2], rec07.shape[1]
        )
        zenith = np.zeros((rec07.shape[0], rec07.shape[1]))
        # Calculate the solar zenith angle
        utc_time = datetime(2019, 1, 2, 18, 00)
        for x in range(len(lat)):
            for y in range(len(lon)):
                zenith[x, y] = astronomy.sun_zenith_angle(
                    utc_time, lon[y], lat[x]
                )
        # refl39 = Calculator(
        #     platform_name="GOES-16", instrument="abi", band="ch7"
        # )
        # data07b = refl39.reflectance_from_tbs(zenith, ch7, ch13)

        R = rec03  # banda3
        G = rec07  # banda7 con corrección zenith
        B = rec13  # banda13

        # Minimuns and Maximuns
        Rmin = 0
        Rmax = 1

        Gmin = 0
        Gmax = 0.6

        Bmin = 203
        Bmax = 323

        # Choose the gamma -> STANDARIZADAS
        gamma_R = 1
        gamma_G = 2.5
        gamma_B = 1

        # Normalize the data
        R = ((R - Rmin) / (Rmax - Rmin)) ** (1 / gamma_R)
        G = ((G - Gmin) / (Gmax - Gmin)) ** (1 / gamma_G)
        B = ((B - Bmin) / (Bmax - Bmin)) ** (1 / gamma_B)

        # Normalizamos (matplotlib lo normaliza de todas formas)
        RR = np.copy(R)
        BB = np.copy(B)
        GG = np.copy(G)

        RR[RR < 0] = 0.0
        RR[RR > 1] = 1.0
        BB[BB < 0] = 0.0
        BB[BB > 1] = 1.0
        GG[GG < 0] = 0.0
        GG[GG > 1] = 1.0

        # Create the RGB
        RGB = np.stack([R, G, B], axis=2)
        # el axis está para que el shape sea fil col dim y no dim col fil
        RRGB = np.stack([RR, GG, BB], axis=2)
        print(RGB.shape)
        return RRGB
#%% 