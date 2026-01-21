# Organizzatore Media

Un'applicazione desktop per organizzare automaticamente file multimediali (immagini e video) in cartelle basate sulla data di creazione, con funzionalità di rilevamento duplicati.

## Funzionalità

- Organizza automaticamente immagini e video in cartelle per data (Anno-Mese/TipoFile)
- Supporta i formati: JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP, MP4, MOV, AVI, MKV, WMV, FLV, WEBM
- Rilevamento e rimozione di immagini duplicate al 100%
- Interfaccia grafica intuitiva con barra di avanzamento e log dettagliato
- Pannello di stato con statistiche avanzate:
  - Numero totale di cartelle e file
  - Dimensione totale dei file spostati (in MB/GB)
  - Conteggio file per tipo (JPG, PNG, MP4, ecc.)
  - Data e ora dell'ultima esecuzione
- Possibilità di interrompere l'elaborazione in qualsiasi momento
- Versione eseguibile per Windows disponibile

## Requisiti

### Per l'uso da codice sorgente:
- Python 3.7 o superiore
- Librerie Python (installabili tramite `pip install -r requirements.txt`):
  - Pillow
  - exifread
  - pyinstaller (solo per creare l'eseguibile)

### Versione eseguibile (Windows):
- Windows 10 o successivo
- Nessuna installazione di Python richiesta

## Documentazione Funzioni

### `MediaOrganizerApp`
Classe principale dell'applicazione che gestisce l'interfaccia utente e il flusso di lavoro.

#### Metodi principali:
- `__init__(self, root)`: Inizializza l'interfaccia grafica e i componenti.
- `browse_source(self)`: Apre una finestra di dialogo per selezionare la cartella sorgente.
- `browse_destination(self)`: Apre una finestra di dialogo per selezionare la cartella di destinazione.
- `get_creation_date(self, file_path)`: Ottiene la data di creazione di un file dai metadati EXIF o dalla data di modifica del file.
- `organize_media(self)`: Avvia il processo di organizzazione dei media.
- `update_stats(self)`: Aggiorna le statistiche della cartella di destinazione.
- `load_application_state(self)`: Carica lo stato precedente dell'applicazione.
- `save_application_state(self)`: Salva lo stato corrente dell'applicazione.
- `_find_duplicate_images(self, file_list)`: Trova immagini duplicate al 100% confrontando gli hash MD5.
- `_remove_duplicates(self, duplicates)`: Rimuove i file duplicati, mantenendo una sola copia.
- `_organize_media_thread(self, source, dest)`: Thread per l'elaborazione dei file in background.
- `update_progress(self, value, status)`: Aggiorna la barra di avanzamento e lo stato.
- `finish_organization(self)`: Gestisce il completamento dell'organizzazione.

## Installazione e Utilizzo

### Esecuzione dal codice sorgente:
1. Assicurati di avere Python 3.7 o superiore installato
2. Installa le dipendenze: `pip install -r requirements.txt`
3. Esegui l'applicazione: `python media_organizer.py`

### Creazione eseguibile Windows:
1. Installa PyInstaller: `pip install pyinstaller`
2. Esegui lo script `build.bat`
3. L'eseguibile verrà creato nella cartella `dist/`

### Utilizzo:
1. Seleziona la cartella sorgente contenente i file da organizzare
2. Scegli la cartella di destinazione (verrà creata se non esiste)
3. Attiva l'opzione per rimuovere i duplicati se necessario
4. Clicca su "Organizza Media" per avviare il processo
5. Segui l'avanzamento nella finestra di log

## Note di Rilascio

### Versione 1.3.0 (17/12/2025)
**Nuove Funzionalità:**
- Aggiunto tracciamento della dimensione totale dei file spostati (MB/GB)
- Aggiunto conteggio file per tipo (JPG, PNG, MP4, ecc.)
- Creazione automatica di un eseguibile Windows con `build.bat`
- Migliorata la visualizzazione delle statistiche nel pannello di stato
- Ottimizzazioni delle prestazioni per grandi quantità di file

### Versione 1.2.0 (16/12/2025)
- Aggiunto pannello di stato con statistiche in tempo reale
- Visualizzazione del numero di cartelle e file nella cartella di destinazione
- Tracciamento dell'ultima esecuzione del programma
- Pulsante per aggiornare manualmente le statistiche

### Versione 1.1.0 (15/12/2025)
**Nuove Funzionalità:**
- Aggiunta funzionalità di rilevamento e rimozione di immagini duplicate al 100%
- Aggiunto checkbox per abilitare/disabilitare la rimozione automatica dei duplicati
- Migliorata la gestione degli errori e il logging

**Miglioramenti:**
- Interfaccia utente più intuitiva con feedback dettagliato
- Ottimizzazioni delle prestazioni per l'elaborazione di grandi quantità di file
- Documentazione aggiornata e completa

**Correzioni di Bug:**
- Risolto problema con la gestione dei percorsi su Windows
- Migliorata la gestione dei file corrotti o non accessibili
- Corretta la visualizzazione della barra di avanzamento

## Changelog

### [1.1.0] - 16/12/2025
**Aggiunto:**
- Funzionalità di rilevamento duplicati basata su hash MD5
- Opzione per abilitare/disabilitare la rimozione automatica dei duplicati
- Log dettagliato delle operazioni eseguite

**Modificato:**
- Ristrutturato il codice per una migliore manutenzione
- Migliorata la gestione degli errori
- Aggiornata l'interfaccia utente

**Risolto:**
- Problemi di prestazioni con grandi quantità di file
- Errori nella gestione di file con nomi speciali
- Problemi di sincronizzazione nell'interfaccia grafica

## Utilizzo

1. Avviare l'applicazione eseguendo `python media_organizer.py`
2. Selezionare la cartella sorgente contenente i file da organizzare
3. Specificare la cartella di destinazione (opzionale, di default è una sottocartella "Organized_Media")
4. Selezionare "Elimina immagini duplicate al 100%" per rimuovere automaticamente i duplicati
5. Cliccare su "Organizza Media" per avviare il processo
6. Monitorare l'avanzamento nella barra di avanzamento e nel log

## Licenza

Questo progetto è rilasciato sotto licenza MIT.
