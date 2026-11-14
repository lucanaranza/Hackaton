"""
Motore delle effemeridi per la valutazione dei siti di atterraggio lunari.

Funzione principale:
    valuta_sito(lat, lon, inizio, giorni=30, passo_min=10, orizzonte=None)

Restituisce un dizionario (convertibile in JSON) con:
    - "serie":    istanti con elevazione/azimut di Sole e Terra
    - "eventi":   alba/tramonto del Sole, sorgere/tramonto della Terra
    - "metriche": ore di luce, ore di comunicazione, tempo al tramonto, ecc.

Convenzioni (da condividere con il team!):
    - Tempi in UTC, formato ISO 8601 (es. "2026-11-13T18:00:00Z")
    - Angoli in GRADI
    - Azimut misurato da NORD (0) verso EST (90), SUD (180), OVEST (270)
    - Latitudine positiva a nord, longitudine positiva a est
    - Orizzonte: lista di 360 elevazioni (gradi), una per ogni grado di
      azimut 0..359. Se None si usa l'orizzonte "liscio" (sfera, 0 gradi).
      La coppia Terreno fornira' l'orizzonte reale da LOLA.

Nota: Sole e Terra sono considerati "visibili" quando il loro CENTRO e' sopra
l'orizzonte (raggio apparente Sole ~0.27 gradi, Terra ~0.95 gradi).
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from skyfield.api import Loader, PlanetaryConstants

# I file delle effemeridi vengono salvati nella cartella principale del repo
# (sono esclusi da Git tramite .gitignore).
_CARTELLA_DATI = Path(__file__).resolve().parent.parent
_load = Loader(str(_CARTELLA_DATI), verbose=True)

_cache = {}


def _risorse():
    """Carica effemeridi e orientamento lunare una sola volta (cache)."""
    if not _cache:
        ts = _load.timescale()
        eph = _load('de421.bsp')
        pc = PlanetaryConstants()
        pc.read_text(_load('moon_080317.tf'))                 # Lunear reference frame
        pc.read_text(_load('pck00008.tpc'))                   # Planetary Constants Kernel (PCK) con orientamento della Luna
        pc.read_binary(_load('moon_pa_de421_1900-2050.bpc'))  # Lunar orientation data (PA = principal axes) per il periodo 1900-2050
        frame = pc.build_frame_named('MOON_ME_DE421')         # Build the lunar reference frame using the DE421 ephemeris - coerent with LOLA data
        _cache.update(ts=ts, eph=eph, pc=pc, frame=frame)
    return _cache


def _maschera(orizzonte, azimut):
    """Elevazione dell'orizzonte (gradi) nelle direzioni 'azimut'."""
    if orizzonte is None:
        return np.zeros_like(azimut)                          # If there is no horizon data, assume a flat horizon at 0 degrees elevation           
    oriz = np.asarray(orizzonte, dtype=float)                 # oriz is an array of 360 elevation values (one for each azimuth degree)      
    gradi = np.linspace(0, 360, len(oriz), endpoint=False)    # Create an array of azimuth values corresponding to the elevation values in 'oriz'
    return np.interp(azimut, gradi, oriz, period=360)         


def _trova_eventi(tempi, margine, nome_sorge, nome_tramonta):
    """Trova gli istanti in cui 'margine' (elevazione - orizzonte) cambia segno.
    Usa un'interpolazione lineare tra due campioni consecutivi: con un passo
    di 10 minuti l'errore e' di pochi minuti, ampiamente sufficiente.
    """
    eventi = []
    for i in range(len(margine) - 1):                      # Loop through the 'margine' array to find sign changes between consecutive samples
        a, b = margine[i], margine[i + 1]
        if (a <= 0 < b) or (a > 0 >= b):
            frazione = a / (a - b)                         # interpolate to find the fraction of the interval where the sign change occurs
            t = tempi[i] + (tempi[i + 1] - tempi[i]) * frazione
            tipo = nome_sorge if b > a else nome_tramonta
            eventi.append({"tipo": tipo, "tempo": t})
    return eventi


def _ore(maschera_bool, passo_min):
# Compute the total number of hours where the boolean mask is True, given the time step in minutes                      
    return float(np.sum(maschera_bool) * passo_min / 60)


