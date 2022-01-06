import pickle
from collections import defaultdict
import time

from . import features
from . import skgmm


class ModelInterface:

    def __init__(self):
        self.features = defaultdict(list)
        self.gmmset = skgmm.GMMSet()

    def enroll(self, name, fs, signal):
        feat = features.get_feature(fs, signal)
        self.features[name].extend(feat)

    def train(self):
        self.gmmset = skgmm.GMMSet()
        start_time = time.time()
        for name, feats in self.features.items():
            try:
                self.gmmset.fit_new(feats, name)
            except Exception as e :
                print ("%s failed"%(name))
        print (time.time() - start_time, " seconds")

    def dump(self, fname):
        """ dump all models to file"""
        self.gmmset.before_pickle()
        with open(fname, 'wb') as f:
            pickle.dump(self, f, -1)
        self.gmmset.after_pickle()

    def predict(self, fs, signal):
        """
        return a label (name)
        """
        try:
            feat = features.get_feature(fs, signal)
        except Exception as e:
            print(e)
        return self.gmmset.predict_one(feat)

    @staticmethod
    def load(fname):
        """ load from a dumped model file"""
        with open(fname, 'rb') as f:
            R = pickle.load(f)
            R.gmmset.after_pickle()
        return R
