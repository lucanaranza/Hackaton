# Sito_NPB

Analisi del centro del DEM; osservatore a 2 m.

| Metrica | Valore |
| --- | --- |
| Centro (lat, lon lunari) | -83.904646, 89.535450 gradi |
| Quote min / max | -3891.10 / -2859.21 m |
| Pendenza media calcolata | 5.25 gradi |
| Area con pendenza <=10 gradi | 338.47 km2 (84.70%) |
| Incertezza verticale media fornita | 1.088 m |
| Pixel con LDEC zero | 98.08% |
| Orizzonte minimo / massimo | 0.068 / 2.780 gradi |
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
