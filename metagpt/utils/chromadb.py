#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/11/22
@Author  : GG-Lizen
@File    : chromadb.py
@Desc:     #TODO Implementation of the chromadb to save results.
"""
# only implement no  db  version
from typing import Dict, List
class Context:
    def __init__(self):
        self.resultsStorage = {}  # 存储结果的字典
        self.resultsOrder = []  # 存储结果顺序的列表

    def add(self, task: Dict, result: str, result_id: str):
        self.resultsStorage[result_id] = {
            "documents": result,
            "metadatas": {"task": task["task_name"], "result": result}
        }
        self.resultsOrder.append(result_id)

    def results2String(self, results: List[Dict]) -> str:
        # 初始化一个空字符串，用于存储转换后的结果
        resultsString = ""
        
        # 遍历数组中的元素
        for i, item in enumerate(results, start=1):
            # 构建每个元素对应的序号和内容，并添加到结果字符串中
            task_name = item["task"]
            result_value = item["result"]
            resultsString += f"任务：{task_name}，执行结果：{result_value}\n"
            
        
        # 返回最终的结果字符串
        return resultsString

    def getTopNResults(self, top_results_num: int) -> str:
        topNIds = self.resultsOrder[-top_results_num:]  # 获取最近添加的 top_results_num 个结果的 result_id
        results = []
        for result_id in topNIds:
            if result_id in self.resultsStorage:
                results.append(self.resultsStorage[result_id]["metadatas"])
        
        # 调用 results2String 方法将结果列表转换为字符串
        return self.results2String(results)
def testContextAgent():
    ContextAgent = Context()
# 添加一些任务结果
    ContextAgent.add({"task_name": "Task A"}, "Result A", "id1")
    ContextAgent.add({"task_name": "Task B"}, "Result B", "id2")
    ContextAgent.add({"task_name": "Task C"}, "Result C", "id3")

# 获取最近的两个结果
    recent_results = ContextAgent.getTopNResults(2)
   

# if __name__ == "__main__":
#     testContextAgent()