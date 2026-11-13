"""Test di base: posizione di Sole e Terra viste dal sito di Apollo 11
al momento dell'allunaggio (20 luglio 1969, 20:17 UTC).

Risultato atteso: Sole basso (~10-11 gradi), Terra alta nel cielo.
Al primo avvio scarica i file delle effemeridi (~17 MB) in questa cartella.
"""
from skyfield.api import load, PlanetaryConstants

# Scala dei tempi e posizioni di Sole, Terra e Luna (file JPL DE421)
ts = load.timescale()
eph = load('de421.bsp')
sun, earth, moon = eph['sun'], eph['earth'], eph['moon']

# Orientamento e rotazione della Luna (librazione inclusa)
pc = PlanetaryConstants()
pc.read_text(load('moon_080317.tf'))
pc.read_text(load('pck00008.tpc'))
pc.read_binary(load('moon_pa_de421_1900-2050.bpc'))
frame = pc.build_frame_named('MOON_ME_DE421')

# Sito: Apollo 11 (lat 0.674 N, lon 23.473 E)
sito = moon + pc.build_latlon_degrees(frame, 0.674, 23.473)

# Data: allunaggio Apollo 11
t = ts.utc(1969, 7, 20, 20, 17)

for nome, corpo in [('Sole', sun), ('Terra', earth)]:
    alt, az, dist = sito.at(t).observe(corpo).apparent().altaz()
    print(f"{nome}: elevazione {alt.degrees:.1f} gradi, azimut {az.degrees:.1f} gradi")
