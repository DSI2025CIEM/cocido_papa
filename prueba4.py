# Tema: pruebas de cocido de imagenes (Stitching de imágenes para crear un panorama).
# Fecha: 24/09/2025.
# Programadora: Ixchel Rmz. Gro.


#Esta version indica en la salida el total de imagenes validas en la salida.

import os
import cv2
import numpy as np

# --- CONFIGURACIÓN ---
# Ruta de la carpeta donde están las imágenes
ruta_carpeta_imagenes = r'C:\Users\CONFIG\Documents\Potato-Monitor\set_Capa_RGB\set_Capa_RGB'
# Nombre del archivo de salida
nombre_panorama_salida = "panorama_mejorado.jpg"
# Mostrar imágenes intermedias (para depuración)
mostrar_intermedias = True

#PASO 1: Cargar imágenes:
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


#Lista de imagenes cargadas:
print("\nResumen de imágenes que realmente se usarán en la estimación de homografía:")
for i, ruta in enumerate(rutas_imagenes_cargadas, start=1):
    print(f" {i}. {ruta}")

print(f"\nTotal de imágenes válidas: {len(rutas_imagenes_cargadas)}")


#PASO 2: Crear el panorama:
print("\n--- PASO 2: Creando el panorama ---")
if len(imagenes) < 2:
    print("Se necesitan al menos 2 imágenes para generar un panorama.")
    exit()


# Crea un objeto Stitcher con configuraciones personalizadas:
stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
# Estas líneas intentan acceder y configurar los componentes internos del stitcher:podemos entenderlo como cosedor de imagen.



#Configuracion del blender(La parte de union de c/d imagen)
if hasattr(stitcher, 'blender'):
    try:
        # Crea un objeto Blender específico
        blender = cv2.detail.FeatherBlender() 
        blender.setFeatherWt(0.1) # Peso del feathering, un valor entre 0 y 1.
        stitcher.blender = blender
        print("Blender Feather configurado con éxito.")
    except Exception as e:
        print(f"Error al configurar FeatherBlender: {e}")
else:
    print("El objeto Stitcher no tiene el atributo 'blender' directamente accesible. La mezcla usará la configuración predeterminada.")
    

# 4. Corrección de Ondas (Wave Correction):
if hasattr(stitcher, 'waveCorrectKind') and hasattr(stitcher, 'waveCorrectKind'):
    try:
        stitcher.setWaveCorrection(True)
        stitcher.setWaveCorrectKind(cv2.detail.WAVE_CORRECT_HORIZ) # o WAVE_CORRECT_VERT
        print("Corrección de ondas (horizontal) activada.")
    except AttributeError:
        print("No se pudo configurar Wave Correction (API diferente).")
else:
    print("El objeto Stitcher no tiene los atributos para Wave Correction directamente accesibles.")


# Realizar el stitching (unión de imagenes para creación del panorama):
estado, panorama = stitcher.stitch(imagenes)

if estado == cv2.Stitcher_OK:
    print("Panorama creado correctamente.")



    #Recorte de bordes sobre la proyeccion:
    if panorama is not None and panorama.shape[0] > 0 and panorama.shape[1] > 0:
        # Encuentra los contornos del área no negra (recorte automático)
        # Asegúrate de que el panorama tenga al menos 3 canales (BGR) antes de convertir a GRAY
        if len(panorama.shape) == 3:
            gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
        else: # Si ya es escala de grises
            gray = panorama
            
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contornos:
            # Encuentra el contorno más grande (que debería ser el panorama)
            c = max(contornos, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)


            # Recorta la imagen:
            if w > 0 and h > 0:
                panorama_recortado = panorama[y:y+h, x:x+w]
                print(f"Panorama recortado de {panorama.shape} a {panorama_recortado.shape}.")
                panorama = panorama_recortado # Usar la versión recortada
            else:
                print("Las dimensiones del contorno son cero o negativas, no se pudo recortar.")
        else:
            print("No se encontraron contornos para recortar el panorama. Puede que ya esté bien o esté todo negro.")


    # Guardar panorama
    ruta_salida_panorama = os.path.join(ruta_carpeta_imagenes, nombre_panorama_salida)
    cv2.imwrite(ruta_salida_panorama, panorama)
    print(f"Panorama guardado en: {ruta_salida_panorama}")

    # Mostrar panorama
    if mostrar_intermedias:
        cv2.imshow("Panorama final", panorama)
        print("\nMostrando el panorama. Cierra la ventana para continuar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
else:
    print(f"Error al crear el panorama. Código de estado: {estado}")

########################################################################################################################################################################
    # Códigos de estado comunes:
    # cv2.Stitcher_ERR_NEED_MORE_IMGS (-1): No hay suficientes imágenes
    # cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL (-2): Falló la estimación de homografía (no se encuentran suficientes coincidencias)
    # cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL (-3): Falló el ajuste de parámetros de la cámara
########################################################################################################################################################################


    if estado == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print("Sugerencia: Intenta con diferentes imágenes, o ajusta los parámetros del Stitcher (ej. detector de características).")
        print("Puede que las imágenes no tengan suficientes puntos en común o sean demasiado diferentes.")
    elif estado == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Sugerencia: Asegúrate de tener al menos 2 imágenes válidas.")

print("\n--- Proceso finalizado ---")