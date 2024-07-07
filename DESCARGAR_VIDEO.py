import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import threading
import imageio
from imageio import get_reader
from PIL import Image, ImageTk


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargar Videos de YouTube")
        self.root.geometry("600x650")

        self.create_widgets()

    def create_widgets(self):
        # Entry para ingresar el enlace del video
        tk.Label(self.root, text="Enlace del video de YouTube:").pack(pady=10)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)

        # Botón para cargar el video
        self.load_button = tk.Button(self.root, text="Cargar Video", command=self.load_video)
        self.load_button.pack(pady=10)

        # Vista previa del video
        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=10)

        # Menú desplegable para seleccionar la calidad del video
        tk.Label(self.root, text="Calidad del Video:").pack()
        self.quality_var = tk.StringVar()
        self.quality_menu = tk.OptionMenu(self.root, self.quality_var, '')
        self.quality_menu.pack(pady=5)

        # Radio buttons para elegir el formato de descarga
        self.download_format = tk.StringVar(value="video")  # Valor predeterminado: descargar video
        tk.Label(self.root, text="Formato de Descarga:").pack()
        tk.Radiobutton(self.root, text="Video (MP4)", variable=self.download_format, value="video").pack(anchor=tk.W)
        tk.Radiobutton(self.root, text="Audio (MP3)", variable=self.download_format, value="audio").pack(anchor=tk.W)

        # Botón para seleccionar carpeta de destino
        self.browse_button = tk.Button(self.root, text="Seleccionar carpeta de destino", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        # Botón para descargar
        self.download_button = tk.Button(self.root, text="Descargar", command=self.download_video, state=tk.DISABLED)
        self.download_button.pack(pady=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Inicialización de variables
        self.destination_folder = ""
        self.yt = None

    def browse_folder(self):
        # Función para seleccionar carpeta de destino
        self.destination_folder = filedialog.askdirectory()
        if self.destination_folder:
            messagebox.showinfo("Carpeta seleccionada", f"Carpeta de destino: {self.destination_folder}")

    def load_video(self):
        # Función para cargar el video desde el enlace proporcionado
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Entrada no válida", "Por favor, introduce el enlace del video de YouTube.")
            return

        try:
            self.yt = YouTube(url)
            thumbnail_url = self.yt.thumbnail_url
            response = requests.get(thumbnail_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((320, 180), Image.Resampling.LANCZOS)
            self.thumbnail = ImageTk.PhotoImage(img)
            self.video_label.config(image=self.thumbnail)

            streams = self.yt.streams.filter(progressive=True, file_extension='mp4')
            if not streams:
                messagebox.showerror("Error", "No se encontraron streams de video.")
                return

            qualities = [stream.resolution for stream in streams]
            self.quality_var.set(qualities[0])
            self.quality_menu['menu'].delete(0, 'end')

            for quality in qualities:
                self.quality_menu['menu'].add_command(label=quality, command=tk._setit(self.quality_var, quality))

            self.download_button.config(state=tk.NORMAL)
            threading.Thread(target=self.play_video).start()
        except RegexMatchError:
            messagebox.showerror("Error", "El enlace de YouTube es inválido.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def play_video(self):
        # Función para reproducir el video en la interfaz
        video_url = self.yt.streams.filter(progressive=True, file_extension='mp4').first().url
        reader = get_reader(video_url, 'ffmpeg')
        for frame in reader:
            img = Image.fromarray(frame)
            img = img.resize((320, 180), Image.Resampling.LANCZOS)
            self.video_frame = ImageTk.PhotoImage(img)
            self.video_label.config(image=self.video_frame)
            self.root.update_idletasks()

    def download_video(self):
        # Función para descargar el video o el audio según la opción seleccionada
        if not self.destination_folder:
            messagebox.showwarning("Carpeta no seleccionada", "Por favor, selecciona una carpeta de destino.")
            return

        selected_quality = self.quality_var.get()
        if not selected_quality:
            messagebox.showwarning("Calidad no seleccionada", "Por favor, selecciona una calidad de video.")
            return

        if self.download_format.get() == "video":
            # Descargar el video en formato MP4
            video = self.yt.streams.filter(res=selected_quality, progressive=True).first()

            def progress_function(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage_of_completion = bytes_downloaded / total_size * 100
                self.progress['value'] = percentage_of_completion
                self.root.update_idletasks()

            self.yt.register_on_progress_callback(progress_function)

            def start_download():
                try:
                    video.download(output_path=self.destination_folder)
                    messagebox.showinfo("Descarga completada", f"El video se descargó en: {self.destination_folder}")
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error: {e}")
                self.progress['value'] = 0

            threading.Thread(target=start_download).start()
        elif self.download_format.get() == "audio":
            # Extraer y descargar solo el audio en formato MP3
            audio = self.yt.streams.filter(only_audio=True).first()

            def progress_function(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage_of_completion = bytes_downloaded / total_size * 100
                self.progress['value'] = percentage_of_completion
                self.root.update_idletasks()

            self.yt.register_on_progress_callback(progress_function)

            def start_download():
                try:
                    audio.download(output_path=self.destination_folder, filename=f"{self.yt.title}.mp3")
                    messagebox.showinfo("Descarga completada", f"El audio se descargó en: {self.destination_folder}")
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error: {e}")
                self.progress['value'] = 0

            threading.Thread(target=start_download).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
