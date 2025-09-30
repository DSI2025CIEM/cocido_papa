# Tema: pruebas de cocido de imagenes (Coincidencia de plantillas openCV).
#No solo de las primeras imagenes.
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
    print(f'\nError inesperado al leer las imágenes: {e}')
    input("\nPresiona enter para salir...")
    exit()

print("\nResumen de imágenes válidas:")
for i, ruta in enumerate(rutas_imagenes_cargadas, start=1):
    print(f" {i}. {ruta}")
print(f"\nTotal de imágenes válidas: {len(rutas_imagenes_cargadas)}")

#Inicio del Paso de Coincidencia de Plantillas Generalizado
#Paso: Coincidencia de plantillas:
def coincidencia_plantillas_par(img1_src, img2_template, metodo=None, mostrar=False): # Cambié el nombre para ser más específico
    """
    Compara img2_template (la "plantilla") contra img1_src (la "imagen fuente").
    Devuelve el valor de similitud y las coordenadas top_left de la mejor coincidencia.
    """
    if metodo is None:
        metodo = cv2.TM_CCOEFF_NORMED

    gray1 = cv2.cvtColor(img1_src, cv2.COLOR_BGR2GRAY) # La imagen más grande
    gray2 = cv2.cvtColor(img2_template, cv2.COLOR_BGR2GRAY) # La plantilla

    # Asegurarse de que la plantilla no sea más grande que la imagen fuente
    if gray2.shape[0] > gray1.shape[0] or gray2.shape[1] > gray1.shape[1]:
        print(f"  Advertencia: Plantilla ({gray2.shape}) es más grande que la imagen fuente ({gray1.shape}). Ignorando este par.")
        return 0.0, (0, 0) # Retorna 0.0 de similitud si la plantilla es más grande

    resultado = cv2.matchTemplate(gray1, gray2, metodo)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultado)

    # Determinar el top_left según el método
    if metodo in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
        similitud_valor = 1 - min_val # Invertir para que mayor sea mejor, como otros métodos
    else: # TM_CCORR, TM_CCORR_NORMED, TM_CCOEFF, TM_CCOEFF_NORMED
        top_left = max_loc
        similitud_valor = max_val

    if mostrar:
        h, w = gray2.shape # Dimensiones de la plantilla
        bottom_right = (top_left[0] + w, top_left[1] + h)
        img_vis = img1_src.copy()
        cv2.rectangle(img_vis, top_left, bottom_right, (0, 255, 0), 2)
        cv2.imshow(f"Plantilla ({rutas_imagenes_cargadas[imagenes.index(img2_template)].split(os.sep)[-1]})", gray2)
        cv2.imshow(f"Coincidencia en {rutas_imagenes_cargadas[imagenes.index(img1_src)].split(os.sep)[-1]} (Similitud: {similitud_valor:.3f})", img_vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return similitud_valor, top_left

# Probar coincidencia de plantillas entre todas las imágenes adyacentes.
if len(imagenes) > 1:
    print("\n--- PASO INTERMEDIO: Evaluación de Coincidencia de Plantillas entre imágenes adyacentes ---")
    similitudes = []
    umbral_advertencia = 0.4 # Umbral por debajo del cual se considera baja la similitud.

    for i in range(len(imagenes) - 1):
        img_actual = imagenes[i]
        img_siguiente = imagenes[i+1]
        nombre_actual = rutas_imagenes_cargadas[i].split(os.sep)[-1]
        nombre_siguiente = rutas_imagenes_cargadas[i+1].split(os.sep)[-1]

        print(f"Comparando '{nombre_actual}' como imagen fuente y '{nombre_siguiente}' como plantilla...")
    
        similitud_val, _ = coincidencia_plantillas_par(img_actual, img_siguiente, mostrar=mostrar_intermedias)
        similitudes.append(similitud_val)
        print(f"Similitud entre '{nombre_actual}' y '{nombre_siguiente}': {similitud_val:.3f}")

        if similitud_val < umbral_advertencia:
            print(f"⚠ Advertencia: La similitud ({similitud_val:.3f}) entre '{nombre_actual}' y '{nombre_siguiente}' es baja. Puede que el stitching falle para este par.")

    if similitudes:
        similitud_promedio = np.mean(similitudes)
        print(f"\nSimilitud promedio entre pares adyacentes: {similitud_promedio:.3f}")
        if similitud_promedio < umbral_advertencia:
            print("⚠ Advertencia general: La similitud promedio entre las imágenes es baja. El stitching podría tener dificultades.")
    else:
        print("No se encontraron pares para comparar la similitud.")
else:
    print("Se necesitan al menos 2 imágenes para realizar la coincidencia de plantillas entre pares adyacentes.")
# --- Fin del Paso de Coincidencia de Plantillas Generalizado ---


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