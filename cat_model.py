import pip._internal

packages = ('pandas', 'numpy', 'catboost', 'seaborn', 'matplotlib', 'sklearn')
for package in packages:
    try:
        __import__(package)
    except ImportError:
        pip._internal.main(["install", package.split()[0]])

import pandas as pd
import numpy as np
from catboost import CatBoostRegressor

pd.set_option("display.max_columns", None)
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn import metrics
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from catboost import Pool, cv

db = pd.read_excel('https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/final_output.xlsx')
db = db.drop('Unnamed: 0', axis=1)
out_index = db[db["Viability (%)"] == db["Viability (%)"].max()].index
db.drop(out_index, inplace=True)

category = ["Cell_type", "Coat", "Line_Primary_Cell", "Animal", "Cell_morphology", "Cell_age",
            "Cell_organ", "Test", "Test_indicator", 'Elements']

# нормализация датафрэйма
to_scale_df = db.drop(category, axis=1)
scaled_data = preprocessing.MinMaxScaler().fit_transform(to_scale_df)
scaled_df = pd.DataFrame(scaled_data, columns=to_scale_df.columns)
norm_df = scaled_df.merge(db[category], right_index=True, left_index=True)

# разделяем таргет и фичи
X_norm = norm_df.drop('Viability (%)', axis=1)
y_norm = norm_df['Viability (%)']

# отделяем train и test
X_train_norm, X_validation_norm, y_train_norm, y_validation_norm = train_test_split(X_norm, y_norm)

# основная цель при работе с catboost - это поиск оптимального колическтва итераций,
# для этого мы решили использовать встроенные в catboost
# методы детекции overfitting'а
tunned_model_norm_1 = CatBoostRegressor(
    random_seed=1000,
    iterations=12000,
    learning_rate=0.03,
    bagging_temperature=1.1,
    leaf_estimation_iterations=10,
    early_stopping_rounds=11,

)
tunned_model_norm_1.fit(
    X_train_norm, y_train_norm,
    cat_features=range(6, 16),
    logging_level='Silent',
    eval_set=(X_train_norm, y_train_norm),
    plot=False
)

# в финальной моделе мы используем весь доступный датасет,
# а ранее найденное оптимальное количество итераций домножается на 1.15 т.к. оно
# было найдено на меньшем датасэте => чтобы модель точно дообучилась потребуется чуть больше итераций.
# Число 1.15 было взято из лекций яндекса по практическуму применению catboost
best_model = CatBoostRegressor(
    random_seed=1000,
    iterations=int(tunned_model_norm_1.tree_count_ * 1.15),
    learning_rate=0.03,
    bagging_temperature=1.1,
    leaf_estimation_iterations=10,

)
best_model.fit(
    X_norm, y_norm,
    cat_features=range(6, 16),
    logging_level='Silent',
    plot=False
)

print('Best score:', best_model.get_best_score())

sns.scatterplot(best_model.predict(X_norm), y_norm)
plt.title("CatBoostRegressor results")
plt.xlabel("predicted")
plt.ylabel("real")
plt.show()
