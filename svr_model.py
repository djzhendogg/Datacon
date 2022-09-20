import pandas as pd
from sklearn import model_selection
from sklearn import metrics
from sklearn import preprocessing
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import StackingRegressor
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
fig3 = plt.figure(figsize=(10, 6))
sns.violinplot(data=db["Viability (%)"], orient="h")
plt.title("Violin plot for viability without outlier data")
plt.show()

# categorical columns
category = ["Cell_type", "Coat", "Line_Primary_Cell", "Animal", "Cell_morphology", "Cell_age",
            "Cell_organ", "Test"]
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

x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, random_state=84, test_size=0.2)

# grid search for SVR
svr_param = {
    "kernel": ["linear"],
    "gamma": ["scale", "auto"],
    "max_iter": [250, 300, 350],
    "epsilon": [0.6, 0.8, 1.0],
    "shrinking": [False, True]
}

svr_grid_clf = model_selection.GridSearchCV(SVR(), param_grid=svr_param, cv=5)
svr_grid_clf.fit(x_train, y_train)
svr_best_param = svr_grid_clf.best_params_
print("SVR best score:\n", svr_grid_clf.best_score_)
print("SVR best parameters:\n", svr_grid_clf.best_params_)

# SVR estimation
svr_clf = SVR(**svr_best_param)
svr_clf.fit(x_train, y_train)
predict = svr_clf.predict(x_test)
svr_mse = metrics.mean_squared_error(y_test, predict)
print("SVR mse: \n", svr_mse)

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

# Stacking
estims2 = [('svr', svr_clf), ('forest', forest_model)]
stack_clf = StackingRegressor(estimators=estims2, cv=5)
stack_clf.fit(x_train, y_train)
stack_clf_pred = stack_clf.predict(x_test)
stack_clf_mse = metrics.mean_squared_error(y_test, stack_clf_pred)
print("Stacking mse: \n", stack_clf_mse)
fig5 = plt.figure(figsize=(10,10))
sns.scatterplot(y_test, stack_clf_pred)
plt.title("Stacking hold-out cross-validation")
plt.xlabel("real")
plt.ylabel("predict")
plt.show()

# cross-validation
stack_cross_val_pred = model_selection.cross_val_predict(stack_clf, x_train, y_train, cv=5)
stack_cross_val_mse = metrics.mean_squared_error(y_true=y_train, y_pred=stack_cross_val_pred)
print("Stacking cross-validation MSE:\n", stack_cross_val_mse)
fig6 = plt.figure(figsize=(10, 10))
sns.scatterplot(y_train, stack_cross_val_pred)
plt.title("Stacking 5-fold cross-validation result")
plt.xlabel("real")
plt.ylabel("predict")
plt.show()

