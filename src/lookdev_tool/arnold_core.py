import os
import json
import logging

from maya import cmds

from lookdev_tool import lookdev_core
from lookdev_tool import constants

ARNOLD_CORE_LOGGER = logging.getLogger(__name__)
ARNOLD_CORE_LOGGER.setLevel(10)


class GroundClass(object):
    def __init__(self, path1, path2, path3, colorCheckerPath):
        self.path1 = path1
        self.path2 = path2
        self.path3 = path3
        self.colorCheckerPath = colorCheckerPath

    def setGround(self, index):
        """
        Set ground and delete if one is already set
        :param index: Combo box current floor

        """
        ARNOLD_CORE_LOGGER.debug('self.path1: {}, self.path2: {}, self.path3: {}'.format(self.path1, self.path2, self.path3))

        # import ground 1
        if index == 0:
            if cmds.objExists('ground_1_arnold_ALL_Grp'):
                cmds.file(self.path1, removeReference=True)
            else:
                cmds.file(self.path1, reference=True)

                if cmds.objExists('ground_2_arnold_ALL_Grp'):
                    cmds.file(self.path2, removeReference=True)

                if cmds.objExists('ground_3_arnold_ALL_Grp'):
                    cmds.file(self.path3, removeReference=True)

        # import ground 2
        if index == 1:
            if cmds.objExists('ground_2_arnold_ALL_Grp'):
                cmds.file(self.path2, removeReference=True)
            else:
                cmds.file(self.path2, reference=True)

                if cmds.objExists('ground_1_arnold_ALL_Grp'):
                    cmds.file(self.path1, removeReference=True)

                if cmds.objExists('ground_3_arnold_ALL_Grp'):
                    cmds.file(self.path3, removeReference=True)

        # import ground 3
        if index == 2:
            if cmds.objExists('ground_3_arnold_ALL_Grp'):
                cmds.file(self.path3, removeReference=True)
            else:
                cmds.file(self.path3, reference=True)

                if cmds.objExists('ground_1_arnold_ALL_Grp'):
                    cmds.file(self.path1, removeReference=True)

                if cmds.objExists('ground_2_arnold_ALL_Grp'):
                    cmds.file(self.path2, removeReference=True)

        cmds.select(clear=True)


class LightDome(object):

    LIGHT_DOME_NAME = 'lightDome'

    def setLightDome(self, hdriName):
        """
        Set light dome and delete it if one is already set
        :param hdriName: HDRI's name from QlineEdit
        """
        if not cmds.objExists(self.LIGHT_DOME_NAME):
            lightDome = cmds.createNode('aiSkyDomeLight', name='lightDome', skipSelect=True)
            # rename lightDome transform node
            lightDomeT = cmds.listRelatives(self.LIGHT_DOME_NAME, parent=True)[0]
            self.lightDomeTransform = cmds.rename(lightDomeT, 'lightDomeTransfom')

            lightDomeFile = lookdev_core.createFileText('dome1')
            cmds.setAttr('{}.{}'.format(lightDomeFile, 'fileTextureName'), '{}.exr'.format(os.path.join(constants.LIGHT_DOME_PATH, hdriName)), type='string')
            cmds.connectAttr('{}.{}'.format(lightDomeFile, 'outColor'), '{}.{}'.format(lightDome, 'color'))

            cmds.setAttr('{}.camera'.format(lightDome), 0)
            cmds.setAttr('{}.intensity'.format(lightDome), 1)
            cmds.setAttr('{}.exposure'.format(lightDome), 1)

        else:
            lightDelOne = cmds.listConnections(self.LIGHT_DOME_NAME, source=True)
            lightDelTwo = cmds.listConnections(lightDelOne[-1], source=True)

            cmds.delete(lightDelTwo[1:])
            cmds.delete(lightDelOne[-1])

    @staticmethod
    def changeDome1Intens(value):
        """
        Changes lightDom intensity
        """
        if cmds.objExists('lightDome'):
            cmds.setAttr('lightDome.intensity', value)

    def rotateDome(self, value):
        """
        Changes lightDom rotation
        """
        if cmds.objExists('lightDome'):
            cmds.setAttr('{}.rotateY'.format(self.lightDomeTransform), value)


