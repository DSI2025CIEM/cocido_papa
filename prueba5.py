# Tema: pruebas de cocido de imagenes (Stitching de imágenes para crear un panorama).
# Fecha: 29/09/2025.
# Ixchel Rmz. Gro.


#Esta version indica en la salida el total de imagenes validas en la salida.

import os
import cv2
import numpy as np

#CONFIGURACIÓN:
# Ruta de la carpeta donde están las imágenes
ruta_carpeta_imagenes = r'C:\Users\CONFIG\Documents\Potato-Monitor\set_Capa_RGB\set_Capa_RGB'
# Nombre del archivo de salida
nombre_panorama_salida = "panorama_mejorado.jpg"
# Mostrar imágenes intermedias (para depuración)
mostrar_intermedias = True
# Tamaño máximo para redimensionar imágenes antes del stitching (reduce memoria y tiempo)
MAX_DIM_RESIZE = 1500 # Si las imágenes son muy grandes, por ejemplo, más de 2000px en algún lado.

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
    # Obtener la lista de archivos en la carpeta y ordenarlos.
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
                # Opcional: Redimensionar imágenes si son muy grandes para ahorrar memoria y tiempo
                if MAX_DIM_RESIZE > 0 and max(imagen.shape) > MAX_DIM_RESIZE:
                    escala = MAX_DIM_RESIZE / max(imagen.shape)
                    # cv2.resize espera (ancho, alto), no (alto, ancho)
                    imagen = cv2.resize(imagen, (int(imagen.shape[1] * escala), int(imagen.shape[0] * escala)), interpolation=cv2.INTER_AREA)
                    print(f" Imagen '{nombre_archivo}' redimensionada a: {imagen.shape[1]}x{imagen.shape[0]}px")
                
                print(f" Imagen '{nombre_archivo}' cargada. Dimensiones: {imagen.shape[1]}x{imagen.shape[0]}px")
                imagenes.append(imagen)
                rutas_imagenes_cargadas.append(ruta_completa_imagen)
            else:
                print(f"Error: No se pudo cargar la imagen '{nombre_archivo}'. Verifique si el archivo está dañado o la ruta es correcta.")
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
    print("Se necesitan al menos 2 imágenes para generar un panorama. Saliendo.")
    exit()

# --- Configuración avanzada del Stitcher ---

stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)


# 1. Configurar el Finder de Características 
try:
    finder = cv2.AKAZE_create() # Prueba con AKAZE
    #finder = cv2.ORB_create(nfeatures=2000) # Si AKAZE falla, prueba ORB y ajusta nfeatures
    #finder = cv2.SIFT_create() # Si SIFT está disponible y necesitas máxima robustez (puede ser más lento)
    stitcher.setFeaturesFinder(finder)
    print(f"Usando {finder.__class__.__name__} como FeaturesFinder.")
except AttributeError:
    print("Advertencia: No se pudo configurar el FeaturesFinder especificado. Usando el predeterminado del Stitcher (generalmente SIFT si está disponible).")


#3 Configurar el Blending (la parte que te daba el error)
# Esto ayuda a suavizar las uniones entre imágenes y reduce los bordes bruscos.
try:
    # Puedes probar FeatherBlender (más rápido, pero a veces menos suave)
    # o MultiBandBlender (más lento, pero resultados más suaves y sin costuras visibles)
    blender_instance = cv2.detail.FeatherBlender() 
    blender_instance.setFeatherWt(0.1) # Peso del feathering, un valor entre 0 y 1.
    
    # Intenta configurar el blender. En algunas versiones es con setBlender(), en otras con el atributo.
    if hasattr(stitcher, 'setBlender'): # Método preferido si existe
        stitcher.setBlender(blender_instance)
        print("Blender Feather configurado con éxito via setBlender().")
    elif hasattr(stitcher, 'blender'): # Fallback para versiones que exponen el atributo
        stitcher.blender = blender_instance
        print("Blender Feather configurado con éxito via atributo 'blender'.")
    else:
        print("Advertencia: No se pudo configurar un blender personalizado. Se usará el blender predeterminado del Stitcher.")

