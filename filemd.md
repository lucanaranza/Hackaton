# 🌕 Lunar Landing Site Navigator
**NASA Space Apps Challenge 2026**

## 📖 Panoramica del Progetto
**Lunar Landing Site Navigator** è una web app interattiva progettata per supportare la pianificazione delle missioni lunari (come quelle del programma *Commercial Lunar Payload Services* - CLPS). L'obiettivo dell'applicazione è analizzare la superficie della Luna combinando dati topografici, ambientali e scientifici per identificare e valutare i siti di allunaggio più sicuri e strategici.

---

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