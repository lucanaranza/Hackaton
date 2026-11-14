"""Orizzonte geografico lunare: contratto JSON per il motore effemeridi."""
from contextlib import ExitStack
from pathlib import Path

import numpy as np
import rasterio
from pyproj import CRS, Geod, Transformer
from rasterio.windows import Window
from scipy.ndimage import map_coordinates

RADIUS_M = 1_737_400.0
LUNAR_CRS = CRS.from_proj4(f"+proj=longlat +R={RADIUS_M} +no_defs")


class DEMSampler:
    def __init__(self, source):
        self.source = source
        if source.count != 1 or source.crs is None:
            raise ValueError("Serve un DEM monobanda con CRS lunare.")
        crs = CRS.from_wkt(source.crs.to_wkt())
        if not (np.isclose(crs.ellipsoid.semi_major_metre, RADIUS_M)
                and np.isclose(crs.ellipsoid.semi_minor_metre, RADIUS_M)):
            raise ValueError("Il DEM deve usare la sfera lunare di raggio 1737400 m.")
        self.to_xy = Transformer.from_crs(LUNAR_CRS, crs, always_xy=True)
        self.data = self._read() if source.width * source.height <= 20_000_000 else None

    def _read(self, window=None):
        src = self.source
        data = src.read(1, window=window, masked=True).astype("float64").filled(np.nan)
        data = data * src.scales[0] + src.offsets[0]
        data[~np.isfinite(data)] = np.nan
        return data

    def sample(self, lon, lat):
        x, y = self.to_xy.transform(lon, lat)
        inverse = ~self.source.transform
        col = inverse.a*np.asarray(x) + inverse.b*np.asarray(y) + inverse.c
        row = inverse.d*np.asarray(x) + inverse.e*np.asarray(y) + inverse.f
        # Rasterio riferisce la trasformazione all'angolo; scipy ai centri.
        row, col = np.atleast_1d(row) - 0.5, np.atleast_1d(col) - 0.5
        result = np.full(row.shape, np.nan)
        inside = (np.isfinite(row) & np.isfinite(col) & (row >= 0) & (col >= 0)
                  & (row <= self.source.height-1) & (col <= self.source.width-1))
        indices = np.flatnonzero(inside)
        # Finestre piccole anche per mosaici enormi: niente lettura integrale.
        for start in range(0, indices.size, 256):
            idx = indices[start:start+256]
            r, c = row[idx], col[idx]
            if self.data is not None:
                data, r0, c0 = self.data, 0, 0
            else:
                r0, c0 = int(np.floor(r.min())), int(np.floor(c.min()))
                r1 = min(self.source.height, int(np.floor(r.max()))+2)
                c1 = min(self.source.width, int(np.floor(c.max()))+2)
                data = self._read(Window(c0, r0, c1-c0, r1-r0))
            result[idx] = map_coordinates(data, [r-r0, c-c0], order=1,
                                          mode="constant", cval=np.nan, prefilter=False)
        return result


def elevation_angles(heights, ground_m, observer_height_m, distances_m):
    """Approssimazione prescritta nel README, con curvatura lunare."""
    d = np.asarray(distances_m, dtype=float)
    return np.degrees(np.arctan2(
        np.asarray(heights) - ground_m - observer_height_m - d*d/(2*RADIUS_M), d))


