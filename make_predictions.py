import numpy as np
from sklearn import cross_validation as cv
from sklearn import linear_model
from sklearn import preprocessing

class Make_Predictions(object):
    """
    Applies machine learning techniques to the scraped colleged basketball data
    and uses the resulting model to make predictions on unplayed games.
    """

    def __init__(self, feature_file):
        data = np.load(feature_file)
        self.X = data['X']
        self.y = data['y']
          
    def train_logistic_regression(self):
        """
        """

    def create_train_test_sets(self, test_size = 0.4,):
        """
        """

        X0, X1, y0, y1 = cv.train_test_split(self.X, self.y, test_size = test_size, random_state = 0)
        self.X_train = X0
        self.X_test = X1
        self.y_train = y0
        self.y_test = y1

    def make_prediction(self):
        raise NotImplementedError

    def scale_features(self, X):
        """
        """

        X_scaled = preprocessing.scale(X)
        return X_scaled

#mp = Make_Predictions('features.npz')


data = np.load('features.npz')
X = data['X']
y = data['y']

X_scaled = preprocessing.scale(X)

logreg = linear_model.LogisticRegression()

scores = cv.cross_val_score(logreg, X_scaled, y, cv = 10)
print scores.mean(), scores.std()




