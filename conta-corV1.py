import cv2
import numpy as np
import time

font = cv2.FONT_HERSHEY_SIMPLEX

# Función para dibujar contornos y calcular centroides dentro del ROI
def dibujar(frame, mask, color, roi_vertices):
    contornos, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centroids_in_roi = []

    for c in contornos:
        area = cv2.contourArea(c)
        if area > 3000:
            M = cv2.moments(c)
            if M["m00"] == 0:
                M["m00"] = 1
            x = int(M["m10"] / M["m00"])
            y = int(M['m01'] / M['m00'])

            if cv2.pointPolygonTest(roi_vertices, (x, y), False) == 1:
                centroids_in_roi.append((x, y))

            nuevoContorno = cv2.convexHull(c)
            cv2.circle(frame, (x, y), 3, color, -1)
            cv2.putText(frame, '{},{}'.format(x, y), (x + 10, y),
                        font, 0.75, color, 1, cv2.LINE_AA)
            cv2.drawContours(frame, [nuevoContorno], 0, color, 3)

    return centroids_in_roi

# Función vacía para la creación de trackbars
def empty(a):
    pass

# Función para ajustar el rango de color mediante trackbars
def configurar_rango_color():
    cv2.namedWindow("HSV")
    cv2.resizeWindow("HSV", 640, 240)
    cv2.createTrackbar("HUE Min", "HSV", 0, 179, empty)
    cv2.createTrackbar("SAT Min", "HSV", 0, 255, empty)
    cv2.createTrackbar("VALUE Min", "HSV", 0, 255, empty)
    cv2.createTrackbar("HUE Max", "HSV", 179, 179, empty)
    cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
    cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)


def main():
    # Configurar el rango de color mediante trackbars
    configurar_rango_color()

    # Configuración de la cámara
    cam = 4
    width, height = 640, 480
    fps = 60
    brightness, contrast, saturation = 55, 130, 112

    cap = cv2.VideoCapture(cam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
    cap.set(cv2.CAP_PROP_CONTRAST, contrast)
    cap.set(cv2.CAP_PROP_SATURATION, saturation)

    azulBajo = np.array([90, 11, 189], np.uint8)
    azulAlto = np.array([105, 255, 255], np.uint8)

    amarilloBajo = np.array([18, 12, 157], np.uint8)
    amarilloAlto = np.array([32, 255, 255], np.uint8)

    red_low = np.array([0, 76, 171], np.uint8)
    red_high = np.array([10, 255, 255], np.uint8)

    # Definir las coordenadas de los vértices del polígono ROI
    roi_vertices = np.array([[430, 15],
                             [430, 474],
                             [435, 474],
                             [435, 15]], np.int32)

    # Initialize counters and lists to keep track of individual detections
    blue_detections = []
    yellow_detections = []
    red_detections = []

    # FPS Teste
    start_time = time.time()
    display_time = 10
    fc = 0
    p_fps = 0

    while True:
        ret, frame = cap.read()



        # Verificar si se capturó correctamente un cuadro
        if not ret:
            break

        fc+=1

        TIME = time.time() - start_time

        if (TIME) >= display_time :
            p_fps = fc / (TIME)
            fc = 0
            start_time = time.time()

        fps_disp = "FPS: "+str(p_fps)[:5]

        # Add contador de frames
        frame = cv2.putText(frame, fps_disp, (15, 465),
        font, 0.7, (0, 0, 0), 2)

        frameHsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        h_min = cv2.getTrackbarPos("HUE Min", "HSV")
        h_max = cv2.getTrackbarPos("HUE Max", "HSV")
        s_min = cv2.getTrackbarPos("SAT Min", "HSV")
        s_max = cv2.getTrackbarPos("SAT Max", "HSV")
        v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
        v_max = cv2.getTrackbarPos("VALUE Max", "HSV")

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(frameHsv, lower, upper)
        # print(lower)

        maskAzul = cv2.inRange(frameHsv, azulBajo, azulAlto)
        maskAmarillo = cv2.inRange(frameHsv, amarilloBajo, amarilloAlto)
        maskRed = cv2.inRange(frameHsv, red_low, red_high)

        # Llamar a la función dibujar() con el argumento frame
        centroids_azul = dibujar(frame, maskAzul, (255, 0, 0), roi_vertices)
        centroids_amarillo = dibujar(
            frame, maskAmarillo, (0, 255, 255), roi_vertices)
        centroids_rojo = dibujar(frame, maskRed, (0, 0, 255), roi_vertices)

        # Draw the ROI polygon on the frame
        cv2.polylines(frame, [roi_vertices], isClosed=False,
                      color=(0, 255, 0), thickness=2)

        cv2.circle(frame, (30, 32), 15, (255, 0, 0), -1)
        cv2.circle(frame, (30, 72), 15, (0, 255, 255), -1)
        cv2.circle(frame, (30, 112), 15, (0, 0, 255), -1)



        # Update counters based on the number of detected objects within ROI
        blue_detected = len(centroids_azul)
        yellow_detected = len(centroids_amarillo)
        red_detected = len(centroids_rojo)

        # Add individual detections to the corresponding lists
        blue_detections.append(blue_detected)
        yellow_detections.append(yellow_detected)
        red_detections.append(red_detected)

        # Calculate the total count for each color by summing all detections
        total_blue = sum(blue_detections)
        total_yellow = sum(yellow_detections)
        total_red = sum(red_detections)

        # Draw the total counts on the frame for each color
        cv2.putText(frame, f': {total_blue}', (50, 40),
                    font, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f': {total_yellow}',
                    (50, 80), font, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, f': {total_red}',
                    (50, 120), font, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
        total = total_blue + total_yellow + total_red
        cv2.putText(frame, f'Total: {total}', (15, 160),
                    font, 0.75, (0, 0, 0), 2, cv2.LINE_AA)

        result = cv2.bitwise_and(frame, frame, mask=mask)

        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        #hStack = np.hstack([frame])
        hStack = np.hstack([frame, mask, result])
        cv2.imshow('Horizontal Stacking', hStack)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar todas las ventanas de OpenCV al finalizar
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()