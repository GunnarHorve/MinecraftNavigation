class levelMap:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ):
        # given
        self.minX = minX
        self.minY = minY
        self.minZ = minZ
        self.maxX = maxX
        self.maxY = maxY
        self.maxZ = maxZ

        # derived
        self.xLen = self.maxX - self.minX
        self.yLen = self.maxY - self.minY
        self.zLen = self.maxZ - self.minZ

        self.data = [[["" for k in xrange(self.zLen)] for j in xrange(self.yLen)] for i in xrange(self.xLen)]
        self.debugPrint()

    def debugPrint(self):
        size = "size [x][y][z]: {} {} {}".format(len(self.data), len(self.data[0]), len(self.data[0][0]))
        mins = "mins [x][y][z]: {} {} {}".format(self.minX, self.minY, self.minZ)
        maxs = "maxs [x][y][z]: {} {} {}".format(self.maxX, self.maxY, self.maxZ)
        print size
        print mins
        print maxs

    def observationDump(self, obs, tp, obsDims):
        x, y, z = map(int, tp)
        if(x < 0): x = x - 1
        if(z < 0): z = z - 1

        print "You've given me an array of length {}.  The hell do I do with this?".format(len(obs))
