#!/usr/bin/env python3

import os
from ngcategorizer.NGCategorizer import NGCategorizer
from ngcategorizer.PerformanceEvaluator import PerformanceEvaluator

ng = NGCategorizer('Sujet/20_newsgroups')
save_path = "Tests/wfreqs-training.p"
groups = ng.exploreDirectory()
training, testing = ng.splitSet(groups)

if os.path.exists(save_path):
    ng.load(save_path)
else:
    ng.parseGroups(training)
    ng.save(save_path)

perf = PerformanceEvaluator(ng)
perf.evaluate(testing)