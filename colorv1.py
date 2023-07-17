import cv2
import json
import numpy as np
import time

def determine_color(hue_value, saturation_value, value_value, color_ranges):
    # Determinar el color según los valores de H, S y V y los rangos especificados
    for color, ranges in color_ranges.items():
        hue_range = ranges["hue"]
        saturation_range = ranges["saturation"]
        value_range = ranges["value"]

        if hue_range[0] <= hue_value <= hue_range[1] and \
           saturation_range[0] <= saturation_value <= saturation_range[1] and \
           value_range[0] <= value_value <= value_range[1]:
            return color

    return "Undefined"

# Leer los parámetros del archivo JSON
with open('parametrosv1.json', 'r') as json_file:
    parametros = json.load(json_file)

resolucion_captura = parametros["resolucion_captura"]
cantidad_areas = parametros["cantidad_areas"]
ancho_area = parametros["ancho_area"]
alto_area = parametros["alto_area"]
posiciones_areas = parametros["posiciones_areas"]
rango_colores = parametros["rango_colores"]
tiempo_desaparicion = parametros["tiempo_desaparicion"]

# Convertir los valores de cadena a enteros
resolucion_captura = tuple(resolucion_captura)
posiciones_areas = [tuple(pos) for pos in posiciones_areas]

cap = cv2.VideoCapture(3)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolucion_captura[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucion_captura[1])

colores_detectados = {}
total_colores_detectados = {}
ultimo_frame_detectado = {}
tiempo_actual = {}

for color in rango_colores.keys():
    if color != "Undefined":
        colores_detectados[color] = 0
        total_colores_detectados[color] = 0
        ultimo_frame_detectado[color] = None
        tiempo_actual[color] = None

while True:
    ret, frame = cap.read()
    if ret:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Voltear la imagen horizontalmente (modo espejo)
        #frame = cv2.flip(frame, 1)

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        height, width, _ = frame.shape
        
        for color in rango_colores.keys():
            if color != "Undefined":
                colores_detectados[color] = 0

        for i in range(cantidad_areas):
            area_x, area_y = posiciones_areas[i]
            centroid_x = area_x + int(ancho_area / 2)
            centroid_y = area_y + int(alto_area / 2)

            pixel_center = hsv_frame[centroid_y, centroid_x]
            hue_value = pixel_center[0]
            saturation_value = pixel_center[1]
            value_value = pixel_center[2]
            color = determine_color(hue_value, saturation_value, value_value, rango_colores)
            #print(pixel_center[0], pixel_center[1], pixel_center[2])

            
            
            cv2.circle(frame, (centroid_x, centroid_y), 1, (255, 255, 255), 2)
            

            if color != "Undefined":
                cv2.rectangle(frame, (area_x, area_y), (area_x + ancho_area, area_y + alto_area), (255, 255, 255), 2)
                #cv2.putText(frame, color, (area_x, area_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(frame, color, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                if ultimo_frame_detectado[color] is None:
                    ultimo_frame_detectado[color] = frame.copy()
                    tiempo_actual[color] = time.time()
                    colores_detectados[color] += 1
                else:
                    tiempo_transcurrido = time.time() - tiempo_actual[color]
                    if tiempo_transcurrido >= tiempo_desaparicion:
                        ultimo_frame_detectado[color] = frame.copy()
                        tiempo_actual[color] = time.time()
                        colores_detectados[color] += 1

        for color, count in colores_detectados.items():
            total_colores_detectados[color] += count

        total_acumulado = sum(total_colores_detectados.values())
        text_y = 360
        for color, count in total_colores_detectados.items():
            cv2.putText(frame, color + ": " + str(count), (7, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            text_y += 20

        cv2.putText(frame, "Total: " + str(total_acumulado), (7, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Contagems", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break

cap.release()
cv2.destroyAllWindows()
