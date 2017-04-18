class levelMap:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ):
        self.minX = minX
        self.minY = minY
        self.minZ = minZ
        self.maxX = maxX
        self.maxY = maxY
        self.maxZ = maxZ

        self.debugPrint()

    def debugPrint():
        tmp = "size [x][y][z]: {} {} {}".format(self.maxX - self.minX, self.maxY - self.minY, self.maxZ - self.minZ)

#    textMap = [[["" for k in xrange(2*numPillars + 1)] for j in xrange(2*numPlatforms + 1)] for i in xrange(2*numPillars + 1)]
