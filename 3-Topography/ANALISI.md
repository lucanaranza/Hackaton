# Prima interpretazione dei dati topografici

## Aggiornamento: contratto orizzonte per le effemeridi

Lo script ora genera per default `output/horizon.json`: i campi `nome`,
`lat`, `lon`, `orizzonte` rispettano il contratto in `readme.md`.
`orizzonte` contiene esattamente 360 numeri, indicizzati per azimut geografico
0..359, con curvatura lunare e altezza osservatore predefinita di 2 m.
I raggi sono geodetiche sferiche calcolate con `pyproj.Geod`, convertite con
`Transformer(always_xy=True)` e campionate con interpolazione bilineare.
Il massimo puo essere negativo: non viene forzato artificialmente a zero.

```powershell
.venv/Scripts/python.exe 3-Topography/script.py --name "Connecting ridge"
# Altro sito: specificare il suo DEM e le sue coordinate effettive
python 3-Topography/script.py --input "percorso/Site04_surf.tif" --name "Shackleton rim"
# Aggiungere il terreno lontano fino a 200 km (quote nello stesso riferimento)
python 3-Topography/script.py --far-dem "percorso/mosaico.tif" --max-distance 200000 --far-step 100
# Conservare anche le metriche topografiche precedenti
python 3-Topography/script.py --mode all
```

Per un punto specifico, passare `--lat` e `--lon` all'interno del DEM.
Senza `--lat` e `--lon` si usa il centro del raster; il file
Site01 viene cercato anche nelle sottocartelle di `dati_topografia`.
`--step` imposta il passo vicino (default 5 m); `--near-distance` il raggio
vicino (default 10 km). `--observer-height` cambia l'altezza dell'osservatore.
`--output` consente cartelle distinte per siti diversi; altrimenti i risultati
dell'orizzonte precedente vengono sovrascritti.

`output/horizon.png` mostra DEM, posizione osservatore e profilo. `--no-plot`
disattiva il grafico. Il motore topografico e nel modulo `horizon.py`.

In `2-Ephemerids/effemeridi.py`, dopo aver caricato il JSON:

```python
profilo = json.loads(Path("3-Topography/output/horizon.json").read_text(encoding="utf-8"))
risultato = valuta_sito(profilo["lat"], profilo["lon"], inizio,
                       orizzonte=profilo["orizzonte"])
```

Controllare prima `metadati`: il campo
`copertura_completa_entro_distanza_richiesta` e falso se manca il DEM lontano
o se qualche campione e fuori dai raster/NoData. I massimi vengono calcolati
solo sul terreno disponibile, senza sostituire i buchi con quota zero.
La copertura per ciascun azimut e registrata nel JSON. Un profilo parziale
puo sottostimare le ostruzioni e sovrastimare luce e comunicazioni.
Con entrambi i DEM, quello lontano riempie anche i campioni mancanti vicini.
La copertura dichiarata riguarda i campioni discreti, non garantisce di
rilevare tutti i rilievi tra un campione e l'altro o oltre il raggio scelto.

Il confronto visivo esterno con Quickmap/Moon Trek resta da effettuare;
i test automatici verificano piani sintetici, azimut geografici, curvatura,
altezza osservatore, copertura e contributo del DEM lontano.

I risultati delle sezioni seguenti riguardano la modalita `--mode metrics`.

