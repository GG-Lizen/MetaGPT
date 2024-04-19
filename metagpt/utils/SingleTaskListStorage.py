#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/11/22
@Author  : GG-Lizen
@File    : SingleTaskListStorage.py
@Desc:     supporting M&BA single instance tasks storage .
"""
from collections import deque
from typing import Dict, List
import unittest
# Task storage supporting only a single instance 
class SingleTaskListStorage:
    def __init__(self):
        self.tasks = deque([])
        self.task_id_counter = 0

    def append(self, task: Dict):
        self.tasks.append(task)

    def replace(self, tasks: List[Dict]):
        self.tasks = deque(tasks)

    def popleft(self):
        return self.tasks.popleft()
    def get_left(self):
        return self.tasks[0]
    def is_empty(self):
        return False if self.tasks else True

    def next_task_id(self):
        self.task_id_counter += 1
        return self.task_id_counter

    def get_task_list(self):
        return [t["task_name"] for t in self.tasks]
    
class TestSingleTaskListStorage(unittest.TestCase):
    def setUp(self):
        # 在每个测试方法执行前初始化测试数据
        self.storage = SingleTaskListStorage()

    def test_append(self):
        # 测试 append 方法是否能正确添加任务到列表中
        task = {"task_name": "Task 1", "task_description": "Description 1"}
        self.storage.append(task)

        self.assertEqual(len(self.storage.tasks), 1)
        self.assertEqual(self.storage.tasks[0], task)

    def test_replace(self):
        # 测试 replace 方法是否能正确替换任务列表
        tasks = [
            {"task_name": "Task A", "task_description": "Description A"},
            {"task_name": "Task B", "task_description": "Description B"}
        ]
        self.storage.replace(tasks)

        self.assertEqual(len(self.storage.tasks), 2)
        self.assertEqual(list(self.storage.tasks), tasks)

    def test_popleft(self):
        # 测试 popleft 方法是否能正确移除最左侧的任务
        tasks = [
            {"task_name": "Task X", "task_description": "Description X"},
            {"task_name": "Task Y", "task_description": "Description Y"}
        ]
        self.storage.replace(tasks)

        popped_task = self.storage.popleft()
        self.assertEqual(popped_task, tasks[0])
        self.assertEqual(len(self.storage.tasks), 1)

    def test_get_left(self):
        # 测试 get_left 方法是否能正确返回最左侧的任务
        tasks = [
            {"task_name": "Task X", "task_description": "Description X"},
            {"task_name": "Task Y", "task_description": "Description Y"}
        ]
        self.storage.replace(tasks)

        left_task = self.storage.get_left()
        self.assertEqual(left_task, tasks[0])

    def test_is_empty(self):
        # 测试 is_empty 方法是否能正确判断任务列表是否为空
        self.assertTrue(self.storage.is_empty())

        tasks = [{"task_name": "Task 1"}]
        self.storage.replace(tasks)

        self.assertFalse(self.storage.is_empty())

    def test_next_task_id(self):
        # 测试 next_task_id 方法是否能正确生成递增的任务 ID
        self.assertEqual(self.storage.next_task_id(), 1)
        self.assertEqual(self.storage.next_task_id(), 2)
        self.assertEqual(self.storage.next_task_id(), 3)

    def test_get_task_list(self):
        # 测试 get_task_list 方法是否能正确返回任务名称列表
        tasks = [
            {"task_name": "Task X", "task_description": "Description X"},
            {"task_name": "Task Y", "task_description": "Description Y"}
        ]
        self.storage.replace(tasks)

        task_names = self.storage.get_task_list()
        expected_names = ["Task X", "Task Y"]
        self.assertEqual(task_names, expected_names)

# if __name__ == '__main__':
#     unittest.main()