def _durata_testo(td):
    """timedelta -> '4g 7h 12m'."""
    if td is None:
        return None
    minuti = int(td.total_seconds() // 60)
    g, resto = divmod(minuti, 24 * 60)
    h, m = divmod(resto, 60)
    return f"{g}g {h}h {m}m"


def _iso(t):
    """datetime -> ISO 8601 (UTC) string."""
    return t.strftime('%Y-%m-%dT%H:%M:%SZ')               # For JAVA!!!


def calcola_posizioni(lat, lon, inizio, giorni=30, passo_min=10):
    """Elevazione e azimut di Sole e Terra visti dal sito, nel tempo.
    inizio: datetime (UTC). Restituisce (tempi, sole_alt, sole_az, terra_alt, terra_az).
    """
    r = _risorse()
    ts, eph, pc, frame = r['ts'], r['eph'], r['pc'], r['frame']

    if inizio.tzinfo is None:
        inizio = inizio.replace(tzinfo=timezone.utc)
    n = int(giorni * 24 * 60 / passo_min) + 1
    tempi = [inizio + timedelta(minutes=passo_min * k) for k in range(n)]   # Create a list of datetime objects representing the time steps for the analysis
    t = ts.from_datetimes(tempi)               # Convert the list of datetime objects to Skyfield Time objects for ephemeris calculations (vectorial form)

    sito = eph['moon'] + pc.build_latlon_degrees(frame, lat, lon)     # Create a Skyfield position object for the lunar site using the Moon's ephemeris and the provided latitude and longitude
    osservatore = sito.at(t)                                          # Create a Skyfield observer object at the lunar site for the specified times

    risultati = []
    for corpo in (eph['sun'], eph['earth']):                          # Loop through the Sun and Earth to calculate their apparent positions as seen from the lunar site
        alt, az, _ = osservatore.observe(corpo).apparent().altaz()    # Compute the apparent altitude and azimuth of the celestial body as seen from the lunar site
        risultati += [alt.degrees, az.degrees]                        # Append the altitude and azimuth values (in degrees) to the results list for both the Sun and Earth

    return (tempi, *risultati)  # Contain tempi, sole_alt, sole_az, terra_alt, terra_az (*risultati unpacks the list into individual variables for return)


def valuta_sito(lat, lon, inizio, giorni=30, passo_min=10, orizzonte=None):
    """Valuta un sito lunare su un intervallo di tempo.
    
    Parametri
    ---------
    lat, lon   : coordinate del sito in gradi (lon positiva a est)
    inizio     : datetime UTC di inizio (es. data di atterraggio)
    giorni     : durata dell'analisi (30 = circa una giornata lunare)
    passo_min  : passo temporale in minuti
    orizzonte  : lista di 360 elevazioni dell'orizzonte (gradi) oppure None
    """
    tempi, s_alt, s_az, e_alt, e_az = calcola_posizioni(lat, lon, inizio, giorni, passo_min)
    inizio = tempi[0]

    # Margine = quanto il corpo e' sopra l'orizzonte locale (terreno incluso)
    s_marg = s_alt - _maschera(orizzonte, s_az)
    e_marg = e_alt - _maschera(orizzonte, e_az)
    sole_su = s_marg > 0
    terra_su = e_marg > 0

    eventi = (_trova_eventi(tempi, s_marg, 'alba', 'tramonto')
              + _trova_eventi(tempi, e_marg, 'sorgere_terra', 'tramonto_terra'))
    eventi.sort(key=lambda e: e['tempo'])

    def prossimo(tipo):
        for e in eventi:
            if e['tipo'] == tipo:
                return e['tempo'] - inizio
        return None

    # Tempo al prossimo tramonto del Sole e della Terra (solo se ora sono visibili).
    # Se non tramontano entro il periodo analizzato, il testo lo dice esplicitamente.
    oltre = f"oltre {giorni}g (nessun tramonto nel periodo)"
    al_tramonto = prossimo('tramonto') if sole_su[0] else None
    al_tramonto_terra = prossimo('tramonto_terra') if terra_su[0] else None

    def testo_tramonto(visibile, td):
        if not visibile:
            return "gia' sotto l'orizzonte"
        return _durata_testo(td) if td is not None else oltre

    def testo_sorgere(visibile, td):
        if visibile:
            return None
        return _durata_testo(td) if td is not None else f"oltre {giorni}g (non sorge nel periodo)"

    metriche = {
        "sole_visibile_ora": bool(sole_su[0]),
        "terra_visibile_ora": bool(terra_su[0]),
        "elevazione_sole_ora": round(float(s_alt[0]), 2),
        "elevazione_terra_ora": round(float(e_alt[0]), 2),
        "tempo_al_tramonto": testo_tramonto(sole_su[0], al_tramonto),
        "ore_al_tramonto": None if al_tramonto is None else round(al_tramonto.total_seconds() / 3600, 1),
        "tempo_al_tramonto_terra": testo_tramonto(terra_su[0], al_tramonto_terra),
        "ore_al_tramonto_terra": None if al_tramonto_terra is None else round(al_tramonto_terra.total_seconds() / 3600, 1),
        "tempo_alla_prossima_alba": testo_sorgere(sole_su[0], prossimo('alba')),
        "tempo_al_sorgere_terra": testo_sorgere(terra_su[0], prossimo('sorgere_terra')),
        "ore_di_luce": round(_ore(sole_su, passo_min), 1),
        "ore_terra_visibile": round(_ore(terra_su, passo_min), 1),
        "ore_luce_e_comunicazione": round(_ore(sole_su & terra_su, passo_min), 1),
        "percentuale_luce": round(100 * float(np.mean(sole_su)), 1),
        "percentuale_terra_visibile": round(100 * float(np.mean(terra_su)), 1),
        "elevazione_sole_max": round(float(s_alt.max()), 2),
        "elevazione_terra_min": round(float(e_alt.min()), 2),
        "elevazione_terra_max": round(float(e_alt.max()), 2),
    }

    return {
        "sito": {"lat": lat, "lon": lon},
        "periodo": {"inizio": _iso(inizio), "giorni": giorni, "passo_min": passo_min},
        "orizzonte_terreno": orizzonte is not None,
        "metriche": metriche,
        "eventi": [{"tipo": e['tipo'], "tempo": _iso(e['tempo'])} for e in eventi],
        "serie": {
            "tempo": [_iso(t) for t in tempi],
            "sole_elevazione": np.round(s_alt, 3).tolist(),
            "sole_azimut": np.round(s_az, 3).tolist(),
            "terra_elevazione": np.round(e_alt, 3).tolist(),
            "terra_azimut": np.round(e_az, 3).tolist(),
        },
    }


def grafico(risultato, titolo="", file=None):
    """Grafico di controllo: elevazione di Sole e Terra nel tempo."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    s = risultato['serie']
    tempi = [datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ') for t in s['tempo']]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(tempi, s['sole_elevazione'], color='orange', label='Sole')
    ax.plot(tempi, s['terra_elevazione'], color='royalblue', label='Terra')
    ax.axhline(0, color='gray', lw=1, ls='--', label='Orizzonte (sfera liscia)')
    ax.set_ylabel('Elevazione [gradi]')
    ax.set_title(titolo)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right')
    fig.tight_layout()
    if file:
        fig.savefig(file, dpi=120)
    else:
        plt.show()
    plt.close(fig)


def _stampa(nome, r):
    m = r['metriche']
    print(f"\n=== {nome} ===")
    print(f"Sole ora: {m['elevazione_sole_ora']} gradi | Terra ora: {m['elevazione_terra_ora']} gradi")
    print(f"Tempo al tramonto del Sole:   {m['tempo_al_tramonto']}")
    print(f"Tempo al tramonto della Terra: {m['tempo_al_tramonto_terra']}")
    if m['tempo_alla_prossima_alba']:
        print(f"Prossima alba tra: {m['tempo_alla_prossima_alba']}")
    if m['tempo_al_sorgere_terra']:
        print(f"Prossimo sorgere della Terra tra: {m['tempo_al_sorgere_terra']}")
    print(f"Luce: {m['ore_di_luce']} h ({m['percentuale_luce']}%) | "
          f"Terra visibile: {m['ore_terra_visibile']} h ({m['percentuale_terra_visibile']}%) | "
          f"Entrambi: {m['ore_luce_e_comunicazione']} h")
    print(f"Elevazione max Sole: {m['elevazione_sole_max']} gradi | "
          f"Terra tra {m['elevazione_terra_min']} e {m['elevazione_terra_max']} gradi")
    print("Primi eventi:")
    for e in r['eventi'][:6]:
        print(f"  {e['tempo']}  {e['tipo']}")


if __name__ == '__main__':
    # Esempio 1: Apollo 11, dall'allunaggio per 30 giorni
    apollo = valuta_sito(0.674, 23.473, datetime(1969, 7, 20, 20, 17, tzinfo=timezone.utc))
    _stampa("Apollo 11 (0.674 N, 23.473 E) dal 20/07/1969", apollo)

    # Esempio 2: vicino al polo sud, stessa durata, data recente
    polo = valuta_sito(-89.5, 0.0, datetime(2026, 11, 14, 0, 0, tzinfo=timezone.utc))
    _stampa("Polo sud (89.5 S, 0 E) dal 14/11/2026", polo)

    cartella = Path(__file__).resolve().parent
    grafico(apollo, "Apollo 11 - elevazione di Sole e Terra", cartella / "grafico_apollo11.png")
    grafico(polo, "Polo sud (89.5 S) - elevazione di Sole e Terra", cartella / "grafico_polo_sud.png")
    print("\nGrafici salvati in:", cartella)
