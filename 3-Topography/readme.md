#MAIN REPO FOR TERRAIN ANALYSIS SCRIPT#

1. Dove prendere i dati (NASA PGDA, DEM LOLA 5 m/pixel del polo sud)
- Siti singoli: https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/
Ci sono Site01 Connecting ridge, Site04 Shackleton rim, Site06 Nobile rim 1, Site07 Peak near Shackleton, Site11 de Gerlache rim, Site20 Leibnitz beta plateau, Site23 Malapert massif e altri.
- Mosaico completo 87°–90°S: https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/87S/
- Spiegazione dei file: https://core2.gsfc.nasa.gov/PGDA/LOLA_5mpp/README
- Per i siti non polari (Apollo ecc.): DEM globale LOLA su https://imbrium.mit.edu/, oppure ritagli da Quickmap.
2. Quale file usare
In ogni cartella di sito prendete il file *_surf.tif: è l’altezza del terreno in metri, con i buchi già riempiti. Gli altri file sono extra: _slp è la pendenza, _toterr l’incertezza, _ldec il numero di misure laser.

3. Formato
- GeoTIFF a 5 m/pixel, coordinate X/Y in metri, proiezione stereografica polare sud.
- Sistema di riferimento MOON_ME (DE421), lo stesso che usiamo noi per le effemeridi. Quindi coordinate coerenti, nessuna conversione strana.
- Si apre con rasterio (python -m pip install rasterio pyproj scipy).
4. Cosa ci dovete restituire: il “contratto”
Per ogni sito, una lista di 360 numeri:
- elemento i = elevazione dell’orizzonte in gradi nella direzione di azimut i;
- azimut geografico: 0 = Nord, 90 = Est, 180 = Sud, 270 = Ovest. Attenzione: al polo sud “Nord” vuol dire “lontano dal polo”;
- salvatela in JSON, es. {"nome": "Shackleton rim", "lat": ..., "lon": ..., "orizzonte": [360 valori]}.
La funzione valuta_sito(..., orizzonte=lista) in 2-Ephemerids/effemeridi.py la usa direttamente.

5. Algoritmo dell’orizzonte (in breve)
Per ogni azimut da 0 a 359:
1. si traccia un raggio dal sito verso quella direzione, campionando punti ogni N metri;
2. per ogni punto: altezza del terreno h, distanza d;
3. angolo di elevazione = atan((h - h_sito - d²/(2R)) / d), con R = 1.737.400 m. Il termine d²/2R è la curvatura lunare: le cose lontane “scendono” sotto l’orizzonte;
4. l’orizzonte in quella direzione è l’angolo massimo trovato lungo il raggio.
Consiglio: aggiungete un paio di metri a h_sito, per l’altezza del lander o dei pannelli.

Per non sbagliare gli azimut al polo, calcolate i punti lungo il raggio in lat/lon con pyproj.Geod e poi convertiteli nelle coordinate del DEM:
python
import rasterio
from pyproj import Geod, Transformer

src = rasterio.open("Site04_..._surf.tif")
dem = src.read(1)
luna = Geod(a=1737400, b=1737400)                         # Luna sferica
to_xy = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", src.crs, always_xy=True)

# punto a distanza d (m) dal sito, in direzione azimut az (gradi da Nord):
lon2, lat2, _ = luna.fwd(lon_sito, lat_sito, az, d)
x, y = to_xy.transform(lon2, lat2)
riga, col = src.index(x, y)        # pixel del DEM -> dem[riga, col] = altezza
(Per velocità, meglio campionare tanti punti insieme con scipy.ndimage.map_coordinates.)

6. ⚠️ Trappola importante: il terreno lontano
Al polo il Sole sta a 1–2° sopra l’orizzonte, quindi una montagna a decine o centinaia di km può fare ombra. Il DEM di un singolo sito copre solo circa 20×20 km, che non basta. Soluzione:
- vicino (fino a ~10 km): DEM a 5 m del sito;
- lontano (fino a 100–200 km): mosaico 87°S o un DEM polare LOLA a risoluzione più bassa.
Si prende il massimo tra i due.

7. Regole pratiche
- I .tif non vanno su GitHub, perché sono pesanti: aggiungete *.tif al .gitignore e condivideteli via Drive. Su GitHub mettete solo i JSON dell’orizzonte, che sono piccoli.
- Partite da un solo sito (Shackleton rim): aprite il DEM, disegnate la mappa con matplotlib, poi calcolate l’orizzonte. Quando funziona, estendete agli altri.
- Test rapido: confrontate il vostro orizzonte con quello che si vede su Quickmap o Moon Trek per lo stesso punto.