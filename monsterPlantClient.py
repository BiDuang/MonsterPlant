# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi

class MonsterPlantClient(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(MonsterPlantClient, self).__init__(namespace, name)