def calculate_horizon(input_path, lat=None, lon=None, name=None,
                      observer_height_m=2.0, near_distance_m=10_000.0,
                      step_m=5.0, far_dem=None, max_distance_m=200_000.0,
                      far_step_m=100.0):
    """Restituisce 360 massimi sui campioni disponibili e metadati di copertura.

    Il DEM lontano copre anche i buchi del DEM vicino. Un profilo incompleto
    e un limite inferiore dell'orizzonte campionato, non una previsione sicura.
    Nessun campione valido in una direzione causa un errore, non uno zero.
    """
    for value in (step_m, far_step_m, near_distance_m, max_distance_m):
        if not np.isfinite(value) or value <= 0:
            raise ValueError("Passi e distanze devono essere positivi e finiti.")
    if step_m > near_distance_m or max_distance_m < near_distance_m:
        raise ValueError("Servono passo <= distanza vicina <= distanza massima.")
    if not np.isfinite(observer_height_m) or observer_height_m < 0:
        raise ValueError("L'altezza osservatore deve essere non negativa e finita.")
    if (lat is None) != (lon is None):
        raise ValueError("Specificare insieme latitudine e longitudine.")
    with ExitStack() as stack:
        src = stack.enter_context(rasterio.open(input_path))
        near = DEMSampler(src)
        far = DEMSampler(stack.enter_context(rasterio.open(far_dem))) if far_dem else None
        if lat is None:
            x, y = src.transform * (src.width/2, src.height/2)
            lon, lat = Transformer.from_crs(src.crs, LUNAR_CRS, always_xy=True).transform(x, y)
        if not (np.isfinite(lat) and np.isfinite(lon) and -90 < lat < 90 and -180 <= lon <= 180):
            raise ValueError("Coordinate non valide; al polo esatto l'azimut nord non e univoco.")
        ground = float(near.sample([lon], [lat])[0])
        if not np.isfinite(ground):
            raise ValueError("Il sito non ha una quota valida nel DEM vicino.")
        distances = np.arange(step_m, near_distance_m, step_m)
        distances = np.append(distances, near_distance_m)
        if far is not None and max_distance_m > near_distance_m:
            distances = np.concatenate((distances,
                np.arange(near_distance_m+far_step_m, max_distance_m, far_step_m),
                [max_distance_m]))
        geod = Geod(a=RADIUS_M, b=RADIUS_M)
        horizons, coverage = [], []
        for az in range(360):
            lons, lats, _ = geod.fwd(np.full(distances.size, lon), np.full(distances.size, lat),
                                      np.full(distances.size, az), distances)
            heights = np.full(distances.size, np.nan)
            local = distances <= near_distance_m
            heights[local] = near.sample(lons[local], lats[local])
            missing = ~np.isfinite(heights)
            if far is not None and missing.any():
                heights[missing] = far.sample(lons[missing], lats[missing])
            valid = np.isfinite(heights)
            if not valid.any():
                raise ValueError(f"Nessun terreno disponibile all'azimut {az}; spostare il sito o fornire un DEM piu ampio.")
            angles = elevation_angles(heights, ground, observer_height_m, distances)
            horizons.append(float(np.nanmax(angles)))
            coverage.append({"azimut": az, "campioni_validi": int(valid.sum()),
                             "campioni_totali": int(distances.size),
                             "distanza_valida_massima_m": float(distances[valid].max()),
                             "copertura_completa": bool(valid.all())})
    complete = far is not None and all(c["copertura_completa"] for c in coverage)
    warnings = []
    if far is None:
        warnings.append("DEM lontano assente: rilievi oltre il DEM locale non valutati.")
    if not all(c["copertura_completa"] for c in coverage):
        warnings.append("Copertura incompleta: campioni fuori raster o NoData; orizzonte potenzialmente sottostimato.")
    return {"nome": name or Path(input_path).stem, "lat": float(lat), "lon": float(lon),
            "orizzonte": horizons,
            "metadati": {"quota_sito_m": ground, "altezza_osservatore_m": observer_height_m,
                "raggio_lunare_m": RADIUS_M, "frame": "MOON_ME_DE421 (da verificare per DEM esterni)",
                "azimut": "0=Nord geografico, 90=Est, 180=Sud, 270=Ovest",
                "dem_vicino": str(input_path), "dem_lontano": str(far_dem) if far_dem else None,
                "passo_vicino_m": step_m, "passo_lontano_m": far_step_m,
                "distanza_vicina_m": near_distance_m, "distanza_massima_richiesta_m": max_distance_m,
                "distanza_massima_campionata_m": float(distances[-1]),
                "copertura_completa_entro_distanza_richiesta": complete,
                "copertura_per_azimut": coverage, "avvertenze": warnings}}


def plot_horizon(input_path, profile, output_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    from rasterio.enums import Resampling

    with rasterio.open(input_path) as src:
        factor = max(1, max(src.shape)/1000)
        image = src.read(1, out_shape=(max(1, int(src.height/factor)), max(1, int(src.width/factor))),
                         masked=True, resampling=Resampling.average)
        image = image * src.scales[0] + src.offsets[0]
        x, y = Transformer.from_crs(LUNAR_CRS, src.crs, always_xy=True).transform(profile["lon"], profile["lat"])
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        raster = axes[0].imshow(image, extent=(src.bounds.left, src.bounds.right,
                                              src.bounds.bottom, src.bounds.top), cmap="terrain")
        axes[0].plot(x, y, "r+", markersize=12, label="Osservatore")
        axes[0].set(xlabel="X griglia [m]", ylabel="Y griglia [m]", title=profile["nome"])
        axes[0].xaxis.set_major_locator(MaxNLocator(4))
        axes[0].legend()
        fig.colorbar(raster, ax=axes[0], label="Quota [m]")
        axes[1].plot(np.arange(361), profile["orizzonte"] + profile["orizzonte"][:1])
        axes[1].set(xlabel="Azimut geografico [gradi]", ylabel="Elevazione [gradi]",
                    title="Orizzonte campionato" + (" (copertura parziale)" if not profile["metadati"]["copertura_completa_entro_distanza_richiesta"] else ""),
                    xlim=(0, 360), xticks=[0, 90, 180, 270, 360])
        axes[1].grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(output_path, dpi=140)
        plt.close(fig)
