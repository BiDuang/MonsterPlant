# -*- coding: utf-8 -*-
# Author: BiDuang

import mod.server.extraServerApi as serverApi
import monsterPlantScripts.data.plantData as plantData
import monsterPlantScripts.data.seedData as seedData
import monsterPlantScripts.data.mobData as mobData
import random
import json

minecraftEnum = serverApi.GetMinecraftEnum()


class MonsterPlantServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(MonsterPlantServer, self).__init__(namespace, name)
        self.playerId = None
        self.ListenEvent()
        self.Init()

    def ListenEvent(self):
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(),
                            "BlockNeighborChangedServerEvent", self,
                            self.OnBlockNeighborChangedServerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(),
                            "ServerItemUseOnEvent", self,
                            self.OnServerItemUseOnEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(),
                            "DestroyBlockEvent", self,
                            self.OnDestroyBlockEvent
                            )
        self.ListenForEvent(serverApi.GetEngineNamespace(),
                            serverApi.GetEngineSystemName(),
                            "MobDieEvent", self,
                            self.OnMobDieEvent
                            )
        print("[MonsterPlant_Initialization] Start listening ")
    # 侦听事件

    def Init(self):
        print("[MonsterPlant_Initialization] Initialized! ")

    def OnBlockNeighborChangedServerEvent(self, args):
        levelId = serverApi.GetLevelId()
        comp = self.CreateComponent(
            self.playerId, "Minecraft", "blockInfo")
        pos = (args['posX'], args['posY'], args['posZ'])
        cropinfo = comp.GetBlockNew(pos)
        dati = ""
        mpd = {}
        for i in plantData.plantList:
            for j in range(3):
                if cropinfo["name"] == plantData.plantList[i][j]:
                    dati = i
                    datj = j
                    mpd = {
                        'itemName': seedData.seedList[dati],
                        'count': 1,
                        'auxValue': 0
                    }
        neighPos = (args['neighborPosX'],
                    args['neighborPosY'], args['neighborPosZ'])
        if (self.IsBelow(pos, neighPos)):
            blockDict = comp.GetBlockNew(neighPos)
            if blockDict["name"] != "minecraft:soul_sand":
                blockDict = {
                    'name': 'minecraft:air',
                    'aux': 0
                }
                comp.SetBlockNew(pos, blockDict)
                comp = self.CreateComponent(
                    self.playerId, "Minecraft", "blockInfo")
                sP = (args['posX'], args['posY'], args['posZ'])
                comp = serverApi.CreateComponent(levelId, 'Minecraft', 'item')
                print("[MonsterPlant_Notice] Event: Neighbor Block Changed | Info ",
                      seedData.seedList[dati])
                comp.SpawnItemToLevel(mpd, 0, sP)
        # 当检测到底部方块变化时，掉落种子

    def OnServerItemUseOnEvent(self, args):
        playerID = args["entityId"]

        dati = ""
        datj = 0
        datin = ""
        stat = False
        for i in seedData.seedList:
            if args["itemName"] == seedData.seedList[i]:
                dati = i
                datin = args["itemName"]
                stat = True
        # 遍历在monsterplant中的seedList获取使用的item

        comp = self.CreateComponent(
            self.playerId, "Minecraft", "blockInfo")

        belowPos = (args["x"], args["y"], args["z"])
        plt = comp.GetBlockNew(belowPos)
        if plt["name"] == "minecraft:soul_sand" and stat:
            plt = {
                'name': plantData.plantList[dati][0],
                'aux': 0
            }
            # 检测为灵魂沙方块才允许种植成功
            print("[Notice] Event: Crop Planted | Info ", dati, belowPos)
            comp.SetBlockNew((args["x"], args["y"] + 1, args["z"]), plt)
            itemComp = self.CreateComponent(playerID, "Minecraft", "item")
            item = itemComp.GetPlayerItem(
                minecraftEnum.ItemPosType.CARRIED, 0)
            print("[MonsterPlant_Notice] Event: Seed Reduced | Info ",
                  item['itemName'], item['count']-1)
            item["count"] -= 1
            itemComp.SpawnItemToPlayerCarried(item, playerID)
            # 种植后减少种子item数量

        if args["itemName"] == "minecraft:dye":
            comp = self.CreateComponent(
                self.playerId, "Minecraft", "blockInfo")
            usePos = (args["x"], args["y"], args["z"])
            bif = comp.GetBlockNew(usePos)

            stat = False
            dati = ""
            datj = 0
            for i in plantData.plantList:
                for j in range(3):
                    if bif["name"] == plantData.plantList[i][j]:
                        stat = True
                        dati = i
                        datj = j
                        datin = plantData.plantList[i]

            if stat and datj != 3:
                # 骨粉催熟作物检测
                bif = {
                    'name': datin[datj+1],
                    'aux': 0
                }
                print("[MonsterPlant_Notice] Event: Dye Used | Info ", bif, usePos)
                comp.SetBlockNew(usePos, bif)
                itemComp = self.CreateComponent(playerID, "Minecraft", "item")
                item = itemComp.GetPlayerItem(
                    minecraftEnum.ItemPosType.CARRIED, 0)
                item["count"] -= 1
                itemComp.SpawnItemToPlayerCarried(item, playerID)
                # 使用骨粉后消耗骨粉item数量

    def OnDestroyBlockEvent(self, args):
        levelId = serverApi.GetLevelId()
        playerId = args["playerId"]

        dati = ""
        datj = 0
        mpd = {}
        for i in plantData.plantList:
            for j in range(4):
                if args["fullName"] == plantData.plantList[i][j]:
                    dati = i
                    datj = j
                    mpd = {
                        'itemName': seedData.seedList[dati],
                        'count': 1,
                        'auxValue': 0
                    }
        if datj == 3:
            comp = self.CreateComponent(
                self.playerId, "Minecraft", "blockInfo")
            bPos = (args["x"], args["y"], args["z"])
            comp = self.CreateComponent(playerId, "Minecraft", "rot")
            rot = comp.GetRot()
            num = random.randint(1, 5)
            print(
                "[MonsterPlant_Notice] Event: Mature Crop Collected | Info ", dati, num)
            for rd in range(num):
                self.CreateEngineEntityByTypeStr(
                    mobData.mobList[dati], bPos, rot)
                rand = random.randint(0, 2)
                bPos = (args["x"] + rd, args["y"], args["z"] + rand)
                # 成熟作物被收获后随机在一个2x2的方格内生成怪物
        elif datj != 0:
            comp = self.CreateComponent(
                self.playerId, "Minecraft", "blockInfo")
            sP = (args["x"], args["y"], args["z"])
            comp = serverApi.CreateComponent(levelId, 'Minecraft', 'item')
            print("[MonsterPlant_Notice] Event: Immature Crop Collected | Info ", dati)
            comp.SpawnItemToLevel(mpd, 0, sP)
            # 如果在成熟前被挖掘则掉落种子

    def IsBelow(self, pos, neighPos):
        return pos[0] == neighPos[0] and (pos[1]-1 == neighPos[1] and pos[2] == neighPos[2])

    def OnMobDieEvent(self, args):
        levelId = serverApi.GetLevelId()
        entityId = args["id"]
        comp = serverApi.GetEngineCompFactory().CreateEngineType(entityId)
        entityName = comp.GetEngineTypeStr()
        mpd = {}
        stat = False
        for i in mobData.mobList:
            if entityName == mobData.mobList[i]:
                mpd = {
                    'itemName': seedData.seedList[i],
                    'count': 1,
                    'auxValue': 0
                }
                ra = random.randint(0, 9)
                stat = True
        if stat:
            comp = serverApi.CreateComponent(entityId, "Minecraft", "pos")
            mbp = comp.GetPos()
            print("[MonsterPlant_Notice] Info: Rand value | ", ra)
            if ra > 6:
                comp = serverApi.CreateComponent(
                    levelId, 'Minecraft', 'item')
                comp.SpawnItemToLevel(mpd, 0, mbp)
                print("[MonsterPlant_Notice] Event: Seed Spawned | Info ",
                      entityName)
            # 50%几率杀死怪物掉落相应种子
