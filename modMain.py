# -*- coding:utf-8 -*-

from mod.common.mod import Mod
import mod.client.extraClientApi as ClientApi
import mod.server.extraServerApi as serverApi


@Mod.Binding(name="MonsterPlant", version="Rev 21.1.1640")
# Release version
# Rev 21.1.1640
# Author:BiDuang(me@biduang.cn|github.com/biduang)
class MonsterPlant(object):

    def __init__(self):
        print("[MonsterPlant_Initialization] Plugin initializing ")

    @Mod.InitServer()
    def initMod(self):
        serverApi.RegisterSystem(
            "MonsterPlant", "MonsterPlantServer",
            "monsterPlantScripts.monsterPlantServer.MonsterPlantServer")

    @Mod.InitClient()
    def init(self):
        ClientApi.RegisterSystem(
            "MonsterPlant", "MonsterPlantClient",
            "monsterPlantScripts.monsterPlantClient.MonsterPlantClient")
