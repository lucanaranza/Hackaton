# Dati topografici condivisi

I GeoTIFF originali di questa cartella sono inclusi nel repository tramite
**Git LFS**. Ogni sito ha una propria sottocartella, per distinguere i dati
già scaricati ed evitare download duplicati.

## Inventario attuale

| Cartella | surf | slp | toterr | ldec |
| --- | --- | --- | --- | --- |
| Sito_01 | presente | presente | presente | presente |
| Sito_07 | presente | presente | presente | presente |
| Sito_11 | presente | presente | presente | presente |
| Sito_23 | presente | presente | presente | presente |

`surf` contiene le quote; `slp` le pendenze; `toterr` l'incertezza verticale;
`ldec` il numero di misure laser per pixel. Aggiornare la tabella quando si
aggiungono altri siti.

## Scaricare i dati dal repository

Installare Git LFS sul proprio computer, poi dalla radice del repository:

```powershell
git lfs install --local
git pull
git lfs pull
```

## Condividere altri dati

Salvare i GeoTIFF nella sottocartella del sito, aggiornare l'inventario e
aggiungere i file insieme alle regole Git LFS:

```powershell
git add .gitattributes .gitignore 3-Topography/readme.md 3-Topography/dati_topografia
git lfs status
git commit -m "Condivide i dati topografici con Git LFS"
git push
```

Le regole Git LFS si applicano automaticamente ai `.tif` e `.tiff` di questa
cartella. I raster generati nelle cartelle di output restano esclusi.
