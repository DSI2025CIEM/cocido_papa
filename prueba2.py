# Tema: pruebas de cocido de imagenes (Stitching de imágenes para crear un panorama).
# Fecha: 18/09/2025.
# Programadora: Ixchel Rmz. Gro.

import os
import cv2
import shutil # Para eliminar directorios y su contenido (opcional)


ruta_carpeta_imagenes = r'C:\Users\CONFIG\Documents\Potato-Monitor\set_Capa_RGB\set_Capa_RGB'

# --- PASO 1: Cargar imágenes:
#Carga todas las imagenes contenidas en la carpeta zip (13)
print(f"--- PASO 1: Cargando imágenes de la carpeta '{ruta_carpeta_imagenes}' ---")
imagenes = []
rutas_imagenes_cargadas = []

# Verificar si la carpeta existe:
if not os.path.exists(ruta_carpeta_imagenes):
    print(f"\nERROR: La carpeta de imágenes '{ruta_carpeta_imagenes}' No se encontro.")
    print("Por favor, verifica que la ruta sea correcta y que la carpeta exista.")
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
                rutas_imagenes_cargadas.append(ruta_completa_imagen) # Guarda la ruta para depuración.
            else:
                print(f"ERROR: No se pudo cargar la imagen '{nombre_archivo}'. ¿Está corrupta o no es un formato válido?")
        else:
            print(f"  - Ignorando archivo no-imagen: '{nombre_archivo}'")

except Exception as e:
    print(f'\nERROR inesperado al leer las imágenes de la carpeta: {e}')
    input("\nPresiona Enter para salir...")
    exit()

# --- PASO 2: Unir las fotografías para crear el panorama ---
print(f"\n--- PASO 2: Creando el panorama ---")

if len(imagenes) < 14:
    print(f"\nAdvertencia: Se necesitan al menos dos imágenes para crear un panorama.")
    print(f"Solo se cargaron {len(imagenes)} imágenes válidas. Saliendo.")
    input("\nPresiona enter para salir...")
    exit()
else:
    print(f"\nTotal de imágenes válidas cargadas para unir: {len(imagenes)}")

    # Intenta crear el objeto Stitcher
    try:
        stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
        print("Objeto Stitcher creado. Intentando unir las imágenes para crear el panorama...")
        (estado, panorama) = stitcher.stitch(imagenes)
    except Exception as e:
        print(f'\nERROR: Falló la inicialización o ejecución del Stitcher: {e}')
        print('Asegúrate de que OpenCV está correctamente instalado y las dependencias son correctas.')
        input("\nPresiona Enter para salir...")
        exit()


    # --- PASO 3: Manejar el resultado del Stitching ---
    print(f"\n--- PASO 3: Procesando el resultado del panorama ---")
    if estado == cv2.Stitcher_OK:
        print("¡El panorama se ha creado!")

        # Construye la ruta de salida para el panorama final
        # El panorama se guardará en la misma carpeta donde se cargaron las imágenes.
        ruta_salida_panorama = os.path.join(ruta_carpeta_imagenes, 'panorama_final.jpg')
        cv2.imwrite(ruta_salida_panorama, panorama)
        print(f"Panorama guardado en: '{ruta_salida_panorama}'")
        print(f"Dimensiones del panorama final: {panorama.shape[1]}x{panorama.shape[0]}px")

        # Muestra el panorama en una ventana (requiere entorno gráfico)
        print("\nMostrando el panorama. Cierra la ventana para continuar...")
        cv2.imshow('Panorama final creado', panorama)
        cv2.waitKey(0) # Espera indefinidamente hasta que se presione una tecla
        cv2.destroyAllWindows() # Cierra todas las ventanas de OpenCV
        print("Ventana del panorama cerrada.")
        
        # Generar imagen con el panorama
        print("\nAquí tienes una representación visual del panorama generado:")
        
    elif estado == cv2.Stitcher_ERR_NO_ENOUGH_FEATURES:
        print(f"\nError al unir las imágenes (código de estado: {estado}): no hay suficientes puntos clave o super posición..")
        print("Posibles causas:")
        print("  - Las imágenes no tienen suficiente área de superposición entre sí.")
        print("  - Las imágenes son demasiado similares o tienen poca textura para encontrar puntos clave.")
        print("  - Las imágenes están muy desenfocadas o tienen mala calidad.")
    elif estado == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
        print(f"\nError al unir las imágenes (código de estado: {estado}): fallo en la estimación de homografía")
        print("Esto puede ocurrir si las imágenes tienen una perspectiva muy diferente,")
        print("o si el movimiento de la cámara entre tomas fue demasiado grande o irregular.")
    elif estado == cv2.Stitcher_ERR_CAM_PARAMS_ADJ_FAIL:
        print(f"\nError al unir las imágenes (código de estado: {estado}): falla en el ajuste de párametros de la cámara.")
        print("Suele indicar problemas más complejos con la geometría o el modelo de cámara de las imágenes.")
    else:
        print(f"\nError  al unir las imágenes. Código de estado desconocido: {estado}")
