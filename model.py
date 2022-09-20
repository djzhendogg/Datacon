import pandas as pd
import numpy as np
from sklearn import model_selection
from sklearn import metrics
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns

# upload data
database = "https://raw.githubusercontent.com/nikolaichem/datacon_hackathon/main/final_output.xlsx"
db = pd.read_excel(database, index_col=0)

# a bit of statistics
print("Brief statistics:")
print(db.describe())
# correlation matrix
correlation = db.corr()
fig1 = plt.figure(figsize=(10, 6), constrained_layout=True)
plt.title("Correlation matrix")
sns.heatmap(correlation)
# violin plots
fig2, ax_ = plt.subplots(5, 4, figsize=(12, 11))
ax = []
for i in ax_:
    ax += i.tolist()
for number, column in enumerate(db.columns):
    sns.violinplot(data=db, x=column, ax=ax[number])
fig2.suptitle("Violin plots for columns in db")
plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.3,
                    hspace=0.6)
plt.show()

# found outlying data in viability
print("Outlying viability: \n", db["Viability (%)"][db["Viability (%)"] > 500])
out_index = db[db["Viability (%)"] == db["Viability (%)"].max()].index
db.drop(out_index, inplace=True)
# violin plot for viability
fig3 = plt.figure(figsize=(10, 6), constrained_layout=True)
sns.violinplot(data=db["Viability (%)"], orient="h")
plt.title("Violin plot for viability without outlier data")
plt.show()

# categorical columns
category = ["Cell_type", "Coat", "Line_Primary_Cell", "Animal", "Cell_morphology", "Cell_age",
            "Cell_organ", "Test", "Elements"]
# minmax scaling
to_scale_df = db.drop(category, axis=1)
scaled_data = preprocessing.MinMaxScaler().fit_transform(to_scale_df)
scaled_df = pd.DataFrame(scaled_data, columns=to_scale_df.columns)
norm_df = scaled_df.merge(db[category], right_index=True, left_index=True)
# statistics for scaled data
print("Scaled db statistics: \n", norm_df.describe())
fig4, ax_ = plt.subplots(5, 4, figsize=(12, 11))
ax = []
for i in ax_:
    ax += i.tolist()
for number, column in enumerate(norm_df.columns):
    sns.violinplot(data=norm_df, x=column, ax=ax[number])
fig4.suptitle("Violin plots for columns in scaled db")
plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.3,
                    hspace=0.6)
plt.show()

# split data on describers and response
x = norm_df.drop("Viability (%)", axis=1)
y = norm_df["Viability (%)"]

# split data
x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, random_state=324, test_size=0.2)

# evaluate the shape of split data
print("Evaluation of data shape after split: \n", x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)

# grid search for RandomForestRegressor
forest_param = {
    "n_estimators": [20, 50, 70],
    "min_samples_leaf": [5, 7, 9],
    "min_samples_split": [4, 5, 7],
    "max_features": ["sqrt", "log2"],
    "bootstrap": [True, False]
}
forest_grid = model_selection.GridSearchCV(RandomForestRegressor(), param_grid=forest_param, cv=5)
forest_grid.fit(x_train, y_train)
forest_best_params = forest_grid.best_params_
print("RandomForestRegressor best score during the grid search: \n", forest_grid.best_score_)
print("RandomForestRegressor best parameters during the grid search: \n", forest_best_params)

# RandomForestRegressor evaluation
forest_model = RandomForestRegressor(**forest_best_params)
forest_model.fit(x_train, y_train)

# hold-out cross-validation
forest_predict = forest_model.predict(x_test)
forest_mse = metrics.mean_squared_error(y_true=y_test, y_pred=forest_predict)
print("RandomForestRegressor MSE: \n", forest_mse)
# plot for hold-out cross-validation
fig5 = plt.figure(figsize=(10, 10), constrained_layout=True)
sns.scatterplot(y_test, forest_predict)
plt.title("RandomForestRegressor hold-out cross-validation result")
plt.xlabel("real")
plt.ylabel("predict")


# feature importance
features = forest_model.feature_names_in_
importance = forest_model.feature_importances_
indices = np.argsort(importance)
fig6 = plt.figure(figsize=(10, 6), constrained_layout=True)
plt.title("RandomForestRegressor feature importance")
plt.barh(range(len(indices)), importance[indices], color="#8f63f4", align="center")
plt.yticks(range(len(indices)), features[indices])
plt.xlabel("Relative Importance")
plt.show()

# 5-fold cross-validation
forest_cross_val_pred = model_selection.cross_val_predict(RandomForestRegressor(**forest_best_params),
                                                          x_train, y_train, cv=5)
forest_cross_val_score = model_selection.cross_val_score(RandomForestRegressor(**forest_best_params),
                                                         x_train, y_train, cv=5)
forest_cross_val_score = sum(forest_cross_val_score) / len(forest_cross_val_score)
forest_cross_val_mse = metrics.mean_squared_error(y_true=y_train, y_pred=forest_cross_val_pred)
print("RandomForestRegressor 5-fold cross-validation mean score: \n", forest_cross_val_score)
print("RandomForestRegressor 5-fold cross-validation MSE result: \n", forest_cross_val_mse)
# RandomForestRegressor 5-fold cross-validation plots
fig7 = plt.figure(figsize=(10, 10), constrained_layout=True)
sns.scatterplot(y_train, forest_cross_val_pred)
plt.title("RandomForestRegressor 5-fold cross-validation result")
plt.xlabel("real")
plt.ylabel("predict")
plt.show()

# check over-fitting
sns.set(style="darkgrid")
fig8 = plt.figure(figsize=(20, 15))
ax = plt.axes(projection="3d")

x=norm_df["Concentration (g/L)"]
y=norm_df["Electronegativity"]
z=norm_df["Viability (%)"]

ax.scatter3D(x, y, z, color="blue", label="data")
ax.set_title("Check over-fitting", pad=25, size=15)
ax.set_xlabel("Concentration (g/L)")
ax.set_ylabel("Electronegativity")
ax.set_zlabel("Viability (%)")

ax.plot3D(norm_df["Concentration (g/L)"].sort_values(), norm_df["Electronegativity"].sort_values(),
          forest_model.predict(norm_df.drop("Viability (%)", axis=1).sort_values(by=["Concentration (g/L)",
                                                                                     "Electronegativity"])),
          color="red", label="model", linewidth=2)

plt.legend()
plt.show()
