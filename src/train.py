import pickle
import warnings
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from preprocessing import Preprocessor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error

warnings.filterwarnings('ignore')

print("Processing...")
try:
    train = pd.read_excel("./data/train.xlsx") 
    test = pd.read_excel("./data/test.xlsx")
    oot = pd.read_excel("./data/oot.xlsx")

except:
    processor = Preprocessor()
    data = processor.process("data.xlsx")
    oot = processor.process("oot.xlsx")

    low, high = data["price"].quantile([0.02, 0.98])
    data = data[(data["price"] >= low) & (data["price"] <= high)]
    oot = oot[(oot["price"] >= low) & (oot["price"] <= high)]

    train, test = train_test_split(data, test_size=0.15, random_state=42)
    print(f"Train: {len(train)}, Test: {len(test)}, OOT: {len(oot)}")

    for col in ['price', 'area']:
        train[col] = np.log(train[col])
        test[col] = np.log(test[col])
        oot[col] = np.log(oot[col])

    train['distance_from_center'] = train['distance_from_center'] ** 0.25
    test['distance_from_center'] = test['distance_from_center'] ** 0.25
    oot['distance_from_center'] = oot['distance_from_center'] ** 0.25

    train['distance_to_nearest_metro'] = train['distance_to_nearest_metro'] ** 0.25
    test['distance_to_nearest_metro'] = test['distance_to_nearest_metro'] ** 0.25
    oot['distance_to_nearest_metro'] = oot['distance_to_nearest_metro'] ** 0.25

    train.to_excel('./data/train.xlsx', index=False)
    test.to_excel('./data/test.xlsx', index=False)
    oot.to_excel('./data/oot.xlsx', index=False)

print("Training...")
X_train = train.drop(columns=["price"])
y_train = train["price"]
X_test = test.drop(columns=["price"])
y_test = test["price"]
X_oot = oot.drop(columns=["price"])
y_oot = oot["price"]

model = CatBoostRegressor(
    learning_rate = 0.0168,
    iterations = 2000,
    verbose=0
    )

model.fit(X_train, y_train,
          cat_features=[X_train.columns.get_loc('address'),
          X_train.columns.get_loc('nearest_metro')])

print("Evaluating...")
y_train_pred_log = model.predict(X_train)
y_test_pred_log = model.predict(X_test)
y_oot_pred_log = model.predict(X_oot)

y_train_pred = np.exp(y_train_pred_log)
y_test_pred = np.exp(y_test_pred_log)
y_oot_pred = np.exp(y_oot_pred_log)

y_train_true = np.exp(y_train)
y_test_true = np.exp(y_test)
y_oot_true = np.exp(y_oot)

mae_train = mean_absolute_error(y_train_true, y_train_pred)
mape_train = mean_absolute_percentage_error(y_train_true, y_train_pred)

mae_test = mean_absolute_error(y_test_true, y_test_pred)
mape_test = mean_absolute_percentage_error(y_test_true, y_test_pred)

mae_oot = mean_absolute_error(y_oot_true, y_oot_pred)
mape_oot = mean_absolute_percentage_error(y_oot_true, y_oot_pred)

print("Finished...")
print(f"Train MAE: {mae_train:.4f} | MAPE: {mape_train:.4%}")
print(f"Test MAE:  {mae_test:.4f} | MAPE: {mape_test:.4%}")
print(f"OOT MAE:  {mae_oot:.4f} | MAPE: {mape_oot:.4%}")

train_test_difference = abs(mape_test - mape_train) * 100
test_oot_difference = abs(mape_oot - mape_test) * 100

if train_test_difference <= 0.2:
    print(f"✅ No overfit for train and test! Gap is {round(train_test_difference, 4)}")
else:
    print(f"⚠️ Overfit for train and test! Gap is {round(train_test_difference, 4)}")

if test_oot_difference <= 0.2:
    print(f"✅ No overfit for test and oot! Gap is {round(test_oot_difference, 4)}")
else:
    print(f"⚠️ Overfit for test and oot! Gap is {round(test_oot_difference, 4)}")

with open("./models/model.pkl", "wb") as f:
    pickle.dump(model, f)