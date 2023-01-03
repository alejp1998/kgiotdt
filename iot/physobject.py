#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Alejandro Jarabo
# Created Date: 2022-09-19
# Contact : ale.jarabo.penas@ericsson.com
# version ='1.0'
# ---------------------------------------------------------------------------
""" Physical Object
This module is responsible for emulating the behavior of the IoT devices platform. 
To do this, it creates several instances of each device corresponding to each of the 
initially described tasks in the plant. These tasks are divided into the production 
and safety/environmental departments.

The data generated by each device is personalized based on the tasks they belong to 
using data generation parameters. This way, devices performing similar tasks are given 
the same data generation parameters, so that their behavior is somewhat similar.

Additionally, ground truth classes are instantiated, which simulate variables such as 
temperature and pressure in different spaces, such as indoors and outdoors. If two temperature 
sensors are placed indoors, for example, they will be linked to the same ground truth instance 
and the data they generate will be somewhat similar (with some random noise).

Finally, some cases of interest are simulated, such as the replacement of a device with a new one 
belonging to a slightly different class, and the installation of a complementary device to speed up a task. 
These cases have been designed to test the correct implementation of the Knowledge Graph Agent's functionalities.
"""
# ---------------------------------------------------------------------------
# Imports
from iotdevices import *
# ---------------------------------------------------------------------------

# PARAMETERS FOR DATA GENERATION DEPENDING ON TASK
# PRODUCTION LINE - Tasks
prod_underpan_params = {
    'pickup': (1,2.0,40,3*np.pi/2), #(offset,amplitude,period,phase_shift)
    'piece_det': (2,1.5,40,0) #(offset,amplitude,period,phase_shift)
}
prod_body_params = { 
    'pickup': (0,1.0,20,0), #(offset,amplitude,period,phase_shift)
    'drilling': (0,2.0,20,np.pi/2), #(offset,amplitude,period,phase_shift)
    'clamping': (0,3.0,20,np.pi), #(offset,amplitude,period,phase_shift)
    'piece_det' : (2,1.5,40,0), #(offset,amplitude,period,phase_shift)
    'pose_det': (1,0.5,20,np.pi) #(offset,amplitude,period,phase_shift)
}
prod_window_params = {
    'pickup': (1,0.5,60,np.pi/2), #(offset,amplitude,period,phase_shift)
    'milling': (0,0.5,70,0), #(offset,amplitude,period,phase_shift)
    'pose_det': (1,0.5,50,np.pi) #(offset,amplitude,period,phase_shift)
}
prod_completion_params = {
    'pickup': (-1,1.5,30,np.pi/2), #(offset,amplitude,period,phase_shift)
    'pose_det': (0,3,50,3*np.pi/2) #(offset,amplitude,period,phase_shift)
}

# PRODUCTION LINE - Conveyor Belts
prod_convbelt_1 = {'conv_belt': (1,0.1)} #(mean, standard deviation)
prod_convbelt_2 = {'conv_belt': (2,0.1)} #(mean, standard deviation)
prod_convbelt_3 = {'conv_belt': (3,0.1)} #(mean, standard deviation)
prod_convbelt_4 = {'conv_belt': (4,0.1)} #(mean, standard deviation)
prod_convbelt_5 = {'conv_belt': (5,0.1)} #(mean, standard deviation)

# SAFETY / ENVIRONMENTAL - Ambient Variables
safetyenv_indoor_vars = { #(mean, standard deviation)
    'temperature': (20,0.1),
    'humidity': (25,0.1),
    'pressure': (1.013,0.3),
    'pm1': (1,0.5),
    'pm25': (9,0.5),
    'pm10': (18,0.5),
}
safetyenv_outdoor_vars = { #(mean, standard deviation)
    'temperature': (10,0.1),
    'humidity': (50,0.1),
    'pressure': (1.013,0.1),
    'pm1': (1.25,0.5),
    'pm25': (10,0.5),
    'pm10': (20,0.5),
    'rain_cumdepth': (10,1),
    'wind_speed': (6,1),
    'wind_direction': (180,5)
}

