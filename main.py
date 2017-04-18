import MalmoPython
import os
import sys
import time
import json

def getMissionXML(mapping, start, obs):
    obsString = ""
    if(mapping):
        open = '<ObservationFromGrid><Grid name="sliceObserver">'
        min = '<min x="{}" y="{}" z="{}"/>'.format(-obs[0], -obs[1], -obs[2])
        max = '<max x="{}" y="{}" z="{}"/>'.format(obs[0], obs[1], obs[2])
        end = '</Grid></ObservationFromGrid>'
        obsString = open + min + max + end

    startString = '<Placement x="{}" y="{}" z="{}" yaw="{}"/>'.format(start[0], start[1], start[2], start[3])

    return '''<?xml version="1.0" encoding="UTF-8" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

      <About>
        <Summary>Hello world!</Summary>
      </About>

      <ServerSection>
        <ServerHandlers>
          <DefaultWorldGenerator seed="1680538402529060016" forceReset="true" />
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

def createTPLocs(my_mission, startPos, obsDims, numPillars, numPlatfms):
    # unpack start position to useful data type (integer)
    x, y, z, _ = map(int, startPos)
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

def initMalmo(mapping, startPos, obsDims, numPillars, numPlatfms):
    # load the world
    missionXML = getMissionXML(mapping, startPos, obsDims)
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    if(mapping):
        my_mission.setModeToSpectator()
        tps = createTPLocs(my_mission, startPos, obsDims, numPillars, numPlatfms)
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
    sys.stdout.write("waiting for sensor at: {} {} {}".format(tp[0], tp[1], tp[2]))
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

def makeMap(agent_host, world_state, tps, startPos, obsDims, numPillars, numPlatfms):
    # unpack start position to useful data type (integer)
    x, y, z, _ = map(int, startPos)
    if(x < 0): x = x - 1
    if(z < 0): z = z - 1

    minX = x - numPillars - obsDims[0]*(2*numPillars + 1)
    maxX = x + numPillars + obsDims[0]*(2*numPillars + 1) + 1
    minY = y - numPlatfms - obsDims[1]*(2*numPlatfms + 1)
    maxY = y + numPlatfms + obsDims[1]*(2*numPlatfms + 1) + 1
    minZ = z - numPlatfms - obsDims[2]*(2*numPillars + 1)
    maxZ = z + numPlatfms + obsDims[2]*(2*numPillars + 1) + 1

    textMap = levelMap(minX, minY, minZ, maxX, maxY, maxZ) #TODO, import this
    return

    for i in range(len(tps)):
        for j in range(len(tps[0])):
            for k in range(len(tps[0][0])):
                tp = tps[i][j][k]
                agent_host.sendCommand("tp {} {} {}".format(tp[0], tp[1], tp[2]))
                grid = waitForSensor(agent_host, tp)
                # sys.stdout.write(" {}\n".format(len(grid)))

def runSearch(agent_host, world_state):
    return

def main():
    #world recording parameters
    startPos = [252.5, 68.0, -214.5, 90.0] # x,y,z,yaw

    obsDims = [5, 1, 5]
    mapping = True
    numPillars = 1 #spaces observed = -O3--O2--O1--O2--O3-
    numPlatfms = 1

    # Loading world, initializing malmo
    agent_host, world_state, tps = initMalmo(mapping, startPos, obsDims, numPillars, numPlatfms)

    if(mapping):
        makeMap(agent_host, world_state, tps, startPos, obsDims, numPillars, numPlatfms)
    else:
        runSearch(agent_host, world_state)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
main()
