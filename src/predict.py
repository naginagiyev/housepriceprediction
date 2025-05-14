import pickle
import numpy as np
from geopy.distance import geodesic

class Predictor:
    def __init__(self, model_path: str):
        self.city_center_coords = (40.39271412682096, 49.85914227549446)
        self.metro_coords = {"Hazi Aslanov":(40.373051773671946, 49.95349983629199), "Ahmadli":(40.385681694123875, 49.95412197020865),
                             "Khalglar Dostlughu":(40.397718265050216, 49.95247536010498), "Neftchiler":(40.41063242845042, 49.944637877423325),
                             "Gara Garayev":(40.41809596280599, 49.93369341348435), "Koroghlu":(40.42174982383615, 49.91682899603657),
                             "Ulduz":(40.4154246911567, 49.89281080952932), "Nariman Narimanov":(40.402894979596034, 49.87063598949156),
                             "Bakmil":(40.414212501973225, 49.87926209603625), "Ganjlik":(40.4006505725387, 49.85152358947007),
                             "28 May":(40.380070538430836, 49.84854200952747), "Sahil":(40.371777336086275, 49.84403189603394),
                             "Icherisheher":(40.36591670244111, 49.83163125130865), "Khatai":(40.383200385960194, 49.87192180952767),
                             "Nizami":(40.37952555022259, 49.829866236562566), "Elmler Akademiyasi":(40.37561857223014, 49.81469909603425),
                             "Inshaatchilar":(40.390291928965276, 49.802691380145696), "20 Yanvar":(40.40416714136188, 49.80781001062231),
                             "Memar Ajami":(40.41066349361367, 49.813622996036), "8 Noyabr":(40.401926268998125, 49.82088033336266),
                             "Avtovagzhal":(40.42152882429223, 49.795038267200965), "Khojasan":(40.42127765054647, 49.778951340214846),
                             "Nasimi":(40.42450930633489, 49.82513056884164), "Azadlig Prospekti":(40.42597278055359, 49.841742796036826),
                             "Darnagul":(40.42550780020771, 49.86194644042418)}
        self.model = self._load_model(model_path)

    def _load_model(self, path: str):
        with open(path, 'rb') as file:
            return pickle.load(file)

    def _calculate_distance_from_center(self, coords: tuple) -> float:
        return geodesic(coords, self.city_center_coords).m

    def _get_nearest_metro_info(self, user_coords: tuple):
        distances = {
            name: geodesic(user_coords, coords).m
            for name, coords in self.metro_coords.items()
        }
        nearest_metro = min(distances, key=distances.get)
        return nearest_metro.lower(), distances[nearest_metro]

    def _preprocess_input(self, input_data: dict) -> dict:
        latitude = input_data['latitude']
        longitude = input_data['longitude']
        coords = (latitude, longitude)

        distance_from_center = self._calculate_distance_from_center(coords)
        nearest_metro, distance_to_nearest_metro = self._get_nearest_metro_info(coords)

        area = input_data['area']
        rooms = input_data['rooms']
        floor = input_data['floor']
        max_floor = input_data['max_floor']

        processed = {
            'address': input_data['address'].lower(),
            'latitude': latitude, 'longitude': longitude,
            'distance_from_center': distance_from_center ** 0.25,
            'nearest_metro': nearest_metro,
            'distance_to_nearest_metro': distance_to_nearest_metro ** 0.25,
            'area': np.log(area), 'rooms': rooms, 'area_per_room': area / rooms,
            'floor': floor, 'max_floor': max_floor, 'floor_ratio': floor / max_floor,
            'category': input_data['category'], 'repaired': input_data['repaired'],
        }

        return processed

    def predict(self, user_input: dict) -> float:
        processed = self._preprocess_input(user_input)

        feature_order = [
            'address', 'latitude', 'longitude', 'distance_from_center', 'nearest_metro',
            'distance_to_nearest_metro', 'area', 'rooms', 'area_per_room', 'floor',
            'max_floor', 'floor_ratio', 'category', 'repaired'
        ]
        input_for_model = [processed[feat] for feat in feature_order]
        
        log_price = self.model.predict([input_for_model])[0]
        return np.exp(log_price)