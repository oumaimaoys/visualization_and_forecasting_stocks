from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import yahooquery as yq
import numpy as np


def svr_model(n, stock_code, column):
    # get the stock data
    df = yq.Ticker(stock_code).history(period="300d", interval="1d")
    df = df[[column]]

    # a variable for predicting "n" days out in the future
    forecast_out = n

    # create another column (the target) shifted "n" units up
    df['prediction'] = df[[column]].shift(-forecast_out)

    # create the independent data set X
    X = np.array(df.drop(['prediction'], axis=1))

    # remove the last n rows
    X = X[:-forecast_out]  # x is a list of lists

    # create the dependant data set y
    y = np.array(df['prediction'])

    # get all the y values except the last n rows
    y = y[:-forecast_out]  # y is a list

    # split the data 9:1
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # create and train the support vector machine (regressor)
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    # svr_rbf.fit(x_train, y_train)

    # testing model : score returns the coefficient of determination R² of the preduction
    # the best possible score is 1.0
    # svm_confidence = svr_rbf.score(x_test, y_test)

    # tuning hyper-parameters
    gsc = GridSearchCV(
        svr_rbf,
        param_grid={
            'C': [0.1, 1, 10, 100, 1000],
            'epsilon': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 10],
            'gamma': [0.0001, 0.001, 0.005, 0.1, 1, 3, 5, 10]
        },
        cv=5,
        scoring='neg_mean_squared_error',
        verbose=0,
        n_jobs=-1
    )

    gsc.fit(x_train, y_train)
    best_params = gsc.best_params_
    best_svr = SVR(kernel='rbf', C=best_params["C"], epsilon=best_params["epsilon"], gamma=best_params["gamma"],
                   coef0=0.1, shrinking=True,
                   tol=0.001, cache_size=200, verbose=False, max_iter=-1)

    best_svr.fit(x_train, y_train)

    x_forecast = np.array(df.drop(['prediction'], axis=1)[-forecast_out:])
    y_pred = best_svr.predict(x_forecast)

    return y_pred



