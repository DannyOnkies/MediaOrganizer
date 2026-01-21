import os
import shutil
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import exifread
import json


class MediaOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizzatore Media")
        self.root.geometry("900x700")  # Aumentata la dimensione della finestra per il nuovo pannello
        self.dest_path = tk.StringVar()
        self.dest_path.set(r"C:\Users\danie\Desktop\MediaOrganized")

        # Stile
        style = ttk.Style()
        style.theme_use('clam')

        # Frame principale
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Pannello superiore per i controlli
        control_frame = ttk.LabelFrame(self.main_frame, text="Controlli", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Etichetta e campo percorso sorgente
        ttk.Label(control_frame, text="Cartella sorgente:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.source_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.source_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Sfoglia...", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)

        # Etichetta e campo percorso destinazione
        ttk.Label(control_frame, text="Cartella destinazione:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.dest_path = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.dest_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Sfoglia...", command=self.browse_destination).grid(row=1, column=2, padx=5,
                                                                                           pady=5)

        # Checkbox per il rilevamento duplicati
        self.duplicate_check = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="Elimina immagini duplicate al 100%",
                        variable=self.duplicate_check).grid(row=2, column=0, columnspan=3, pady=5)

        # Pulsante di avvio e aggiornamento statistiche
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)

        self.organize_btn = ttk.Button(btn_frame, text="Organizza Media", command=self.organize_media)
        self.organize_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(btn_frame, text="Aggiorna Statistiche", command=self.update_stats)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Barra di avanzamento
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        # Area di log
        log_frame = ttk.LabelFrame(self.main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbar per l'area di log
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # Pannello di stato
        self.status_frame = ttk.LabelFrame(self.main_frame, text="Stato", padding="10")
        self.status_frame.pack(fill=tk.X, pady=(0, 10))

        # Etichette per lo stato
        self.folder_count_var = tk.StringVar(value="Cartelle: 0")
        self.file_count_var = tk.StringVar(value="File: 0")
        self.last_run_var = tk.StringVar(value="Ultimo avvio: Mai")

        ttk.Label(self.status_frame, textvariable=self.folder_count_var).grid(row=0, column=0, padx=10, pady=2,
                                                                              sticky=tk.W)
        ttk.Label(self.status_frame, textvariable=self.file_count_var).grid(row=1, column=0, padx=10, pady=2,
                                                                            sticky=tk.W)
        ttk.Label(self.status_frame, textvariable=self.last_run_var).grid(row=0, column=1, padx=10, pady=2, sticky=tk.W)

        # Variabili di stato
        self.is_organizing = False
        self.stop_requested = False

        # Statistiche
        self.total_size_moved = 0  # in bytes
        self.file_type_counts = {
            'JPG': 0, 'JPEG': 0, 'PNG': 0, 'GIF': 0, 'BMP': 0,
            'TIFF': 0, 'WEBP': 0, 'MP4': 0, 'MOV': 0, 'AVI': 0,
            'MKV': 0, 'WMV': 0, 'FLV': 0, 'WEBM': 0
        }

        # Etichette aggiuntive per lo stato
        self.total_size_var = tk.StringVar(value="Dimensione totale: 0 MB")
        self.file_types_var = tk.StringVar(value="File per tipo: ")

        # Aggiungi le nuove etichette al pannello di stato
        ttk.Label(self.status_frame, textvariable=self.total_size_var).grid(row=2, column=0, padx=10, pady=2,
                                                                            sticky=tk.W)
        ttk.Label(self.status_frame, textvariable=self.file_types_var, wraplength=600).grid(
            row=3, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)

        # Carica lo stato precedente e aggiorna il pannello
        self.load_application_state()

    def log(self, message):
        """Aggiunge un messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def browse_source(self):
        """Apre la finestra di dialogo per selezionare la cartella sorgente"""
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
            # Imposta automaticamente la cartella di destinazione se non è già impostata
            if not self.dest_path.get():
                self.dest_path.set(os.path.join(folder, "Organized_Media"))

    def browse_destination(self):
        """Apre la finestra di dialogo per selezionare la cartella di destinazione"""
        folder = filedialog.askdirectory()
        if folder:
            self.dest_path.set(folder)

    def get_creation_date(self, file_path):
        """Ottiene la data di creazione di un file"""
        try:
            # Prova a ottenere la data dai metadati EXIF per le immagini
            if file_path.lower().endswith(('.jpg', '.jpeg', '.tiff', '.tif')):
                with open(file_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)
                    if 'EXIF DateTimeOriginal' in tags:
                        date_str = str(tags['EXIF DateTimeOriginal'])
                        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')

            # Per i file video o se non trova i metadati EXIF, usa la data di modifica del file
            return datetime.fromtimestamp(os.path.getmtime(file_path))

        except Exception as e:
            self.log(f"Errore durante il recupero della data per {file_path}: {str(e)}")
            return datetime.now()  # Data di default in caso di errore

    def load_application_state(self):
        """Carica lo stato precedente dell'applicazione"""
        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_state.json')
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    if 'last_run' in state:
                        self.last_run_var.set(f"Ultimo avvio: {state['last_run']}")
        except Exception as e:
            self.log(f"Errore nel caricamento dello stato: {str(e)}")

    def save_application_state(self):
        """Salva lo stato corrente dell'applicazione"""
        state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_state.json')
        try:
            state = {
                'last_run': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            with open(state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            self.log(f"Errore nel salvataggio dello stato: {str(e)}")

    def update_stats(self):
        """Aggiorna le statistiche della cartella di destinazione"""
        dest = self.dest_path.get()
        if not dest or not os.path.exists(dest):
            self.folder_count_var.set("Cartelle: N/A")
            self.file_count_var.set("File: N/A")
            return

        try:
            num_files = 0
            num_dirs = 0

            for root, dirs, files in os.walk(dest):
                num_dirs += len(dirs)
                num_files += len(files)

            self.folder_count_var.set(f"Cartelle: {num_dirs}")
            self.file_count_var.set(f"File: {num_files}")
            self.log("Statistiche aggiornate con successo")
        except Exception as e:
            self.log(f"Errore nell'aggiornamento delle statistiche: {str(e)}")

    def _update_file_type_stats(self, file_extension, file_size):
        """Aggiorna le statistiche dei tipi di file e la dimensione totale"""
        ext = file_extension.upper().lstrip('.')
        if ext in self.file_type_counts:
            self.file_type_counts[ext] += 1
            self.total_size_moved += file_size

            # Aggiorna la visualizzazione
            size_mb = self.total_size_moved / (1024 * 1024)  # Converti in MB
            if size_mb < 1024:
                self.total_size_var.set(f"Dimensione totale: {size_mb:.2f} MB")
            else:
                size_gb = size_mb / 1024
                self.total_size_var.set(f"Dimensione totale: {size_gb:.2f} GB")

            # Aggiorna il conteggio dei tipi di file
            type_counts = [f"{k}: {v}" for k, v in self.file_type_counts.items() if v > 0]
            self.file_types_var.set("File per tipo: " + ", ".join(type_counts))

    def organize_media(self):
        """Avvia il processo di organizzazione dei media"""
        if self.is_organizing:
            return

        os.makedirs(self.dest_path.get(), exist_ok=True)

        # Resetta i contatori
        self.total_size_moved = 0
        self.file_type_counts = {k: 0 for k in self.file_type_counts}
        self.total_size_var.set("Dimensione totale: 0 MB")
        self.file_types_var.set("File per tipo: ")

        source = self.source_path.get()
        dest = self.dest_path.get()

        # Aggiorna la data dell'ultimo avvio
        self.save_application_state()
        self.last_run_var.set(f"Ultimo avvio: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        if not source or not dest:
            messagebox.showerror("Errore", "Seleziona sia la cartella sorgente che quella di destinazione")
            return

        if not os.path.exists(source):
            messagebox.showerror("Errore", f"La cartella sorgente non esiste: {source}")
            return

        # Crea la cartella di destinazione se non esiste
        os.makedirs(dest, exist_ok=True)

        self.is_organizing = True
        self.stop_requested = False
        self.organize_btn.config(text="Ferma")
        self.log("Avvio organizzazione media...")
        self.log(f"Origine: {source}")
        self.log(f"Destinazione: {dest}")

        # Pulisci la barra di avanzamento
        self.progress['value'] = 0
        self.root.update_idletasks()

        # Avvia il processo in un thread separato per non bloccare l'interfaccia
        import threading
        self.processing_thread = threading.Thread(target=self._organize_media_thread, args=(source, dest), daemon=True)
        self.processing_thread.start()

        # Avvia il timer per aggiornare l'interfaccia
        self.update_progress_timer()

    def update_progress_timer(self):
        """Aggiorna periodicamente l'interfaccia utente durante l'elaborazione"""
        if self.is_organizing:
            self.root.after(100, self.update_progress_timer)  # Aggiorna ogni 100ms

    def _find_duplicate_images(self, file_list):
        """Trova immagini duplicate al 100%"""
        self.log("Ricerca immagini duplicate in corso...")
        file_hashes = {}
        duplicates = []

        for file_path, file, file_ext in file_list:
            if self.stop_requested:
                return []

            if file_ext.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}:
                try:
                    # Calcola l'hash del file
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()

                    # Se l'hash esiste già, è un duplicato
                    if file_hash in file_hashes:
                        duplicates.append((file_path, file_hashes[file_hash]))
                        self.log(f"Trovato duplicato: {os.path.basename(file_path)}")
                    else:
                        file_hashes[file_hash] = file_path
                except Exception as e:
                    self.log(f"Errore durante l'analisi di {file_path}: {str(e)}")

        return duplicates

    def _remove_duplicates(self, duplicates):
        """Rimuovi i file duplicati"""
        if not duplicates:
            self.log("Nessuna immagine duplicata trovata.")
            return 0

        self.log(f"Rimozione di {len(duplicates)} immagini duplicate...")
        removed_count = 0

        for duplicate, original in duplicates:
            if self.stop_requested:
                break

            try:
                os.remove(duplicate_path)
                self.log(f"Eliminato duplicato: {duplicate_path}")
                removed_count += 1
            except Exception as e:
                self.log(f"Impossibile eliminare il file {duplicate_path}: {str(e)}", "errore")

        return removed_count

    def _organize_media_thread(self, source, dest):
        """Thread per l'organizzazione dei media"""
        try:
            # Estensioni supportate
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
            video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'}

            # Fase 1: Conta i file da elaborare
            self.log("Analisi dei file in corso...")
            file_list = []
            for root_dir, _, files in os.walk(source):
                if self.stop_requested:
                    break

                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in image_extensions or file_ext in video_extensions:
                        file_path = os.path.join(root_dir, file)
                        file_list.append((file_path, file, file_ext))

            # Se richiesto, cerca e rimuovi duplicati
            if self.duplicate_check.get():
                duplicates = self._find_duplicate_images(file_list)
                if duplicates:
                    removed = self._remove_duplicates(duplicates)
                    self.log(f"Rimossi {removed} file duplicati.")
                    # Aggiorna la lista dei file dopo la rimozione dei duplicati
                    file_list = [(path, file, ext) for path, file, ext in file_list
                                 if not any(d[0] == path for d in duplicates)]
                else:
                    self.log("Nessuna immagine duplicata trovata.")

            total_files = len(file_list)
            if total_files == 0:
                self.log("Nessun file immagine o video trovato nella cartella specificata.")
                self.finish_organization()
                return

            self.log(f"Trovati {total_files} file da elaborare...")

            # Fase 2: Elabora i file
            processed = 0
            for file_path, file, file_ext in file_list:
                if self.stop_requested:
                    break

                try:
                    # Ottieni la data di creazione
                    creation_date = self.get_creation_date(file_path)
                    year_month = creation_date.strftime("%Y-%m")

                    # Determina la sottocartella in base al tipo di file
                    file_type = "Immagini" if file_ext in image_extensions else "Video"

                    # Crea la struttura delle cartelle: Anno-Mese/TipoFile
                    target_folder = os.path.join(dest, year_month, file_type)
                    os.makedirs(target_folder, exist_ok=True)

                    # Costruisci il percorso di destinazione
                    dest_file = os.path.join(target_folder, file)

                    # Se il file esiste già, aggiungi un suffisso numerato
                    counter = 1
                    while os.path.exists(dest_file):
                        name, ext = os.path.splitext(file)
                        dest_file = os.path.join(target_folder, f"{name}_{counter}{ext}")
                        counter += 1

                    # Copia il file
                    shutil.copy2(file_path, dest_file)

                    # Aggiorna le statistiche
                    file_size = os.path.getsize(dest_file)
                    self.root.after(0, self._update_file_type_stats, file_ext, file_size)

                    processed += 1
                    progress = (processed / total_files) * 100

                    # Aggiorna l'interfaccia ogni 10 file o per l'ultimo file
                    if processed % 10 == 0 or processed == total_files:
                        status = f"Elaborati {processed}/{total_files} file ({progress:.1f}%) - {file}"
                        self.root.after(0, self.update_progress, progress, status)

                except Exception as e:
                    error_msg = f"Errore durante l'elaborazione di {file}: {str(e)}"
                    self.root.after(0, self.log, error_msg)
                    continue

            if not self.stop_requested:
                self.root.after(0, self.log, "\nOrganizzazione completata con successo!")
                self.root.after(0, messagebox.showinfo, "Completato",
                                "L'organizzazione dei media è stata completata con successo!")
            else:
                self.root.after(0, self.log, "\nOperazione interrotta dall'utente.")

        except Exception as e:
            error_msg = f"\nSi è verificato un errore: {str(e)}"
            self.root.after(0, self.log, error_msg)
            self.root.after(0, messagebox.showerror, "Errore",
                            f"Si è verificato un errore durante l'organizzazione: {str(e)}")
        finally:
            self.root.after(0, self.finish_organization)

    def update_progress(self, value, message):
        """Aggiorna la barra di avanzamento e il log"""
        try:
            self.progress['value'] = value
            self.log(message)
            # Forza l'aggiornamento dell'interfaccia
            self.root.update_idletasks()
        except Exception as e:
            print(f"Errore durante l'aggiornamento della UI: {str(e)}")

    def finish_organization(self):
        """Ripristina l'interfaccia al termine dell'organizzazione"""
        self.is_organizing = False
        self.stop_requested = False

        # Ripristina lo stato dei widget
        def restore_widgets():
            self.organize_btn.config(text="Organizza Media", state=tk.NORMAL)
            for widget in self.main_frame.winfo_children():
                try:
                    if widget != self.progress:  # Non modificare la barra di avanzamento
                        widget.config(state=tk.NORMAL)
                except:
                    pass  # Ignora i widget che non supportano l'opzione 'state'

            # Forza l'aggiornamento dell'interfaccia
            self.root.update_idletasks()

        self.root.after(0, restore_widgets)


def main():
    root = tk.Tk()
    app = MediaOrganizerApp(root)

    # Imposta l'icona dell'applicazione (opzionale)
    try:
        root.iconbitmap(default='icon.ico')  # Assicurati di avere un file icon.ico nella stessa cartella
    except:
        pass  # Ignora se non riesci a caricare l'icona

    root.mainloop()


if __name__ == "__main__":
    main()
