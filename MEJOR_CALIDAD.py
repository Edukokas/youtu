import os
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, messagebox, ttk
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import threading

def select_path():
    path = filedialog.askdirectory()
    if path:
        path_var.set(path)

def update_video_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    video_progress_var.set(percentage_of_completion)
    root.update_idletasks()

def update_audio_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    audio_progress_var.set(percentage_of_completion)
    root.update_idletasks()

def download_video():
    url = url_var.get()
    path = path_var.get()
    if not url:
        messagebox.showerror("Error", "Por favor, ingrese una URL de YouTube")
        return
    if not path:
        messagebox.showerror("Error", "Por favor, seleccione una ruta de destino")
        return

    try:
        yt = YouTube(url)

        # Descargar el video y audio de mayor calidad
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4').order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()

        if video_stream is None or audio_stream is None:
            messagebox.showerror("Error", "No hay streams disponibles para esta URL")
            return

        # Descargar video
        video_progress_bar.grid(row=6, column=0, columnspan=3, pady=10)
        video_progress_var.set(0)
        video_file = video_stream.download(output_path=path, filename='video.mp4')

        # Descargar audio
        audio_progress_bar.grid(row=8, column=0, columnspan=3, pady=10)
        audio_progress_var.set(0)
        audio_file = audio_stream.download(output_path=path, filename='audio.mp4')

        # Combinar video y audio
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)
        final_clip = video_clip.set_audio(audio_clip)

        combined_progress_bar.grid(row=10, column=0, columnspan=3, pady=10)
        combined_progress_var.set(0)

        # Esta función realiza la escritura del archivo, sin mostrar la barra de progreso.
        output_file = os.path.join(path, yt.title + '.mp4')
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', verbose=False, threads=4)

        # Limpiar archivos temporales
        video_clip.close()
        audio_clip.close()
        os.remove(video_file)
        os.remove(audio_file)

        combined_progress_var.set(100)
        combined_progress_bar.grid_remove()
        messagebox.showinfo("Éxito", f"Video descargado y combinado exitosamente en {output_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def start_download_thread():
    threading.Thread(target=download_video).start()

# Crear la GUI
root = Tk()
root.title("YouTube Video Downloader")
root.geometry("500x300")

url_label = Label(root, text="URL de YouTube:")
url_label.grid(row=0, column=0, pady=10)
url_var = StringVar()
url_entry = Entry(root, textvariable=url_var, width=50)
url_entry.grid(row=0, column=1, pady=10)

path_label = Label(root, text="Ruta de destino:")
path_label.grid(row=1, column=0, pady=10)
path_var = StringVar()
path_entry = Entry(root, textvariable=path_var, width=50)
path_entry.grid(row=1, column=1, pady=10)
path_button = Button(root, text="Seleccionar ruta", command=select_path)
path_button.grid(row=1, column=2, pady=10)

download_button = Button(root, text="Descargar Video", command=start_download_thread)
download_button.grid(row=2, column=1, pady=20)

video_progress_var = StringVar()
video_progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate', variable=video_progress_var)

audio_progress_var = StringVar()
audio_progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate', variable=audio_progress_var)

combined_progress_var = StringVar()
combined_progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate', variable=combined_progress_var)

root.mainloop()
