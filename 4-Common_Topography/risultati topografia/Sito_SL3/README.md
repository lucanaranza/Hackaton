# Sito_SL3

Analisi del centro del DEM; osservatore a 2 m.

| Metrica | Valore |
| --- | --- |
| Centro (lat, lon lunari) | -89.032416, -101.999287 gradi |
| Quote min / max | -1169.76 / 1693.09 m |
| Pendenza media calcolata | 14.70 gradi |
| Area con pendenza <=10 gradi | 91.66 km2 (22.94%) |
| Incertezza verticale media fornita | 0.454 m |
| Pixel con LDEC zero | 94.23% |
| Orizzonte minimo / massimo | -9.683 / 10.649 gradi |
| Celle | 40000 |
| Verifica | PASS |

## Risultati

- [Orizzonte a 360 valori](horizon.json)
- [Mappa e profilo](horizon.png)
- [Statistiche complete](summary.json)
- [Celle topografiche](site_cells.csv)
- [Rapporto di verifica e qualita](validation.json)

## Interpretazione e limiti

La pendenza descrive tutto il DEM, mentre il profilo orizzonte riguarda soltanto il suo centro.
Il centro del raster non e necessariamente il punto di atterraggio associato al nome del sito.
Le percentuali sono riferite ai pixel con pendenza calcolabile; le aree sono proiettate.
Le celle sono 100 x 100 m, piu piccole ai bordi quando necessario.
LDEC zero non e NoData: il DEM contiene anche terreno interpolato.
Il filtro di pendenza non certifica un sito sicuro e non impone aree connesse.
Non sono stati calcolati luce, visibilita terrestre, temperatura o presenza di ghiaccio.
Output compatti: nessun GeoTIFF derivato, per contenere lo spazio su disco.
- DEM lontano assente: rilievi oltre il DEM locale non valutati.
- Copertura incompleta: campioni fuori raster o NoData; orizzonte potenzialmente sottostimato.
