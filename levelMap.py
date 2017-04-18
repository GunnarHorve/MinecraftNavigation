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
        self.xLen = self.maxX - self.minX + 1
        self.yLen = self.maxY - self.minY + 1
        self.zLen = self.maxZ - self.minZ + 1

        self.data = [[["" for k in xrange(self.zLen)] for j in xrange(self.yLen)] for i in xrange(self.xLen)]

    def debugPrint(self):
        # size = "size [x][y][z]: {} {} {}".format(len(self.data), len(self.data[0]), len(self.data[0][0]))
        # mins = "mins [x][y][z]: {} {} {}".format(self.minX, self.minY, self.minZ)
        # maxs = "maxs [x][y][z]: {} {} {}".format(self.maxX, self.maxY, self.maxZ)
        # import pprint
        # pprint.pprint(self.data)
        for i in range(len(self.data)):
            for j in range(len(self.data[0])):
                for k in range(len(self.data[0][0])):
                    print(self.data[i][j][k])
                    if self.data[i][j][k] == "":
                        print("you done fucked up now {} {} {}".format(i,j,k))
        return

    def insert(self, val, x, y, z):
        xPos = self.xLen - (self.maxX - x) - 1
        yPos = self.yLen - (self.maxY - y) - 1
        zPos = self.zLen - (self.maxZ - z) - 1
        self.data[xPos][yPos][zPos] = val
        # print val

    # note:  variables in this section (sans x,y,z) are relative to the observation
    def observationDump(self, obs, tp, obsDims):
        x, y, z = map(int, tp)
        if(x < 0): x = x - 1
        if(z < 0): z = z - 1

        xMin = x - obsDims[0]
        yMin = y - obsDims[1]
        zMin = z - obsDims[2]
        xLen = 1 + 2*obsDims[0]
        zLen = 1 + 2*obsDims[2]

        for i in range(len(obs)):
            x = xMin +  i %  (xLen)
            y = yMin +  i // (xLen*zLen)
            z = zMin + (i // (xLen)) % zLen

            self.insert(obs[i], x, y, z)
            # print(x,y,z, self.minX, self.minY, self.minZ, self.maxX, self.maxY, self.maxZ)
