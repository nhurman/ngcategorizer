class PerformanceEvaluator:
    def __init__(self, ng):
        self.ng = ng

    def evaluate(self, groups):
        overallSuccess = 0
        overallCount = 0
        for g in groups:
            print("-- Testing group {}".format(g))
            success = 0

            for message in groups[g]:
                c = self.ng.categorize(g, message)
                if c == g:
                    success += 1

            overallSuccess += success
            overallCount += len(groups[g])
            ratio = int(round(100 * success / len(groups[g]), 0))
            print("Success ratio: {}% ({}/{})".format(
                ratio, success, len(groups[g])))

        ratio = round(100 * overallSuccess / overallCount, 2)
        print("\n== OVERALL STATS")
        print("Success ratio: {}% ({}/{})".format(
                ratio, overallSuccess, overallCount))
