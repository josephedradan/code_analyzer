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

        self.list_str: List[str] = []

        self.dict_k_variable_value: dict = {}

    def get_list_str(self) -> List[str]:
        return self.list_str

    def get_dict_k_variable_value(self) -> dict:
        return self.dict_k_variable_value

    def add(self, object_: Any):

        if isinstance(object_, ContainerComment):
            self.list_str.extend(object_.list_str)
            self.dict_k_variable_value.update(object_.dict_k_variable_value)

        elif isinstance(object_, dict):
            self.dict_k_variable_value.update(object_)

        elif isinstance(object_, str):
            self.list_str.append(object_)

        elif isinstance(object_, Iterable):
            self.list_str.extend(object_)

        else:
            self.list_str.append(object_)

    def add_by_exhausting(self, object_: List):

        while object_:
            item = object_.pop()
            self.add(item)

    def __str__(self):

        list_items = []

        if self.list_str:
            list_items.append(str(self.list_str))
        if self.dict_k_variable_value:
            list_items.append(str(self.dict_k_variable_value))

        return ", ".join(list_items)

    def __len__(self):
        return len(self.__str__())
