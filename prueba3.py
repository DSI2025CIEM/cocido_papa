# Tema: pruebas de cocido de imagenes (Stitching de imágenes para crear un panorama).
# Fecha: 24/09/2025.
# Programadora: Ixchel Rmz. Gro.


#Esta version indica en la salida el total de imagenes validas en la salida.

import os
import cv2

# Ruta de la carpeta donde están las imágenes
ruta_carpeta_imagenes = r'C:\Users\CONFIG\Documents\Potato-Monitor\set_Capa_RGB\set_Capa_RGB'

# --- PASO 1: Cargar imágenes:
print(f"--- PASO 1: Cargando imágenes de la carpeta '{ruta_carpeta_imagenes}' ---")
imagenes = []
rutas_imagenes_cargadas = []

# Verificar si la carpeta existe:
if not os.path.exists(ruta_carpeta_imagenes):
    print(f"\nERROR: La carpeta de imágenes '{ruta_carpeta_imagenes}' No se encontró.")
    input("\nPresiona enter para salir...")
    exit()

try:
    # Obtener la lista de archivos en la carpeta y ordenarlos:
    nombres_archivos = sorted(os.listdir(ruta_carpeta_imagenes))
    print(f"Archivos encontrados en '{ruta_carpeta_imagenes}': {nombres_archivos}")

    if not nombres_archivos: # Si la lista de archivos está vacía
        print(f"\nAdvertencia: La carpeta '{ruta_carpeta_imagenes}' está vacía o no contiene archivos.")
        input("\nPresiona Enter para salir...")
        exit()

    for nombre_archivo in nombres_archivos:
        # Filtra solo archivos de imagen comunes
        if nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            ruta_completa_imagen = os.path.join(ruta_carpeta_imagenes, nombre_archivo)
            print(f"Cargando imagen: {ruta_completa_imagen}")
            imagen = cv2.imread(ruta_completa_imagen)

            if imagen is not None:
                print(f" Imagen '{nombre_archivo}' cargada. dimensiones: {imagen.shape[1]}x{imagen.shape[0]}px")
                imagenes.append(imagen)
                rutas_imagenes_cargadas.append(ruta_completa_imagen)
            else:
                print(f"Error: No se pudo cargar la imagen '{nombre_archivo}'.")
        else:
            print(f"  - Ignorando archivo no-imagen: '{nombre_archivo}'")

except Exception as e:
    print(f'\nERROR inesperado al leer las imágenes de la carpeta: {e}')
    input("\nPresiona Enter para salir...")
    exit()


# 🔎 --- LISTADO LIMPIO DE IMÁGENES CARGADAS ---
print("\nResumen de imágenes que realmente se usarán en la estimación de homografía:")
for i, ruta in enumerate(rutas_imagenes_cargadas, start=1):
    print(f" {i}. {ruta}")

print(f"\nTotal de imágenes válidas: {len(rutas_imagenes_cargadas)}")


# --- PASO 2: Crear el panorama ---
print("\n--- PASO 2: Creando el panorama ---")
if len(imagenes) < 2:
    print("Se necesitan al menos 2 imágenes para generar un panorama.")
    exit()

stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
estado, panorama = stitcher.stitch(imagenes)

if estado == cv2.Stitcher_OK:
    print("Panorama creado correctamente.")

    # Guardar panorama
    ruta_salida_panorama = os.path.join(ruta_carpeta_imagenes, "panorama_final.jpg")
    cv2.imwrite(ruta_salida_panorama, panorama)
    print(f"Panorama guardado en: {ruta_salida_panorama}")

    # Mostrar panorama
    cv2.imshow("Panorama final", panorama)
    print("\nMostrando el panorama. Cierra la ventana para continuar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"Error al crear el panorama. Código de estado: {estado}")
