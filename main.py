import MalmoPython
import os
import sys
import time
import json
from levelMap import levelMap
import cPickle as pickle
import A_star

#world recording parameters
startPos = [252.5, 68.0, -214.5] # x,y,z
obsDims = [10,3,10] # [50, 3, 5]
mapping = False
numPillars = 2 #2     #spaces observed = -O3--O2--O1--O2--O3-
numPlatfms = 3 #3
saveFile = "save.p"

def getMissionXML():
    print("creating mission xml")
    obsString = ""
    if(mapping):
        open = '<ObservationFromGrid><Grid name="sliceObserver">'
        min = '<min x="{}" y="{}" z="{}"/>'.format(-obsDims[0], -obsDims[1], -obsDims[2])
        max = '<max x="{}" y="{}" z="{}"/>'.format(obsDims[0], obsDims[1], obsDims[2])
        end = '</Grid></ObservationFromGrid>'
        obsString = open + min + max + end

    startString = '<Placement x="{}" y="{}" z="{}" yaw="90"/>'.format(startPos[0], startPos[1], startPos[2])

    return '''<?xml version="1.0" encoding="UTF-8" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

      <About>
        <Summary>Hello world!</Summary>
      </About>

      <ServerSection>
        <ServerHandlers>
          <DefaultWorldGenerator seed="1680538402529060016" forceReset="false" />
          <ServerQuitWhenAnyAgentFinishes/>
        </ServerHandlers>
      </ServerSection>

      <AgentSection mode="Creative">
        <Name>MalmoTutorialBot</Name>
        <AgentStart>''' + startString + '''
        </AgentStart>
        <AgentHandlers>''' + obsString +'''
          <ObservationFromFullStats/>
            <AbsoluteMovementCommands />
            <DiscreteMovementCommands autoFall="true" autoJump="true"/>
        </AgentHandlers>
      </AgentSection>
    </Mission>'''

def createTPLocs(my_mission):
    print("calculating teleport locations")
    # unpack start position to useful data type (integer)
    x, y, z = map(int, startPos)
    if(x < 0): x = x - 1
    if(z < 0): z = z - 1

    strtX = x - numPillars - obsDims[0]*2*numPillars
    stopX = x + numPillars + obsDims[0]*2*numPillars + 1
    stepX = obsDims[0] * 2 + 1

    strtY = y - numPlatfms - obsDims[1]*2*numPlatfms
    stopY = y + numPlatfms + obsDims[1]*2*numPlatfms + 1
    stepY = obsDims[1] * 2 + 1

    strtZ = z - numPillars - obsDims[2]*2*numPillars
    stopZ = z + numPillars + obsDims[2]*2*numPillars + 1
    stepZ = obsDims[2] * 2 + 1

    tplocs = [[[(0,0,0) for k in xrange(2*numPillars + 1)] for j in xrange(2*numPlatfms + 1)] for i in xrange(2*numPillars + 1)]

    x = 0
    for i in range(strtX, stopX, stepX):
        y = 0
        for j in range(strtY, stopY, stepY):
            z = 0
            for k in range(strtZ, stopZ, stepZ):
                tplocs[x][y][z] = (i+.5, j, k+.5)
                z = z + 1
            y = y + 1
        x = x + 1

    return tplocs

def initMalmo():
    print("initializing malmo")
    # load the world
    missionXML = getMissionXML()
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    if(mapping):
        my_mission.setModeToSpectator()
        tps = createTPLocs(my_mission)
    else:
        tps = -1

    # create default malmo objects
    agent_host = MalmoPython.AgentHost()
    my_mission_record = MalmoPython.MissionRecordSpec()

    # Attempt to start a mission:
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission( my_mission, my_mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print "Error starting mission:",e
                exit(1)
            else:
                time.sleep(2)

    # Loop until mission starts:
    print "Waiting for the mission to start ",
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print "Error:",error.text

    print
    print "Mission running "

    return (agent_host, world_state, tps)

def samePoint(p1, p2):
    return int(p1[0]) == int(p2[0]) and int(p1[1]) == int(p2[1]) and int(p1[2]) == int(p2[2])

def waitForSensor(agent_host, tp):
    print "waiting for sensor at: {} {} {}".format(tp[0], tp[1], tp[2])
    while True:
        sys.stdout.write(".")
        time.sleep(0.1)

        world_state = agent_host.getWorldState()
        if not world_state.number_of_observations_since_last_state > 0: continue

        # parse obsrvations
        msg = world_state.observations[-1].text
        obs = json.loads(msg)
        if(samePoint((obs[u'XPos'], obs[u'YPos'], obs[u'ZPos']), tp)):
            grid = obs.get(u'sliceObserver', 0)
            return grid

def makeMap(agent_host, world_state, tps):
    print("making map")
    # unpack start position to useful data type (integer)
    x, y, z = map(int, startPos)

    minX = x - numPillars - obsDims[0]*(2*numPillars + 1)
    maxX = x + numPillars + obsDims[0]*(2*numPillars + 1)
    minY = y - numPlatfms - obsDims[1]*(2*numPlatfms + 1)
    maxY = y + numPlatfms + obsDims[1]*(2*numPlatfms + 1)
    minZ = z - numPillars - obsDims[2]*(2*numPillars + 1)
    maxZ = z + numPillars + obsDims[2]*(2*numPillars + 1)

    dataMap = levelMap(minX, minY, minZ, maxX, maxY, maxZ)
    print(dataMap.getSize())

    for i in range(len(tps)):
        for j in range(len(tps[0])):
            for k in range(len(tps[0][0])):
                tp = tps[i][j][k]
                agent_host.sendCommand("tp {} {} {}".format(tp[0], tp[1], tp[2]))
                grid = waitForSensor(agent_host, tp)
                dataMap.observationDump(grid, tp, obsDims)
    dataMap.text2bool()
    print("making pickles")
    pickle.dump(dataMap, open(saveFile, "wb"))
    print("finished creating and saving map")

def preSearchSanitize(point):
    x, y, z = map(int, point)
    if(x < 0): x = x - 1
    if(z < 0): z = z - 1
    return (x,y,z)

def walkPath(agent_host, path):
    commands = [["movenorth","movesouth"],["movewest","moveeast"]]
    for i in range(len(path)):
        step = path[i]
        agent_host.sendCommand(commands[step[0]][step[2]])
        time.sleep(1/4.317)

def runSearch(agent_host, dataMap):
    print("running search")
    start = dataMap.indexFromPoint(preSearchSanitize(startPos))
    end = preSearchSanitize((217.5, 67.0, -203.5))
    end = dataMap.indexFromPoint(end)
    path = A_star.search(start, end, dataMap.data)

    walkPath(agent_host, path)

def main():
    # Loading world, initializing malmo
    agent_host, world_state, tps = initMalmo()

    if(mapping):
        makeMap(agent_host, world_state, tps)
    else:
        print("opening jar of pickles")
        dataMap = pickle.load(open( "save.p", "rb"))
        runSearch(agent_host, dataMap)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
main()