except Exception as e:
    print(f"Error al configurar el Blender: {e}. Se usará el blender predeterminado.")


# 4. Corrección de Ondas (Wave Correction)
# Ayuda a enderezar el panorama si hay una curvatura no deseada.
try:
    stitcher.setWaveCorrection(True)
    stitcher.setWaveCorrectKind(cv2.detail.WAVE_CORRECT_HORIZ) # o WAVE_CORRECT_VERT si es un panorama vertical
    print("Corrección de ondas (horizontal) activada.")
except AttributeError:
    print("Advertencia: No se pudo configurar Wave Correction (la API puede ser diferente).")


#Realizar el stitching 
print("\nIniciando el proceso de stitching...")
estado, panorama = stitcher.stitch(imagenes)

if estado == cv2.Stitcher_OK:
    print("Panorama creado correctamente.")

    # Post-procesamiento: Recorte de bordes negros no deseados
    if panorama is not None and panorama.shape[0] > 0 and panorama.shape[1] > 0:
        print("Iniciando recorte automático de bordes negros...")
        # Convierte a escala de grises para encontrar el área de la imagen real.
        if len(panorama.shape) == 3: # Si es una imagen a color (BGR)
            gray = cv2.cvtColor(panorama, cv2.COLOR_BGR2GRAY)
        else: # Si ya es escala de grises
            gray = panorama
            
        # Crea una máscara binaria: blanco para pixeles > 1, negro para pixeles <= 1
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        
        # Encuentra los contornos del área blanca (el panorama real)
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contornos:
         # Encuentra el contorno más grande (que debería ser el panorama)
            c = max(contornos, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

        # Recorta la imagen a las dimensiones del contorno encontrado
            if w > 0 and h > 0:
                panorama_recortado = panorama[y:y+h, x:x+w]
                print(f"Panorama recortado de {panorama.shape} a {panorama_recortado.shape}.")
                panorama = panorama_recortado # Usar la versión recortada
            else:
                print("Advertencia: Las dimensiones del contorno son cero o negativas, no se pudo recortar efectivamente.")
        else:
            print("Advertencia: No se encontraron contornos para recortar el panorama. Puede que el panorama esté completamente negro o con muy poco contenido.")
    else:
        print("Advertencia: El panorama resultante está vacío o inválido, no se puede recortar.")

    # Guardar panorama:
    ruta_salida_panorama = os.path.join(ruta_carpeta_imagenes, nombre_panorama_salida)
    cv2.imwrite(ruta_salida_panorama, panorama)
    print(f"\nPanorama final guardado en: {ruta_salida_panorama}")

    # Mostrar panorama:
    if mostrar_intermedias:
        cv2.imshow("Panorama final", panorama)
        print("\nMostrando el panorama. Cierra la ventana para continuar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
else:
    print(f"\nError al crear el panorama. Código de estado: {estado}")
    # Códigos de estado comunes:
    
    if estado == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print("Sugerencia: Falló la estimación de homografía. Esto suele ocurrir porque:")
        print(" - Las imágenes no tienen suficiente solapamiento o puntos en común.")
        print(" - Las imágenes son demasiado diferentes (cambios de perspectiva, iluminación).")
        print(" - Intenta cambiar el detector de características (FeaturesFinder), por ejemplo, a SIFT si está disponible.")
    elif estado == cv2.Stitcher_ERR_NEED_MORE_IMGS:
        print("Sugerencia: Asegúrate de tener al menos 2 imágenes válidas en la carpeta especificada.")
    elif estado == cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL:
        print("Sugerencia: Falló el ajuste de parámetros de la cámara. Puede ser un problema similar al de la homografía.")

print("\n--- Proceso finalizado ---")