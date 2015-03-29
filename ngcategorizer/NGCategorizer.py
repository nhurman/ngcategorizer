import os
import nltk
import pickle
import random
from functools import reduce

from .Mail import Mail

class NGCategorizer:
    def __init__(self, rootpath):
        self.rootpath = rootpath
        self.prune_frequencies = 20
        self.wfreqs = {}

    def exploreDirectory(self):
        """ Assumes the structure is {newsgroup_name}/{message_id}
            Returns a dict [newsgroup] => [id, id, id...]
        """
        groups = {}
        for groupname in os.listdir(self.rootpath):
            groups[groupname] = []
            dirpath = os.path.join(self.rootpath, groupname)
            if os.path.isdir(dirpath):
                for messageid in os.listdir(dirpath):
                    groups[groupname].append(messageid)
        return groups

    def parseMail(self, groupname, messageid):
        """ Parses the given message to extract the Mail
            object from the associated file
        """
        filepath = os.path.join(self.rootpath, groupname, messageid)
        mail = Mail()
        mail.id = messageid
        mail.group = groupname

        with open(filepath, encoding="iso-8859-1", errors="backslashreplace") as fp:
            inheaders = True
            content = []
            for line in fp:
                line = line.strip()
                if inheaders:
                    if line == "":
                        inheaders = False
                    else:
                        try:
                            name, value = line.split(':', 1)
                        except ValueError:
                            pass
                        if name == "Subject": mail.subject = value
                elif line != "":
                    content.append(line)

            mail.text = "\n".join(content)
        return mail

    def extractWords(self, mail):
        """ Extracts all the words from the mail """
        tokens = nltk.word_tokenize(mail.text)
        words = [w.lower() for w in tokens if all([c.isalnum() for c in w])]
        return words

    def filterWords(self, words):
        """ Filters words that are too small or in the stoplist """
        filtered = []
        stopwords = nltk.corpus.stopwords.words('english')
        stopwords.extend(["n't", "'re", "'ve", "'ll"])
        for w in words:
            if len(w) > 2 and not w in stopwords:
                filtered.append(w)
        return filtered

    def calculateFreq(self, words):
        """ Calculates the frequencies of each word """
        nb = len(words)
        prob = {w: (words.count(w) / nb) for w in words}
        return prob

    def parseMessage(self, group, messageid, prune = True):
        mail = self.parseMail(group, messageid)
        words = self.extractWords(mail)
        filtered = self.filterWords(words)
        freq = self.calculateFreq(filtered)

        # only keep top frequencies
        if prune:
            f = sorted(freq.items(), key=lambda x:x[1], reverse=True)
            nb = min(self.prune_frequencies, len(f))
            freq = dict(f[:nb])
        return freq

    def parseGroup(self, group, messages):
        freqs = {}
        nbMessage = len(messages)
        for messageid in messages:
            words = self.parseMessage(group, messageid)
            for w, f in words.items():
                if w in freqs:
                    freqs[w] += f
                else:
                    freqs[w] = f
        freqs = {w: (freqs[w]/nbMessage) for w in freqs}
        return freqs

    def parseGroups(self, groups):
        freqs = {}
        for group in groups:
            f = self.parseGroup(group, groups[group])
            freqs[group] = f

        wfreqs = {}
        for g in freqs:
            for w in freqs[g]:
                if w not in wfreqs:
                    wfreqs[w] = [(g, freqs[g][w])]
                else:
                    wfreqs[w].append((g, freqs[g][w]))
        self.wfreqs = wfreqs

    def categorize(self, group, messageid):
        freq = self.parseMessage(group, messageid, prune=False)
        groups = {}

        for word in freq:
            if word not in self.wfreqs:
                continue
            for (g, f) in self.wfreqs[word]:
                if g not in groups:
                    groups[g] = f * freq[word]
                else:
                    groups[g] += f * freq[word]

        groups = sorted(groups.items(), key=lambda x: x[1], reverse=True)
        if len(groups) == 0:
            return None
        return groups[0][0]

    def save(self, filepath):
        pickle.dump(self.wfreqs, open(filepath, "wb"))

    def load(self, filepath):
        self.wfreqs = pickle.load(open(filepath, "rb"))

    def splitSet(self, groups):
        messages = reduce(lambda a, b: a+b, [[(g, m) for m in groups[g]] for g in groups])
        random.shuffle(messages)

        # Keep 33% of messages for the testing set
        ratio_testing = 1/3
        nb = int(len(messages) * ratio_testing)

        testing = self.toDict(messages[:nb])
        training = self.toDict(messages[nb:])

        return (training, testing)

    def toDict(self, messages):
        out = {}
        for (g, m) in messages:
            if g not in out: out[g] = []
            out[g].append(m)
        return out