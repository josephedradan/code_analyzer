"""
Created by Joseph Edradan
Github: https://github.com/josephedradan

Date created: 12/1/2022

Purpose:

Details:

Description:

Notes:

IMPORTANT NOTES:

Explanation:

Tags:

Reference:

"""
from typing import Any, Iterable, List


class ContainerComment:

    def __init__(self):

        self.list_any: List[Any] = []

        self.dict_k_variable_value: dict = {}

    def get_list_any(self) -> List[str]:
        return self.list_any

    def get_dict_k_variable_value(self) -> dict:
        return self.dict_k_variable_value

    def add(self, object_: Any):

        if isinstance(object_, ContainerComment):
            self.list_any.extend(object_.list_any)
            self.dict_k_variable_value.update(object_.dict_k_variable_value)

        elif isinstance(object_, dict):
            self.dict_k_variable_value.update(object_)

        elif isinstance(object_, str):
            self.list_any.append(object_)

        elif isinstance(object_, Iterable):
            self.list_any.extend(object_)

        else:
            self.list_any.append(object_)

    def add_by_exhausting(self, object_: List):

        while object_:
            item = object_.pop()
            self.add(item)

    def __str__(self) -> str:

        list_items: List[str] = []

        for item in self.list_any:

            if isinstance(item, str):
                list_items.append("'{}'".format(item))
            else:
                list_items.append(str(item))

        for k, v in self.dict_k_variable_value.items():

            if isinstance(v, str):
                list_items.append("'{}': '{}'".format(k, v))
            else:
                list_items.append("'{}': {}".format(k, v))

        if list_items:
            return "({})".format(", ".join(list_items))

        return ""

    def __len__(self):
        return len(self.__str__())
