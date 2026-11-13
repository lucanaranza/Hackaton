# Hackaton
Hackaton Common Repository
## 🎯 Obiettivi Principali
* **Visualizzazione Cartografica:** Offrire una mappa interattiva della superficie lunare con diversi livelli informativi (immagini ad alta risoluzione, elevazione, pendenza e illuminazione).
* **Analisi dei Vincoli Tecnici:** Permettere agli utenti di filtrare le aree di atterraggio in base ai parametri specifici del lander (es. inclinazione massima tollerata, esposizione solare per l'alimentazione e linea di vista con la Terra per le comunicazioni).
* **Valutazione del Rischio e Ricerca Scientifica:** Calcolare un indice di idoneità (*Suitability Score*) per bilanciare la sicurezza dell'atterraggio con l'interesse scientifico del sito (es. vicinanza a zone in ombra perenne con potenziale presenza di ghiaccio d'acqua).

---

## ⚙️ Funzionalità Chiave
1. **Esplorazione Multi-Layer:** Navigazione fluida con possibilità di attivare, disattivare e sovrapporre diversi dataset lunari.
2. **Filtri Dinamici di Missione:** Pannello di controllo interattivo per impostare i requisiti del veicolo spaziale e aggiornare in tempo reale le zone idonee sulla mappa.
3. **Scheda Dettagli Sito:** Selezione di coordinate specifiche per visualizzare metriche dettagliate (pendenza media, altitudine, temperatura stimata, visibilità terrestre).
4. **Confronto Siti Candidati:** Strumento per salvare e mettere a confronto diverse aree di atterraggio potenziali.

Le librerie che ho scariscate sono
Skyfield, numpy, matplotlib, rasterio, plotly


English Version:

Objectives
Your challenge is to create a tool or application that enables rapid evaluation of lunar landing site options. Your solution may include:

 * Interactive site selection and comparison: You may consider allowing users to choose from a curated list of notable landing sites – such as past Apollo missions, future CLPS mission targets, targets of other commercial lunar missions, or landing sites from other countries' lunar programs – as well as the ability to input custom lunar coordinates. You may also consider enabling side-by-side or sequential comparison of multiple sites to help users quickly assess trade-offs.

* Date and time flexibility: You may consider allowing users to select landing dates and times, and providing tools to explore how conditions change across different lunar days or seasons. This enables users to understand how mission schedule adjustments affect feasibility.

* Sun and Earth position visualization: Display the positions of the Sun and Earth relative to the horizon at a selected landing site on a chosen date. You may consider showing how much time remains before sunset or Earthset, as this directly impacts mission operations and power generation windows.

* Power and communication assessment: You may consider highlighting key metrics such as solar elevation angle (which affects power generation efficiency), duration of sunlight, and Earth visibility windows. These metrics help mission planners quickly assess whether a site-date combination is viable.

* Multiple visualization approaches: You may explore 2D maps, 3D surface visualizations, or other creative representations that help users understand the spatial relationships between the landing site, Sun, and Earth.

* Temporal dynamics: You may consider creating animations or timeline views that show how Sun and Earth positions change over a lunar day or across multiple days, helping users understand the duration and timing of operational windows.

* Accessibility across skill levels: Your tool could serve mission planners seeking detailed technical information for rapid decision-making, as well as educators and the general public curious about why the Moon presents such distinct engineering challenges.
You are encouraged to be creative in how you present this information. Your solution might be a web application, a mobile app, an interactive visualization, an educational game, or another format entirely — as long as it makes rapid site evaluation clear and efficient.

Potential Consideration
You may (but are not required to) consider the following:

Technical approach:

* Ephemeris data – the positions and motions of celestial bodies – can be calculated using tools like the JPL Horizons System, or you may consider using pre-computed datasets.
* Lunar topography data from sources like the Lunar Orbiter Laser Altimeter (LOLA) can help create realistic surface visualizations and accurate horizon calculations.
* Consider how to handle the Moon's lack of atmosphere when calculating horizon positions. Without atmospheric refraction, the horizon is determined by local terrain and the edge of the lunar sphere as seen from the landing site.
* Solar elevation angle is a key metric for power generation, and you may consider calculating and displaying this prominently.

User experience:

* Your interface could prioritize rapid scenario comparison, allowing mission planners to evaluate multiple site-date combinations efficiently.
* Consider how to clearly communicate time remaining before sunset or Earthset, as this is critical operational information.
* Think about how to make the extreme differences between lunar and terrestrial conditions apparent—they can be compelling when visualized effectively.
* You may consider features that help users understand why small location or date changes have large impacts on mission feasibility.

Data and accuracy:

* Consider accounting for the Moon's actual topography, as terrain elevation can significantly affect horizon positions and visibility windows.
* Consider whether your tool will account for factors like Earth's libration (wobble) or the Moon's orbital variations.
* South pole terrain is particularly complex, and you may consider how to represent steep slopes and deep craters that create extreme shadow conditions.

Engagement and impact:

* Your solution could support mission planners in coordinating between science and engineering teams during mission development.
* It could help teams respond quickly when schedule changes or hardware development challenges require landing date or location adjustments.
*I t could also serve as an educational tool to help students and the public understand lunar exploration challenges and why mission planning is so complex.
* For data and resources related to this challenge, refer to the Resources tab at the top of the page. More resources may be added before the hackathon begins.