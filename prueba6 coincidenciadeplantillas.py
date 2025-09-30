# Tema: pruebas de cocido de imagenes (Coincidencia de plantillas openCV).
# Fecha: 30/09/2025.
# Ixchel Rmz. Gro.

import os
import cv2
import numpy as np

#Configuracion:
ruta_carpeta_imagenes = r'C:\Users\CONFIG\Documents\Potato-Monitor\set_Capa_RGB\set_Capa_RGB'
nombre_panorama_salida = "panorama_mejorado.jpg"
mostrar_intermedias = True
MAX_DIM_RESIZE = 1500

#Paso 1: Cargar imágenes:
print(f"--- Paso 1: Cargando imágenes de la carpeta '{ruta_carpeta_imagenes}' ---")
imagenes = []
rutas_imagenes_cargadas = []

if not os.path.exists(ruta_carpeta_imagenes):
    print(f"\nError: La carpeta de imágenes '{ruta_carpeta_imagenes}' no se encontró.")
    input("\nPresione Enter para salir...")
    exit()

try:
    nombres_archivos = sorted(os.listdir(ruta_carpeta_imagenes))
    print(f"Archivos encontrados: {nombres_archivos}")

    if not nombres_archivos:
        print(f"\nAdvertencia: La carpeta '{ruta_carpeta_imagenes}' está vacía.")
        input("\nPresiona Enter para salir...")
        exit()

    for nombre_archivo in nombres_archivos:
        if nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            ruta_completa_imagen = os.path.join(ruta_carpeta_imagenes, nombre_archivo)
            print(f"Cargando imagen: {ruta_completa_imagen}")
            imagen = cv2.imread(ruta_completa_imagen)

            if imagen is not None:
                if MAX_DIM_RESIZE > 0 and max(imagen.shape) > MAX_DIM_RESIZE:
                    escala = MAX_DIM_RESIZE / max(imagen.shape)
                    imagen = cv2.resize(imagen, (int(imagen.shape[1] * escala), int(imagen.shape[0] * escala)), interpolation=cv2.INTER_AREA)
                    print(f" Imagen '{nombre_archivo}' redimensionada a: {imagen.shape[1]}x{imagen.shape[0]}px")
                print(f" Imagen '{nombre_archivo}' cargada. Dimensiones: {imagen.shape[1]}x{imagen.shape[0]}px")
                imagenes.append(imagen)
                rutas_imagenes_cargadas.append(ruta_completa_imagen)
            else:
                print(f"Error: No se pudo cargar la imagen '{nombre_archivo}'")
        else:
            print(f"  - Ignorando archivo no-imagen: '{nombre_archivo}'")
except Exception as e:
    print(f'\nEror inesperado al leer las imágenes: {e}')
    input("\nPresiona enter para salir...")
    exit()

print("\nResumen de imágenes válidas:")
for i, ruta in enumerate(rutas_imagenes_cargadas, start=1):
    print(f" {i}. {ruta}")
print(f"\nTotal de imágenes válidas: {len(rutas_imagenes_cargadas)}")

#Paso: Coincidencia de plantillas:
def coincidencia_plantillas(img1, img2, metodo=None, mostrar=True):
    """
    Compara img1 contra img2 usando template matching.
    """
    if metodo is None:
        metodo = cv2.TM_CCOEFF_NORMED

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Ajustar tamaño si template es más grande que la imagen:
    if gray1.shape[0] > gray2.shape[0] or gray1.shape[1] > gray2.shape[1]:
        escala = min(gray2.shape[0]/gray1.shape[0], gray2.shape[1]/gray1.shape[1])
        gray1 = cv2.resize(gray1, (int(gray1.shape[1]*escala), int(gray1.shape[0]*escala)), interpolation=cv2.INTER_AREA)

    resultado = cv2.matchTemplate(gray2, gray1, metodo)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultado)

    print(f"\nCoincidencia entre imágenes → Valor máximo de similitud: {max_val:.3f}")

    if mostrar:
        h, w = gray1.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        img_vis = img2.copy()
        cv2.rectangle(img_vis, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imshow("Template (img1)", gray1)
        cv2.imshow("Coincidencia encontrada en img2", img_vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return max_val

# Probar coincidencia entre las dos primeras imágenes:
if len(imagenes) >= 2:
    print("\n--- Prueba de coincidencia de plantillas entre las 2 primeras imágenes ---")
    similitud = coincidencia_plantillas(imagenes[0], imagenes[1])
    if similitud < 0.3:
        print("⚠ Advertencia: La similitud entre las imágenes es baja. Puede que el stitching falle.")

#Paso 2: Crear el panorama:
print("\n--- PASO 2: Creando el panorama ---")
if len(imagenes) < 2:
    print("Se necesitan al menos 2 imágenes para generar un panorama. Saliendo.")
    exit()

stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)

try:
    finder = cv2.AKAZE_create()
    stitcher.setFeaturesFinder(finder)
    print(f"Usando {finder.__class__.__name__} como FeaturesFinder.") #Detecta puntos clave para unir imagenes.
except AttributeError:
    print("Advertencia: No se pudo configurar el FeaturesFinder. Se usará el predeterminado.")

try:
    blender_instance = cv2.detail.FeatherBlender()
    blender_instance.setFeatherWt(0.1)
    if hasattr(stitcher, 'setBlender'):
        stitcher.setBlender(blender_instance)#Suabiza las uniones entre imagenes.
    elif hasattr(stitcher, 'blender'):
        stitcher.blender = blender_instance
except Exception as e:
    print(f"Advertencia: No se pudo configurar el Blender: {e}")

try:
    stitcher.setWaveCorrection(True)
    stitcher.setWaveCorrectKind(cv2.detail.WAVE_CORRECT_HORIZ)
except AttributeError:
    print("Advertencia: No se pudo configurar Wave Correction.")

print("\nIniciando el proceso de stitching...") #Union de imagenes superpuestas.
estado, panorama = stitcher.stitch(imagenes)

if estado == cv2.Stitcher_OK:
    print("Panorama creado correctamente.")

    if panorama is not None and panorama.shape[0] > 0 and panorama.shape[1] > 0:
        if len(panorama.shape) == 3:
            gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
        else:
            gray = panorama
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contornos:
            c = max(contornos, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c) #Union para encerrar el conjunto de puntos.
            if w > 0 and h > 0:
                panorama_recortado = panorama[y:y+h, x:x+w]
                panorama = panorama_recortado
                print(f"Panorama recortado a {panorama.shape}.")
    ruta_salida_panorama = os.path.join(ruta_carpeta_imagenes, nombre_panorama_salida)
    cv2.imwrite(ruta_salida_panorama, panorama)#Union para guardar imagen en el disco indicado por el usuario.
    print(f"\nPanorama final guardado en: {ruta_salida_panorama}")
    if mostrar_intermedias:
        cv2.imshow("Panorama final", panorama)
        cv2.waitKey(0)
        cv2.destroyAllWindows() #Funcion que openCV uso para cerrar todas las ventanas que abrio para ver imagenes.
else:
    print(f"\nError al crear el panorama. Código de estado: {estado}")
    if estado == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print("Falló la estimación de homografía.")
    elif estado == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Se necesitan al menos 2 imágenes válidas.")
    elif estado == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
        print("Falló el ajuste de parámetros de la cámara.")

print("\n--- Proceso finalizado ---")



