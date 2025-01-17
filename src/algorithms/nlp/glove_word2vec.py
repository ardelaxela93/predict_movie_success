import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

with open("../../../data/glove.6B.50d.txt", "rb") as lines:
	w2v = {line.split()[0]: np.array(map(float, line.split()[1:]))
		   for line in lines}


class MeanEmbeddingVectorizer(object):
	def __init__(self, word2vec):
		self.word2vec = word2vec
		# if a text is empty we should return a vector of zeros
		# with the same dimensionality as all the other vectors
		self.dim = len(word2vec.itervalues().next())

	def fit(self, X, y):
		return self

	def transform(self, X):
		return np.array([
							np.mean([self.word2vec[w] for w in words if w in self.word2vec]
									or [np.zeros(self.dim)], axis=0)
							for words in X
							])

class TfidfEmbeddingVectorizer(object):
	def __init__(self, word2vec):
		self.word2vec = word2vec
		self.word2weight = None
		self.dim = len(word2vec.itervalues().next())

	def fit(self, X, y):
		tfidf = TfidfVectorizer(analyzer=lambda x: x)
		tfidf.fit(X)
		# if a word was never seen - it must be at least as infrequent
		# as any of the known words - so the default idf is the max of
		# known idf's
		max_idf = max(tfidf.idf_)
		self.word2weight = defaultdict(
			lambda: max_idf,
			[(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])

		return self

	def transform(self, X):
		return np.array([
				np.mean([self.word2vec[w] * self.word2weight[w]
						 for w in words if w in self.word2vec] or
						[np.zeros(self.dim)], axis=0)
				for words in X
			])