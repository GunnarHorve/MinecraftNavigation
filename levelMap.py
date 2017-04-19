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

    def getSize(self):
        return (len(self.data), len(self.data[0]), len(self.data[0][0]))

    def debugPrint(self):
        import pprint
        pprint.pprint(self.data)

    def indexFromPoint(self, point):
        x, y, z = map(int, point)
        xPos = self.xLen - (self.maxX - x) - 1
        yPos = self.yLen - (self.maxY - y) - 1
        zPos = self.zLen - (self.maxZ - z) - 1
        return (xPos, yPos, zPos)

    def insert(self, val, x, y, z):
        index = self.indexFromPoint((x,y,z))
        self.data[index[0]][index[1]][index[2]] = val

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

    def text2bool(self):
        print("converting string array into boolean array")
        tmp = [[[0 for k in xrange(self.zLen)] for j in xrange(self.yLen)] for i in xrange(self.xLen)]

        size = self.getSize()
        for x in range(1,size[0]-1):
            for y in range(1,size[1]-1):
                for z in range(1,size[2]-1):
                    bot = self.data[x][y-1][z]
                    cur = self.data[x][y][z]
                    top = self.data[x][y+1][z]

                    if(cur == "air" and top == "air" and bot != "air"):
                        tmp[x][y][z] = 1
        self.data = tmp