######################
######## MAIN ########
######################
def main() :
    # DEMO - Reduced number of devices
    # SAFETY / ENVIRONMENTAL - INITIAL DEVICES
    # Ambient variables time series
    safetyenv_indoors = GroundTruth(safetyenv_indoor_vars)
    safetyenv_outdoors = GroundTruth(safetyenv_outdoor_vars)
    safetyenv_indoors.start()
    safetyenv_outdoors.start()

    # Indoors Monitoring
    indoors_airquality = AirQuality(safetyenv_indoors,devuuid="indoors_airquality",print_logs=True)
    indoors_airquality.start()
    NoiseSensor(devuuid="7fc17e8f-1e1c-43f8-a2d1-9ff4bcfbf9ff").start()
    SmokeSensor(devuuid="5a84f26b-bf77-42d3-ab8a-83a214112844").start()
    SeismicSensor(devuuid="4f1f6ac2-f565-42af-a186-db17f7ed94c2").start()

    # Outdoors Monitoring
    AirQuality(safetyenv_outdoors,devuuid="outdoors_airquality").start()
    RainSensor(safetyenv_outdoors,devuuid="70a15d0b-f6d3-4833-b929-74abdff69fa5").start()
    WindSensor(safetyenv_outdoors,devuuid="f41db548-3a85-491e-ada6-bab5c106ced6").start()

    # CASE 1: Known device disappears and new, similar device appears
    # If a known device disappears and a new one with similar characteristics appears, 
    # this could justify replacing the old device with the new one. 
    # Similar characteristics refer to a few modifications in the device's modules or attributes, 
    # and the data it reports having a similar behavior. 
    # In this case, the similarity between the two devices should be quite high.

    time.sleep(90) # after 30 secs old device disappears and new one appears
    indoors_airquality.active = False # stop indoors air quality
    time.sleep(10)
    indoors_airqualitysimp = AirQualitySimplified(safetyenv_indoors,devuuid='indoors_airqualitysimp',print_logs=True)
    indoors_airqualitysimp.start() # start simplified indoors air quality

    '''
    # PRODUCTION LINE - INITIAL DEVICES
    # Initialization Task
    TagScanner(devuuid="8a40d136-8401-41bd-9845-7dc8f28ea582").start()
    ProductionControl(devuuid="3d193d4c-ba9c-453e-b98b-cec9546b9182").start()

    # Underpan Configuration Task
    PickUpRobot(prod_underpan_params,devuuid="5f3333b9-8292-4371-b5c5-c1ec21d0b652").start()
    PieceDetector(prod_underpan_params,devuuid="45d289e7-4da6-4c10-aa6e-2c1d48b223e2").start()

    # Body Configuration Task
    bodyconfig_pickuprob = PickUpRobot(prod_body_params,devuuid="bodyconfig_pickuprob")
    bodyconfig_pickuprob.start()
    ClampingRobot(prod_body_params,devuuid="5ee2149f-ef6e-402b-937e-8e04a2133cdd").start()
    DrillingRobot(prod_body_params,devuuid="98247600-c4fe-4728-bda6-ed8fadf81af2").start()
    PieceDetector(prod_body_params,devuuid="d7295016-4a54-4c98-a4c1-4f0c7f7614b5").start()
    PoseDetector(prod_body_params,devuuid="2c91bd9d-bdfc-4a6b-b465-575f43897d59").start()

    # Vehicle Scanning
    ConfigurationScanner(devuuid="0d451573-243e-423b-bfab-0f3117f88bd0").start()
    FaultNotifier(devuuid="f1b43cb8-127a-43b5-905d-9f145171079es").start()

    # Window Milling
    PickUpRobot(prod_window_params,devuuid="windowmilling_pickuprob").start()
    MillingRobot(prod_window_params,devuuid="5ce94c31-3004-431e-97b3-c8f779fb180d").start()
    PoseDetector(prod_window_params,devuuid="1df9566a-2f06-48f0-975f-28058c6784c0").start()

    # Quality Check
    QualityScanner(devuuid="fd9ccbb2-be41-4507-85ac-a431fe886541").start()
    FaultNotifier(devuuid="5bb02f4b-0dfe-45d4-8a87-e902e6ea0bf6").start()

    # Artificial Repair
    RepairControl(devuuid="4525aa12-06fb-484f-be38-58afb33e1558").start()

    # Product Completion
    PickUpRobot(prod_completion_params,devuuid="ae5e4ad3-bd59-4dc8-b242-e72747d187d4").start()
    PoseDetector(prod_completion_params,devuuid="f2d73019-1e87-48a7-b93c-af0a4fc17994").start()

    # Tasks Connectors
    ConveyorBelt(prod_convbelt_1,devuuid="fbeaa5f3-e532-4e02-8429-c77301f46470").start()
    ConveyorBelt(prod_convbelt_2,devuuid="f169a965-bb15-4db3-97cd-49b5b641a9fe").start()
    ConveyorBelt(prod_convbelt_3,devuuid="3140ce5c-0d08-4aff-9bb4-14a9e6a33d12").start()
    ConveyorBelt(prod_convbelt_4,devuuid="a6f65d7a-019a-4723-9b81-fb4a163fa23a").start()
    ConveyorBelt(prod_convbelt_5,devuuid="f342e60b-6a54-4f20-8874-89a550ebc75c").start()
    
    # SAFETY / ENVIRONMENTAL - INITIAL DEVICES
    # Ambient variables time series
    safetyenv_indoors = GroundTruth(safetyenv_indoor_vars)
    safetyenv_outdoors = GroundTruth(safetyenv_outdoor_vars)
    safetyenv_indoors.start()
    safetyenv_outdoors.start()

    # Indoors Monitoring
    indoors_airquality = AirQuality(safetyenv_indoors,devuuid="indoors_airquality",print_logs=True)
    indoors_airquality.start()
    NoiseSensor(devuuid="7fc17e8f-1e1c-43f8-a2d1-9ff4bcfbf9ff").start()
    SmokeSensor(devuuid="5a84f26b-bf77-42d3-ab8a-83a214112844").start()
    SeismicSensor(devuuid="4f1f6ac2-f565-42af-a186-db17f7ed94c2").start()

    # Outdoors Monitorization
    AirQuality(safetyenv_outdoors,devuuid="outdoors_airquality").start()
    RainSensor(safetyenv_outdoors,devuuid="70a15d0b-f6d3-4833-b929-74abdff69fa5").start()
    WindSensor(safetyenv_outdoors,devuuid="f41db548-3a85-491e-ada6-bab5c106ced6").start()

    # Safety Alarms
    IndoorsAlarm(devuuid="4d36d0c4-891f-44ec-afe1-278258058944").start()
    OutdoorsAlarm(devuuid="b60108c2-46a3-4b67-9b8d-38586cb3039d").start()

    # TEST CASES

    # CASE 1: New, slightly different class device replaces inactive device.

    # Similar characteristics implies that it will have a few modifications in its modules/attribs
    # and the data it reports will have a somehow similar behavior.

    # In this case similarity should be quite high, which could justify applying a simple
    # replacement of the old device by the new device.

    time.sleep(15) # after 2 mins old device disappears and new one appears
    indoors_airquality.active = False # stop indoors air quality
    time.sleep(15)
    indoors_airqualitymod = AirQualitySimplified(safetyenv_indoors,devuuid='indoors_airqualitysimp',print_logs=True)
    indoors_airqualitymod.start() # start modified indoors air quality

    # CASE 2: Complementary device appears in a task.
    # In this case, a complementary device appears in a task. 
    # This device has a new or existing class that has been added to an existing task 
    # and shows a high similarity to a set of devices already present in that task. 
    # The device's description and attributes time series should allow us to determine that it belongs in the task. 
    # As a result, the device can be integrated into the task in the knowledge graph. 
    # An example of this scenario is the addition of a robotic arm to speed up a task, 
    # where the new robotic arm shows similar behavior to the one it is complementing.

    time.sleep(30) # after 30 seconds a complementary pickup robot is added to bodyconf task
    bodyconfig_pickuprob2 = PickUpRobot(prod_body_params,devuuid='bodyconfig_pickuprob2',print_logs=False)
    bodyconfig_pickuprob2.start()

    # CASE 3: Completely unknown device appears.
    # In this case, a completely unknown device appears. 
    # This device has a new name and SDF definition, so the knowledge graph agent 
    # must decide where it belongs in the graph's structure. 
    # This may involve modifying the schema and data as necessary. 
    # This is a more complex problem because there may not be any other devices in the structure 
    # that measure similar data or fulfill a similar function. 
    # To determine where the new device belongs, we can search for the most similar existing devices 
    # based on a given feature space. Once we find the most similar devices, we can query their neighborhoods 
    # and analyze them to determine how the new device should be included in the graph. 
    # This only addresses the problem of determining which task the new device belongs to, 
    # but it may not be able to create a new task or higher ontological entity to include the device if it does not fit anywhere. 
    # To do this, it may be necessary to include more information in the device's description, such as which devices it interacts with. 
    # One option could be to check which devices are subscribed to other devices' topics to create more complex relations.
    '''
    

if __name__ == "__main__":
    main()