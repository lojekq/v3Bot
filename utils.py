from math import radians, sin, cos, sqrt, atan2

# Функция для расчета расстояния между двумя координатами (широта, долгота) в километрах
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Радиус Земли в километрах

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance
