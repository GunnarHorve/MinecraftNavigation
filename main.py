import MalmoPython
import os
import sys
import time
import json
from levelMap import levelMap
import cPickle as pickle
import A_star

#world recording parameters
startPos = [252, 68, -214] # x,y,z
obsDims = [50,3,50] # [50, 3, 5]
mapping = False
numPillars = 2 #2
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

    startString = '<Placement x="{}" y="{}" z="{}" yaw="90"/>'.format(startPos[0]+.5, startPos[1], startPos[2]+.5)

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

def createTPLocs():
    print("calculating teleport locations")
    # unpack start position to useful data type (integer)
    x, y, z = startPos

    strtX = x - numPillars - obsDims[0]*2*numPillars
    stopX = x + numPillars + obsDims[0]*2*numPillars + 1
    stepX = obsDims[0] * 2 + 1

    strtY = y - numPlatfms - obsDims[1]*2*numPlatfms
    stopY = y + numPlatfms + obsDims[1]*2*numPlatfms + 1
    stepY = obsDims[1] * 2 + 1

    strtZ = z - numPillars - obsDims[2]*2*numPillars
    stopZ = z + numPillars + obsDims[2]*2*numPillars + 1
    stepZ = obsDims[2] * 2 + 1

    tplocs = []

    for i in range(strtX, stopX, stepX):
        for j in range(strtY, stopY, stepY):
            for k in range(strtZ, stopZ, stepZ):
                tplocs.append((i, j, k))

    return tplocs

def initMalmo():
    print("initializing malmo")
    # load the world
    missionXML = getMissionXML()
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    if(mapping):
        my_mission.setModeToSpectator()

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

    return agent_host

def samePoint(p1, p2):
    return int(p1[0]) == int(p2[0]) and int(p1[1]) == int(p2[1]) and int(p1[2]) == int(p2[2])

def waitForSensor(agent_host, tp):
    print "waiting for sensor at: {} {} {}".format(tp[0], tp[1], tp[2])
    while True:
        time.sleep(0.1)

        world_state = agent_host.getWorldState()
        if not world_state.number_of_observations_since_last_state > 0: continue

        # parse obsrvations
        msg = world_state.observations[-1].text
        obs = json.loads(msg)
        if(samePoint((obs[u'XPos'], obs[u'YPos'], obs[u'ZPos']), tp)):
            grid = obs.get(u'sliceObserver', 0)
            return grid

def makeMap(agent_host, tps):
    print("making map")
    # unpack start position to useful data type (integer)
    x, y, z = startPos

    minX = x - numPillars - obsDims[0]*(2*numPillars + 1)
    maxX = x + numPillars + obsDims[0]*(2*numPillars + 1)
    minY = y - numPlatfms - obsDims[1]*(2*numPlatfms + 1)
    maxY = y + numPlatfms + obsDims[1]*(2*numPlatfms + 1)
    minZ = z - numPillars - obsDims[2]*(2*numPillars + 1)
    maxZ = z + numPillars + obsDims[2]*(2*numPillars + 1)

    dataMap = levelMap(minX, minY, minZ, maxX, maxY, maxZ)

    for tp in tps:
            agent_host.sendCommand("tp {} {} {}".format(tp[0]+.5, tp[1], tp[2]+.5))
            grid = waitForSensor(agent_host, (tp[0]+.5, tp[1], tp[2]+.5))
            dataMap.observationDump(grid, tp, obsDims)

    dataMap.text2bool()
    return dataMap

def walkPath(agent_host, path):
    for step in path:
        print step
        if(step[0] == 1):
            agent_host.sendCommand("moveeast")
        elif step[0] == -1:
            agent_host.sendCommand("movewest")
        elif step[2] == 1:
            agent_host.sendCommand("movesouth")
        elif step[2] == -1:
            agent_host.sendCommand("movenorth")
        time.sleep(1/4.317) #walking speed

def main():
    # Loading world, initializing malmo
    agent_host = initMalmo()

    if(mapping):
        dataMap = makeMap(agent_host, createTPLocs())
        print("making pickles")
        pickle.dump(dataMap, open(saveFile, "wb"))
    else:
        searchTesting(agent_host)

def searchTesting(agent_host):
    #load saved map
    print("opening jar of pickles")
    dataMap = pickle.load(open("save.p", "rb"))
    print("begin testing in earnest")

    start = dataMap.indexFromPoint(startPos)
    dm = dataMap.getDepthMap()

    # run A* 40^2 times, each time to a different point
    t0 = time.time()
    count = 1
    for i in range(-200, 200, 10):
        for j in range(-200, 200, 10):
            tmp = dataMap.indexFromPoint((startPos[0] + i, startPos[1], startPos[2] + j))
            end = (tmp[0], dm[tmp[0]][tmp[2]], tmp[2])          #search goal (per for loops)

            t = time.time()                                     #store timestamp
            path = A_star.search(start, end, dataMap.data, 15)  #15 second timeout

            # print results thus far
            if(path):
                s = "{},{}:  |  Ellapsed: {:f}  |  Current:  {:f}  |  Percentage:  {:f}%  |"
                print s.format(i, j, time.time() - t0, time.time() - t, count/1600.)
            else:
                s = "{},{}:  |  Ellapsed: {:f}  |  TIME ELLAPSED  |  Percentage:  {:f}%  |"
                print s.format(i, j, time.time() - t0, count/1600.)
            count = count + 1



                # if path:
    #     walkPath(agent_host, path)
    # else:
    #     print("we didn't find shit")

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
main()
