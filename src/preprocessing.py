import pandas as pd
from tqdm import tqdm
from pathlib import Path
from geopy.distance import geodesic

class Preprocessor:
    def __init__(self):
        self.df = None
        self.data_path = Path("data")
        self.city_center_coords = (40.39271412682096, 49.85914227549446)
        self.underground_coords = {"Hazi Aslanov":(40.373051773671946, 49.95349983629199), "Ahmadli":(40.385681694123875, 49.95412197020865),
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

    def read_data(self, filename: str):
        file_path = self.data_path / filename
        self.df = pd.read_excel(file_path)

    def clean_data(self):
        self.df.dropna(inplace=True)
        self.df.drop_duplicates(inplace=True)

    def feature_engineering(self):
        self.df["floor_ratio"] = self.df["floor"] / self.df["max_floor"]

        self.df['distance_from_center'] = self.df.apply(lambda row: geodesic((row['latitude'], row['longitude']), self.city_center_coords).m, axis=1)

        self.df["area_per_room"] = self.df["area"] / self.df["rooms"]

        distances = []
        metros = []
        for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Calculating distances"):
            user_coords = (row['latitude'], row['longitude'])
            min_dist = float("inf")
            nearest_station = None

            for name, coords in self.underground_coords.items():
                dist = geodesic(user_coords, coords).m
                if dist < min_dist:
                    min_dist = dist
                    nearest_station = name

            distances.append(min_dist)
            metros.append(nearest_station.lower())

        self.df['distance_to_nearest_metro'] = distances
        self.df['nearest_metro'] = metros

        self.df.drop(columns=['mortgage', 'receipt'], inplace=True)

    def select_features(self):
        self.df = self.df[[ 
            'address', 'latitude', 'longitude', 'distance_from_center',
            'nearest_metro', 'distance_to_nearest_metro', 'area', 'rooms',
            'area_per_room', 'floor', 'max_floor', 'floor_ratio', 'category',
            'repaired', 'price'
        ]]

    def process(self, filename: str):
        self.read_data(filename)
        self.clean_data()
        self.feature_engineering()
        self.select_features()
        return self.df