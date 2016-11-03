# Aueshor : Karan Singla

import numpy as np  # Make sure that numpy is imported
import time
import sys

from sklearn.externals import joblib
from sklearn import cluster
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.ensemble import BaggingClassifier
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import pairwise_distances
from sklearn import metrics
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline,Pipeline
from sklearn.preprocessing import Normalizer
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster.k_means_ import euclidean_distances
from scipy.sparse import *
from sklearn import metrics
from sklearn.svm import SVC

## library imports
from gensim.models import Word2Vec
from gensim import corpora, models, similarities
from gensim.models.doc2vec import TaggedDocument, LabeledSentence, Doc2Vec



''' Class WordClusters trains a word2vec model and also runs k-means clustering '''
class WordClusters(object):
    def __init__(self,data,model_name,num_features=100,min_count = 5):

        self.data = data
        self.model_name = model_name
        self.num_features = num_features
        self.min_count = min_count

    
    def word_mapper(self,output,context=5):
        ## Creates mapping of words to Word2Vec based cluster ID's
        # train Word2Vec model
        self.word2vec_train(self.data,self.model_name,num_features=self.num_features,min_count=self.min_count,context=context)


        # Do k-means clustering and create a mapping
        mapping = self.cluster_word2vec(self.model_name)
        out = open(output,'w')
        for item in mapping:
            out.write(str(item)+"\t"+str(mapping[item])+"\n")
        out.close()

    def word2vec_train(self,data,model_name,num_features=200,min_count=1,num_workers=15,\
        context=5,downsampling=1e-3):
        # Set values for various parameters
        
        #num_features : Word vector dimensionality
        #min_word_count : Minimum word count
        #num_workers : Number of threads to run in parallel
        #context : Context window size
        #downsampling : Downsample setting for frequent words
        input_data = []
        for i in data:
            input_data.append(i.split())
        print "Word2Vec model and saving it to ",model_name
        # Initialize and train the model (this will take some time)
        model = Word2Vec(sentences=input_data, workers=num_workers, \
                size=num_features, min_count = min_count, \
                window = context, sample = downsampling, seed=1)

        # If you don't plan to train the model any further, calling
        # init_sims will make the model much more memory-efficient.
        model.init_sims(replace=True)

        # It can be helpful to create a meaningful model name and
        # save the model for later use. You can load it later using Word2Vec.load()
        model.save(model_name)

        print "Model trained and saved"

    def cluster_word2vec(self,model_name):

        print "Clustering the Vectors and saving mapping to ",model_name
        model = Word2Vec.load(model_name)
        # ****** Run k-means on the word vectors and print a few clusters

        start = time.time() # Start time
        # Set "k" (num_clusters) to be 1/5th of the vocabulary size, or an
        # average of 5 words per cluster
        word_vectors = model.syn0
        num_clusters = word_vectors.shape[0] / 5
        
        # Initalize a k-means object and use it to extract centroids
#        logging.info("\nRunning K means")
        kmeans_clustering = MiniBatchKMeans( n_clusters = num_clusters )
        idx = kmeans_clustering.fit_predict( word_vectors )

        # Get the end time and print how long the process took
        end = time.time()
        elapsed = end - start
#        logging.info("Time taken for K Means clustering: ", elapsed, "seconds.")

        # Create a Word / Index dictionary, mapping each vocabulary word to
        # a cluster number

        word_centroid_map = dict(zip( model.index2word, idx ))
        return word_centroid_map

def word_mappings(file):
        ''' use the monolingual model, train word2vec, do KNN and generate word mapping '''
        data = open(file,'r').readlines()

        model_name = "english.vec"
        mapping = "en.map"
        clusters = WordClusters(data,model_name,num_features=100,min_count = 5)
        clusters.word_mapper(mapping)


if __name__ == "__main__":

    word_mappings(sys.argv[1])

            
