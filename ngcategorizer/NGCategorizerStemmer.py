import sys
import Stemmer
from .NGCategorizer import NGCategorizer

class NGCategorizerStemmer(NGCategorizer):
    def __init__(self, rootpath):
        NGCategorizer.__init__(self, rootpath)
        self.stemmer = Stemmer.Stemmer('english')

    def stemWords(self, words):
        """ Reduces words to their stem """
        stemmed = []
        for w in words:
            stemmed.append(self.stemmer.stemWord(w))
        return stemmed

    def parseMessage(self, group, messageid, prune = True):
        mail = self.parseMail(group, messageid)
        words = self.extractWords(mail)
        filtered = self.filterWords(words)
        stemmed = self.stemWords(filtered)
        freq = self.calculateFreq(stemmed)

        # only keep top frequencies
        if prune:
            f = sorted(freq.items(), key=lambda x:x[1], reverse=True)
            nb = min(self.prune_frequencies, len(f))
            freq = dict(f[:nb])
        return freq