Il file `Site01_final_adj_5mpp_surf.tif` corrisponde al prodotto LDEM Site01
del [NASA GSFC / PGDA](https://pgda.gsfc.nasa.gov/products/78).
La documentazione identifica i valori come quote in metri e le coordinate
nel sistema lunare MOON_ME, riferito a DE421. Il GeoTIFF non dichiara
l'unita verticale: l'interpretazione in metri proviene dalla documentazione.
Il riferimento verticale va verificato prima di combinare altre mappe.
Quote negative non significano profondita sotto un livello del mare lunare.

## Risultati del file disponibile

| Metrica | Risultato |
| --- | --- |
| Dimensioni | 3200 x 3200 pixel, 10.240.000 quote |
| Passo della griglia | 5 x 5 m |
| Estensione proiettata | 16 x 16 km = 256 km2 |
| Centro della mappa | latitudine -89,463163°, longitudine -137,489553° |
| Quote mancanti | 0% |
| Quota minima / massima | -523,18 / 1959,50 m |
| Quota media / mediana | 1139,06 / 1200,25 m |
| Pendenza media / mediana | 12,60° / 12,29° |
| Pendenza al percentile 95 / massima | 22,81° / 64,59° |

Le pendenze sono calcolate con differenze centrate tra vicini opposti
(baseline 10 m) e distanze della griglia proiettata. Viene escluso il bordo
di un pixel, insieme alle celle prive dei vicini necessari: area con pendenza
calcolabile 255,6801 km2. Le aree sono approssimazioni nella proiezione.

| Filtro di pendenza | Area che passa | Percentuale dell'area con pendenza calcolabile |
| --- | --- | --- |
| <= 5° | 24,93 km2 | 9,75% |
| <= 10° | 93,12 km2 | 36,42% |
| <= 15° | 168,65 km2 | 65,96% |
| <= 20° | 225,17 km2 | 88,07% |

Le soglie sono esempi per il pannello filtri: vanno sostituite con i requisiti
del veicolo. Le aree sommate possono essere disconnesse; non equivalgono a
piazzole continue o a ellissi di atterraggio utilizzabili.

## Dati pronti per l'app

- `output/summary.json`: metadati, statistiche, soglie e prime dieci celle
  ordinate per frazione che passa il filtro, pendenza massima e dislivello.
- `output/terrain_metrics.tif`: tre bande georeferenziate: quota in metri,
  pendenza in gradi, orientamento della discesa in gradi orari dal nord
  della **griglia**. L'orientamento e indefinito sui pixel piatti.
- `output/slope_filter.tif`: 1 supera il filtro, 0 lo fallisce, 255 sconosciuto.
  Filtro predefinito: pendenza <= 10°.
- `output/site_cells.csv`: 25.600 celle da 100 x 100 m con centro lunare,
  quota media, pendenza media e massima, copertura dei dati, dislivello e
  percentuale di pixel che passa il filtro. Il denominatore e l'intera cella,
  inclusi eventuali dati mancanti.

Un esempio da confrontare nell'app e la cella centrata a latitudine
**-89,452586°**, longitudine **-146,549262°**: quota media 1623,56 m,
pendenza media 1,21°, massima 2,76°, dislivello 1,97 m su 100 x 100 m.
E la prima secondo l'ordinamento puramente topografico usato qui;
non e una raccomandazione di atterraggio.

Per la scheda sito usate quota e pendenza del pixel, e le statistiche della
cella per il contesto circostante. Un valore al centro della cella non
rappresenta tutta l'area. Il dislivello e max(quota)-min(quota), non una
misura di rugosita depurata dalla pendenza.

## Limiti e prossimi dati

La risoluzione di campionamento di 5 m non implica precisione di 5 m:
massi, crateri piccoli e dettagli sotto questa scala possono sfuggire.
Il prodotto e interpolato; per valutare la qualita servono anche le mappe
di errore e di risoluzione effettiva distribuite da PGDA.

L'orientamento rispetto al nord geografico differisce molto da quello di
griglia vicino al polo. Non usare direttamente questa banda con azimut
astronomici. Le coordinate esportate sono lunari, non EPSG:4326 terrestre:
una mappa dell'app deve usare la stessa proiezione o una conversione lunare.

Per illuminazione e comunicazioni servono effemeridi Sole/Terra alla data
selezionata, altezza di pannello/antenna e orizzonte topografico con curvatura
lunare. Un DEM di 16 km puo non includere rilievi lontani che occultano
l'orizzonte. Temperatura, ghiaccio e ombra permanente non si possono
assegnare da questa sola mappa. Lo score complessivo va introdotto dopo
aver aggiunto queste metriche, pesi e vincoli di missione.

## Esecuzione

Con Python e le dipendenze di `requirements.txt` installate:

```powershell
python 3-Topography/script.py --mode metrics --max-slope 10 --tile-size 100
python -m unittest discover -s 3-Topography -p "test_*.py"
```

I percorsi predefiniti sono relativi allo script. `--input` e `--output`
permettono di cambiarli. Rieseguire sovrascrive gli output con gli stessi nomi.
Lo script controlla il CRS lunare sferico di raggio 1.737.400 m e applica
maschere NoData, scale e offset della banda.
La gestione delle maschere segue la
[documentazione Rasterio](https://rasterio.readthedocs.io/en/stable/topics/masks.html).
