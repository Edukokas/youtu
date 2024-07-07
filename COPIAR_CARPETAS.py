import os
import shutil
import re


def is_valid_folder_name(folder_name):
    """ Verifica si el nombre de la carpeta contiene una secuencia de 8 dígitos consecutivos """
    return re.search(r'\d{8}', folder_name) is not None


def copy_valid_folders(src, dst):
    """ Copia carpetas válidas de la carpeta origen a la carpeta destino """
    for root, dirs, files in os.walk(src):
        for dir_name in dirs:
            if is_valid_folder_name(dir_name):
                src_folder = os.path.join(root, dir_name)
                dst_folder = os.path.join(dst, dir_name)
                if not os.path.exists(dst_folder):
                    shutil.copytree(src_folder, dst_folder)
                    print(f'Carpeta copiada: {src_folder} a {dst_folder}')


def main():
    src_folder = input("Ingrese la ruta de la carpeta origen: ")
    dst_folder = input("Ingrese la ruta de la carpeta destino: ")

    if not os.path.exists(src_folder):
        print("La carpeta origen no existe.")
        return

    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    copy_valid_folders(src_folder, dst_folder)
    print("Copia completada.")


if __name__ == "__main__":
    main()
