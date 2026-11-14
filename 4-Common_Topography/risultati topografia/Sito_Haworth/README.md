# Sito_Haworth

Analisi del centro del DEM; osservatore a 2 m.

| Metrica | Valore |
| --- | --- |
| Centro (lat, lon lunari) | -86.763942, -22.777024 gradi |
| Quote min / max | -1642.90 / 2842.21 m |
| Pendenza media calcolata | 10.84 gradi |
| Area con pendenza <=10 gradi | 423.37 km2 (47.71%) |
| Incertezza verticale media fornita | 0.403 m |
| Pixel con LDEC zero | 89.43% |
| Orizzonte minimo / massimo | -0.040 / 5.932 gradi |
| Celle | 88804 |
| Verifica | PASS_WITH_NOTES |

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
- LDEC contiene 0.956% di valori frazionari: non interpretare come conteggio grezzo intero. Valori originali preservati.
