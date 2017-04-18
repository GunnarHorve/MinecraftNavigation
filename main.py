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

def initMalmo(mapping, startPos, obsDims, numPillars, numPlatforms):
    # load the world
    missionXML = getMissionXML(mapping, startPos, obsDims)
    my_mission = MalmoPython.MissionSpec(missionXML, True)

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

    return (agent_host, world_state)

################## Boilerplate code above this point ##########################

def main():
    #world recording parameters
    startPos = [252.5, 68.0, -214.5, 90.0] # x,y,z,yaw
    obsDims = [5, 1, 5]
    mapping = True
    numPillars = 2 #spaces observed = -O3--O2--O1--O2--O3-
    numPlatforms = 3

    # Loading world, initializing malmo
    agent_host, world_state = initMalmo(mapping, startPos, obsDims, numPillars, numPlatforms)

    # Loop until mission ends:
    while world_state.is_mission_running:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        agent_host.sendCommand("tp 100 100 100")

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
main()

    # for error in world_state.errors:
    #     print "Error:",error.text
    # if world_state.number_of_observations_since_last_state > 0:
    #     msg = world_state.observations[-1].text
    #     observations = json.loads(msg)
    #     grid = observations.get(u'sliceObserver', 0)
    #     print len(grid)
    #     break