def createLight(name, intensity, translates, rotates):
    """
    Creates light function
    :return: None
    """
    # create key light and rename the transform
    light = cmds.createNode('aiAreaLight', name=name, skipSelect=True)

    lightTransform = cmds.rename(cmds.listRelatives(light, parent=True), name+'Transform')

    # set light scale and intensity
    cmds.setAttr('{}.{}'.format(lightTransform, 'scaleX'), 14)
    cmds.setAttr('{}.{}'.format(lightTransform, 'scaleY'), 10)

    cmds.setAttr('{}.{}'.format(light, 'intensity'), intensity)

    # place the light in front of the asset
    cmds.xform(lightTransform, translation=translates, rotation=rotates)

    # add ramp to the light
    rampText = cmds.createNode('place2dTexture', name='keyLightText', skipSelect=True)
    rampKeyL = cmds.createNode('ramp', name='keyLightRamp', skipSelect=True)

    cmds.connectAttr('{}.{}'.format(rampText, 'outUV'), '{}.uv'.format(rampKeyL))
    cmds.connectAttr('{}.{}'.format(rampText, 'outUvFilterSize'), '{}.uvFilterSize'.format(rampKeyL))
    cmds.connectAttr('{}.{}'.format(rampKeyL, 'outColor'), '{}.color'.format(light))

    # set the ramp
    cmds.setAttr('{}.{}'.format(rampKeyL, 'colorEntryList[0].color'),  1, 1, 1, type='double3')
    cmds.setAttr('{}.{}'.format(rampKeyL, 'colorEntryList[1].color'), 0, 0, 0, type='double3')
    cmds.setAttr('{}.{}'.format(rampKeyL, 'colorEntryList[1].position'), 1)
    cmds.setAttr('{}.{}'.format(rampKeyL, 'type'), 4)
    cmds.setAttr('{}.{}'.format(rampKeyL, 'interpolation'), 3)


def setThreePointsLights():
    """
    Set Three points light in scene and delete them is they are already in scene
    """
    if cmds.objExists('fillLightTransform') and cmds.objExists('keyLightTransform') and cmds.objExists('backLightTransform'):
        cmds.delete('Lights_Grp')

    else:
        createLight('fillLight', 10, (-27.622, 13.845, 39.553), (-9.131, -33.499, 0))
        createLight('keyLight', 40, (42.354, 14.693, 24.781), (-11.178, 58.981, 0))
        createLight('backLight', 10, (17.813, 11.919, -29.204), (-10.897, -213.093, 0))

        # make lights invisible
        cmds.setAttr('{}.aiCamera'.format('fillLight'), 0)
        cmds.setAttr('{}.aiCamera'.format('keyLight'), 0)
        cmds.setAttr('{}.aiCamera'.format('backLight'), 0)

        cmds.setAttr('{}.intensity'.format('fillLight'), 1)
        cmds.setAttr('{}.intensity'.format('keyLight'), 1)
        cmds.setAttr('{}.intensity'.format('backLight'), 1)

        lightGroup = cmds.createNode('transform', name='Lights_Grp', skipSelect=True)

        cmds.parent('fillLightTransform', lightGroup)
        cmds.parent('keyLightTransform', lightGroup)
        cmds.parent('backLightTransform', lightGroup)

        cmds.select(clear=True)


def rotLights(rotation):
    """
    Set rotations on the light's offset group
    """
    if cmds.objExists('Lights_Grp'):
        cmds.setAttr('Lights_Grp.rotateY', rotation)


def changeLightIntensity(light, intensity):
    """
    Changes fill light intensity if it's in scene
    """
    if cmds.objExists('Lights_Grp'):
        cmds.setAttr('{}.exposure'.format(light), intensity)


def createCam(colorCheckerPath):
    """
    Create camera in scene
    :param colorCheckerPath: path of colorchecker to reference it
    """
    cmds.select(clear=True)

    if not cmds.objExists('Cam_Main_Grp'):
        cmds.createNode('camera', name='Main_Cam', skipSelect=True)
        cameraTransform = cmds.listRelatives('Main_Cam', parent=True)
        cameraOffset = cmds.createNode('transform', name='Camera_Offset', skipSelect=True)
        cmds.rename(cameraTransform, 'Main_Cam_Transform')

        # create color palette
        cmds.file(colorCheckerPath, reference=True)

        # group cam
        cmds.parent('ColorPalette_arnold_ALL_Grp', 'Main_Cam_Transform')
        cmds.parent('Main_Cam_Transform', cameraOffset)

        cmds.createNode('transform', name='Cam_Main_Grp', skipSelect=True)
        cmds.parent(cameraOffset, 'Cam_Main_Grp')

        # move cam
        cmds.xform('Main_Cam_Transform', translation=(0, 4.542, 13.729))

    else:
        cmds.file(colorCheckerPath, removeReference=True)
        cmds.delete('Cam_Main_Grp')

    cmds.select(clear=True)


