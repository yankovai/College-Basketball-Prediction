import numpy as np
from sklearn import cross_validation as cv
from sklearn import preprocessing

class Make_Predictions(object):
	"""
	Applies machine learning techniques to the scraped colleged basketball data
	and uses the resulting model to make predictions on unplayed games.
	"""

	def __init__(self):
		raise NotImplementedError

	def train_logistic_regression(self):
		"""
		"""

	def create_train_test_sets(self, X, y, test_size = 0.4,):
		"""
		"""

		X_train, X_test, y_train, y_test = cv.train_test_split(X, y, test_size = test_size, random_state = 0)

		return X_train, X_test, y_train, y_test 

	def make_prediction(self):
		raise NotImplementedError

	def scale_features(self, X):
		"""
		"""

		X_scaled = preprocessing.scale(X)

		return X_scaled




