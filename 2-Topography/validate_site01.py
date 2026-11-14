"""Controllo ripetibile dei quattro prodotti Site01 e del JSON dell'orizzonte.

Eseguire prima script.py --output 3-Topography/output/test_site01.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Geod, Transformer

from horizon import LUNAR_CRS, RADIUS_M
from script import statistics, terrain_derivatives


def validate():
    base = Path(__file__).resolve().parent
    output = base / "output/test_site01"
    profile = json.loads((output / "horizon.json").read_text(encoding="utf-8"))
    paths = {suffix: list((base / "dati_topografia").rglob(f"Site01_final_adj_5mpp_{suffix}.tif"))
             for suffix in ("surf", "slp", "toterr", "ldec")}
    for suffix, matches in paths.items():
        if len(matches) != 1:
            raise ValueError(f"Serve un solo file Site01 {suffix}: trovati {len(matches)}")
    arrays, report = {}, {"files": {}, "checks": []}
    with rasterio.open(paths["surf"][0]) as src:
        shape, transform, crs = src.shape, src.transform, src.crs
        dx, dy = src.res
    for suffix, matches in paths.items():
        with rasterio.open(matches[0]) as src:
            assert src.count == 1 and src.shape == shape, f"Dimensioni incompatibili: {suffix}"
            assert src.crs == crs and src.transform == transform, f"Griglie non allineate: {suffix}"
            values = src.read(1, masked=True).astype("float32").filled(np.nan)
            values = values * src.scales[0] + src.offsets[0]
            values[~np.isfinite(values)] = np.nan
            arrays[suffix] = values
            report["files"][suffix] = {"path": str(matches[0]), "shape": list(shape),
                "resolution_m": list(src.res), "statistics": statistics(values),
                "missing_pct": 100 * np.count_nonzero(~np.isfinite(values))/values.size}
    assert dx == dy == 5, "Risoluzione Site01 inattesa"
    report["checks"].append("Tutti i quattro raster sono leggibili e allineati a 5 m/pixel")
    official_slope, error, count = arrays["slp"], arrays["toterr"], arrays["ldec"]
    assert np.all((official_slope[np.isfinite(official_slope)] >= 0)
                  & (official_slope[np.isfinite(official_slope)] <= 90))
    assert np.all(error[np.isfinite(error)] >= 0)
    valid_count = count[np.isfinite(count)]
    assert np.all(valid_count >= 0) and np.allclose(valid_count, np.round(valid_count))
    report["files"]["ldec"]["zero_count_pct_of_valid"] = float(100*np.count_nonzero(valid_count == 0)/valid_count.size)
    report["checks"].append("Pendenze in [0,90], incertezze non negative, conteggi interi non negativi")
    calculated, _ = terrain_derivatives(arrays["surf"], dx, dy)
    valid = np.isfinite(calculated) & np.isfinite(official_slope)
    difference = calculated[valid] - official_slope[valid]
    report["slope_comparison"] = {"pixels": int(valid.sum()),
        "mean_difference_deg": float(difference.mean(dtype=np.float64)),
        "mean_absolute_difference_deg": float(np.abs(difference).mean(dtype=np.float64)),
        "p95_absolute_difference_deg": float(np.percentile(np.abs(difference), 95)),
        "note": "Differenze possibili per metodo/baseline: lo script usa differenze centrate, non sostituisce la mappa ufficiale."}

    horizon = np.asarray(profile["orizzonte"], dtype=float)
    assert horizon.shape == (360,) and np.isfinite(horizon).all()
    # Percorso indipendente da scipy/map_coordinates: interpolazione esplicita
    # dei quattro centri pixel e massimo angolare, in otto direzioni.
    z = arrays["surf"].astype("float64")
    converter = Transformer.from_crs(LUNAR_CRS, crs, always_xy=True)
    inverse = ~transform

    def manual_sample(lons, lats):
        x, y = converter.transform(lons, lats)
        c = inverse.a*np.asarray(x)+inverse.b*np.asarray(y)+inverse.c-.5
        r = inverse.d*np.asarray(x)+inverse.e*np.asarray(y)+inverse.f-.5
        result = np.full(np.shape(r), np.nan)
        valid = (r >= 0) & (c >= 0) & (r < shape[0]-1) & (c < shape[1]-1)
        rr, cc = r[valid], c[valid]
        ri, ci = np.floor(rr).astype(int), np.floor(cc).astype(int)
        wr, wc = rr-ri, cc-ci
        result[valid] = ((1-wr)*(1-wc)*z[ri, ci] + wr*(1-wc)*z[ri+1, ci]
                         + (1-wr)*wc*z[ri, ci+1] + wr*wc*z[ri+1, ci+1])
        return result

    meta = profile["metadati"]
    assert meta["dem_lontano"] is None, "Questo controllo indipendente riguarda solo il DEM vicino"
    d = np.append(np.arange(meta["passo_vicino_m"], meta["distanza_vicina_m"], meta["passo_vicino_m"]), meta["distanza_vicina_m"])
    ground = manual_sample(np.array([profile["lon"]]), np.array([profile["lat"]]))[0]
    assert abs(ground-meta["quota_sito_m"]) < 1e-7
    geod = Geod(a=RADIUS_M, b=RADIUS_M)
    differences = []
    for az in range(0, 360, 45):
        lon, lat, _ = geod.fwd(np.full(d.size, profile["lon"]), np.full(d.size, profile["lat"]),
                                np.full(d.size, az), d)
        h = manual_sample(lon, lat)
        angles = np.degrees(np.arctan((h-ground-meta["altezza_osservatore_m"]-d*d/(2*RADIUS_M))/d))
        difference = abs(float(np.nanmax(angles))-horizon[az])
        assert difference < 1e-7, f"Orizzonte non coerente all'azimut {az}"
        differences.append(difference)
    report["checks"].append("360 valori finiti; otto azimut verificati con interpolazione bilineare indipendente")
    spec = importlib.util.spec_from_file_location("effemeridi", base.parent / "2-Ephemerids/effemeridi.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    np.testing.assert_allclose(module._maschera(profile["orizzonte"], np.arange(360)), horizon)
    report["checks"].append("JSON compatibile con la funzione _maschera del motore effemeridi")
    coverage = meta["copertura_per_azimut"]
    report["horizon"] = {"min_deg": float(horizon.min()), "max_deg": float(horizon.max()),
        "ground_m": ground, "independent_max_difference_deg": max(differences),
        "directions_with_complete_near_coverage": sum(c["copertura_completa"] for c in coverage),
        "warnings": meta["avvertenze"]}
    report["note"] = "Lo script usa surf per l'orizzonte; slp, toterr e ldec sono controllati qui come prodotti di pendenza e qualita. Non costituiscono un DEM lontano."
    report["status"] = "PASS"
    path = output / "validation.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    validate()
