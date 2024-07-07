import os

import pytube
import streamlit as st
class YouTubeDownloader:
    def __init__(self, url):
        self.url = url
        self.youtube = pytube.YouTube(self.url, on_progress_callback=YouTubeDownloader.onProgress)
        self.stream = None
    def showTitle(self):
        st.write(f"**Título:** {self.youtube.title}")
        self.showStreams()
    def showStreams(self):
        streams = self.youtube.streams
        stream_options = [
            f"Resolución: {stream.resolution or 'N/A'} / FPS: {getattr(stream, 'fps', 'N/A')} / Tipo: {stream.mime_type}"
            for stream in streams
        ]
        choice = st.selectbox("Elija una opcion de stream:", stream_options)
        self.stream = streams[stream_options.index(choice)]
    def getFileSize(self):
        file_size = self.stream.filesize / 1000000
        return file_size

    def getPermissionToContinue(self, file_size):
        st.write(f"**Título:** {self.youtube.title}")
        st.write(f"**Autor:** {self.youtube.author}")
        st.write(f"**Tamaño:** {file_size:.2f} MB")
        st.write(f"**Resolución:** {self.stream.resolution or 'N/A'}")
        st.write(f"**FPS:** {getattr(self.stream, 'fps', 'N/A')}")
        download_folder = st.text_input("Ingrese la carpeta de destino para la descarga:")
        if download_folder:
            self.download_folder = download_folder
        if st.button("Descargar"):
            self.download()

    def download(self):
        if not os.path.isdir(self.download_folder):
            st.error("La carpeta de destino no es válida.")
            return
        self.stream.download(output_path=self.download_folder)
        st.success("¡Descarga completada!")
    @staticmethod
    def onProgress(stream=None, chunk=None, remaining=None):
        file_size = stream.filesize / 1000000
        file_download = file_size - (remaining / 1000000)
        st.progress(file_download / file_size)
if __name__ == "__main__":
    st.title("Descargador de Videos de Oyutube")
    url = st.text_input("Ingrese la URL del video de YouTube:")
    if url:
        downloader = YouTubeDownloader(url)
        downloader.showTitle()
        if downloader.stream:
            file_size = downloader.getFileSize()
            downloader.getPermissionToContinue(file_size)