def rotateCam(rotateValue):
    """
    Rotate cam's offset group
    :param: rotateValue: rotate value from rotateCam's Qline
    """
    if cmds.objExists('Cam_Main_Grp'):
        cmds.setAttr('{}.{}'.format('Cam_Main_Grp', 'rotateY'), rotateValue)


def disableLight(light, state):
    """
    Disable fill light if it's in scene
    :param: state(bool): light presence query
    light(str): light name
    """
    if state and cmds.objExists(light):
        cmds.connectAttr(
            '{}.instObjGroups[0]'.format(light), 'defaultLightSet.dagSetMembers', nextAvailable=True
        )

    if not state and cmds.objExists(light):
        cmds.disconnectAttr('{}.instObjGroups[0]'.format(light), 'defaultLightSet.dagSetMembers', nextAvailable=True)


def storePrefs():
    """Creates a json and write coordinates to replace the lights"""
    # create dict from lights position, values, intensity and scale

    if not cmds.objExists('fillLightTransform'):
        raise RuntimeError('No lights in scene')

    for index, light in enumerate(['fillLightTransform', 'keyLightTransform', 'backLightTransform']):
        constants.ARNOLD_LIGHT_VALUES[index].get(light, {})['{}Coords'.format(light)] = cmds.xform(light, query=True, matrix=True)
        constants.ARNOLD_LIGHT_VALUES[index].get(light, {})['{}scaleX'.format(light)] = cmds.getAttr('{}.scaleX'.format(light))
        constants.ARNOLD_LIGHT_VALUES[index].get(light, {})['{}scaleY'.format(light)] = cmds.getAttr('{}.scaleY'.format(light))
        constants.ARNOLD_LIGHT_VALUES[index].get(light, {})['{}exposure'.format(light)] = cmds.getAttr('{}.exposure'.format(light))

    with open(constants.ARNOLD_PREFERENCE_PATH, 'w') as wFile:
        wFile.write(json.dumps(constants.ARNOLD_LIGHT_VALUES, indent=4))

        # Write prefs in Maya
        cmds.optionVar(stringValue=('lookdev_arnold_settings', json.dumps(constants.ARNOLD_LIGHT_VALUES, indent=4)))


def clearScene(colorCheckerPath, ground1Path, ground2Path, ground3Path):
    """
    Clear all tool's nodes in scene
    :param colorCheckerPath: colorChecker's path
    :param ground1Path: ground1's path
    :param ground2Path: ground2's path
    :param ground3Path: ground3's path
    """
    # cam
    if cmds.objExists('Cam_Main_Grp'):
        cmds.file(colorCheckerPath, removeReference=True)
        cmds.delete('Cam_Main_Grp')

    # ground
    if cmds.objExists('ground_1_arnold_ALL_Grp'):
        cmds.file(ground1Path, removeReference=True)

    if cmds.objExists('ground_2_arnold_ALL_Grp'):
        cmds.file(ground2Path, removeReference=True)

    if cmds.objExists('ground_3_arnold_ALL_Grp'):
        cmds.file(ground3Path, removeReference=True)

    # lights
    if cmds.objExists('Lights_Grp'):
        cmds.delete('Lights_Grp')

    # lightDome
    if cmds.objExists('lightDomeTransfom'):
        # del connected nodes
        lightDelOne = cmds.listConnections('lightDome', source=True)
        print(lightDelOne)
        lightDelTwo = cmds.listConnections(lightDelOne[0], source=True)
        print(lightDelTwo)

        cmds.delete(lightDelTwo[-1])
        cmds.delete(lightDelOne[0])


def importPrefs():
    """
    Read .json to set position, rotation, scale and intensity to three points light
    """
    arnoldMayaSettings = cmds.optionVar(query='lookdev_arnold_settings')
    arnoldSettings = json.loads(arnoldMayaSettings)

    if not arnoldSettings:
        cmds.error("Settings not found")
        return
    print(arnoldSettings)

    # set the position, scale and intensity
    for index, light in enumerate(['fillLightTransform', 'keyLightTransform', 'backLightTransform']):
        cmds.xform(light, matrix=(arnoldSettings[index].get(light, {}).get('{}Coords'.format(light))))
        cmds.setAttr('{}.scaleX'.format(light), (arnoldSettings[index].get(light, {}).get('{}scaleX'.format(light))))
        cmds.setAttr('{}.scaleY'.format(light), (arnoldSettings[index].get(light, {}).get('{}scaleY'.format(light))))
        cmds.setAttr('{}.exposure'.format(light), (arnoldSettings[index].get(light, {}).get('{}exposure'.format(light))))
