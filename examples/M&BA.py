"""
Filename: MetaGPT/examples/M&BA.py
Created Date: Wednesday, April 17th 2024, 10:40:39 am
Author: GG-Lizen
"""
import re
import fire
import time
import json
import unittest
from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team
from metagpt.utils.SingleTaskListStorage import SingleTaskListStorage
from metagpt.utils.chromadb import Context
from metagpt.utils.colorful import ColorPrinter

OBJECTIVE="发布一条受人欢迎的抖音视频"
INITIAL_TASK="选取热门话题"
#tasks storage
tasks_storage = SingleTaskListStorage()
#tasks excute result storage
ContextAgent = Context()
#Outputs text with the specified color to the command line
Colorful = ColorPrinter()
#start of the agent and connect prioritizationAgent and ExecutionAgent 
class Start(Action):
    name: str ="Start"
    async def run(self,task):


        if not tasks_storage.is_empty():
            
            # Print the task list
            task_list_log = Colorful.colorful( "\n*****任务清单*****\n",'purple')
            for t in tasks_storage.get_task_list():
                 task_list_log+=" • " + str(t)+"\n"
            logger.info(task_list_log)
            next_task_log=Colorful.colorful( "\n*****下一任务*****\n",'blue')+" • " +str(task["task_name"])
            logger.info(next_task_log)
              
            return tasks_storage.popleft()    
        else:
            logger.info(Colorful.colorful("\n***** 任务执行完成****\n",'green'))
class Connector(Role):
    name: str = "Kobe"
    profile: str = "EntryPoint"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([PrioritizationAgent,UserRequirement])
        self.set_actions([Start])

    
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")

        todo=self.rc.todo
        context = self.get_memories(k=1)  # use all memories as context
        context = json.loads(context[0].rag_key())
        # logger.info(f"Connector context :{context}")
        if context['new_tasks_list']:
            tasks_storage.replace(context['new_tasks_list'])
        task = await todo.run(task = tasks_storage.get_left())
        
        msg = Message(content=json.dumps(task),role = self.profile,cause_by=type(todo))
        return msg   

class ExecutionAgent(Action):
    PROMPT_TEMPLATE: str = """
    根据以下目标完成一项任务： {objective}.
    考虑到这些先前已完成的任务：
    {results}
    你当前的任务是：{task}
    只返回当前任务执行结果
    当前任务执行结果：
    """
    name: str = "ExecutionAgent"

    async def run(self, task):
        results = ContextAgent.getTopNResults(top_results_num=3)
        prompt = self.PROMPT_TEMPLATE.format(objective=OBJECTIVE,results=results,task=task["task_name"])
        logger.info(Colorful.colorful('\n***** 任务执行代理提示****\n','cyan')+f'{prompt}\n')
        logger.info(Colorful.colorful('\n***** LLM响应****\n','cyan'))
        rsp = await self._aask(prompt)
        
        logger.info(Colorful.colorful('\n***** 任务执行代理回应****\n','yellow')+ f'{rsp}\n')
        
        # Step 2: Enrich result and store in the results storage
        # This is where you should enrich the result if needed
        enriched_result = {
            "data": rsp
        }
        # extract the actual result from the dictionary
        # since we don't do enrichment currently
        # vector = enriched_result["data"]

        result_id = f"result_{task['task_id']}"

        ContextAgent.add(task, rsp, result_id)



        msg = {
            "result":enriched_result,
            "task_name":task["task_name"],
        }
        
        return msg

        

class Executor(Role):
    name: str = "Charlie"
    profile: str = "TaskExecutor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([Start])
        self.set_actions([ExecutionAgent])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo=self.rc.todo
        context = self.get_memories(k=1)  # use all memories as context
        # logger.info(f"Executor context :{context}")
        res = await todo.run(json.loads(context[0].rag_key()))

        msg = Message(content=json.dumps(res),role = self.profile,cause_by=type(todo))
        return msg   


class TaskCreationAgent(Action):
    PROMPT_TEMPLATE: str = """
    请在答复中每行填写一项任务。结果必须是一个编号列表，格式为:
    #. 第一个任务 
    #. 第二个任务 
    其中#指代编号。
    输出示例为:
    1. 收集资料
    2. 整理资料
    每个条目的编号后必须有一个英文句号“.”。如果列表是空的，请写 "目前没有任务要添加"。每个任务都要单行输出。
    您要使用执行代理的结果创建新任务，目标如下： {objective}.
    最后完成的任务有结果：  {result} 
    这一结果是根据执行任务：{task} 得出的.
    这些都是未完成的任务： {Uncompleted}
    根据结果，返回为实现目标而需完成的任务列表。
    这些新任务不得与未完成的任务重叠，不能返回重复任务。
    若当前任务足以实现目标则返回为空。
    不要在编号列表前添加任何内容，也不要在编号列表后添加任何其他输出。
    """
    name: str = "TaskCreationAgent"

    async def run(self,  result,task,tasks_list):
        Uncompleted=""
        if tasks_list:
            Uncompleted=','.join(item for item in tasks_list)
        prompt = self.PROMPT_TEMPLATE.format(objective=OBJECTIVE,result=result,task=task,Uncompleted=Uncompleted)
        logger.info(Colorful.colorful('\n***** 任务创建代理提示****\n','cyan')+f'{prompt}\n')
        logger.info(Colorful.colorful('\n***** LLM响应****\n','cyan'))#不知道为何会在这里print rsp,非log
        rsp = await self._aask(prompt)

        logger.info(Colorful.colorful('\n**** 任务创建代理响应****\n','yellow') +rsp+'\n')
        new_tasks = rsp.split('\n')
        new_tasks_list=[]
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = ''.join(s for s in task_parts[0] if s.isnumeric())
                task_name = re.sub(r'[^\w\s_]+', '', task_parts[1]).strip()
                if task_name.strip() and task_id.isnumeric():
                    new_tasks_list.append({"task_name": task_name} )
        return new_tasks_list
class Creator(Role):
    name: str = "Jesus"
    profile: str = "TaskCreator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([ExecutionAgent])
        self.set_actions([TaskCreationAgent])
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo=self.rc.todo
        context = self.get_memories(k=1)  # use all memories as context
        # logger.info(f"Creator context :{context}")
        content = json.loads(context[0].rag_key())
        
        new_tasks_list=await todo.run(content["result"]["data"],content["task_name"],tasks_storage.get_task_list())
        # logger.info('\n向 task_storage 添加新任务\n')
        for new_task in new_tasks_list:
            new_task.update({"id": tasks_storage.next_task_id()})
            tasks_storage.append(new_task)
            # logger.info(f'\nNew task created:\n{new_task}\n')
        msg = Message(content="DONE",role = self.profile,cause_by=type(todo))
        return msg

class PrioritizationAgent(Action):
    PROMPT_TEMPLATE: str = """
    任务应按优先级从高到低排序，其中优先级较高的任务是实现目标的先决条件或更重要的任务。
    不要删除任何任务。以编号列表的格式返回已排序的任务：
    #. 第一项任务 
    #. 第二个任务
    其中#指代编号。 
    输出示例为:
    1. 收集资料
    2. 整理资料
    条目必须连续编号，从 1 开始。 每个条目的编号后必须有一个英文句号“.”。每个任务都要单行输出。
    请勿在排序列表前添加任何标题，也不要在列表后添加任何其他输出。
    您的任务是确定以下任务的优先次序： {task_list} 
    考虑团队的最终目标：{OBJECTIVE} 
    """
    name: str = "PrioritizationAgent"

    async def run(self,task_names):
        
        bullet_string = '\n'
        task_list=bullet_string + bullet_string.join(task_names)
        prompt = self.PROMPT_TEMPLATE.format(OBJECTIVE=OBJECTIVE,task_list=task_list)
        logger.info(Colorful.colorful('\n***** 优先级代理提示****\n','cyan')+f'{prompt}\n')
        logger.info(Colorful.colorful('\n***** LLM响应****\n','cyan'))
        rsp = await self._aask(prompt)
        logger.info(Colorful.colorful('\n***** 优先级代理响应****\n','yellow') +f'{rsp}\n')
        if not rsp:
            logger.info('\n收到来自优先权代理的空回复。任务列表保持不变。\n')
            return
        new_tasks = rsp.split("\n") if "\n" in rsp else [rsp]
        new_tasks_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = ''.join(s for s in task_parts[0] if s.isnumeric())
                task_name = re.sub(r'[^\w\s_]+', '', task_parts[1]).strip()
                if task_name.strip():
                    new_tasks_list.append({"task_id": task_id, "task_name": task_name})
       
        time.sleep(5)
        msg = {
            "new_tasks_list":new_tasks_list,
        }

        return msg
        
class Sorter(Role):
    name: str = "Brian"
    profile: str = "TaskPrioritySorter"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch([TaskCreationAgent])
        self.set_actions([PrioritizationAgent])
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo=self.rc.todo
        # context = self.get_memories(k=1)  # use all memories as context
        # logger.info(f"Sorter context :{context}")
        res = await todo.run(tasks_storage.get_task_list())
        msg = Message(content=json.dumps(res),role = self.profile,cause_by=type(todo))
        return msg



async def main(
    investment: float = 3.0,
    n_round: int = 20,
):


    team = Team()
    team.hire(
        [
            Connector(),
            Executor(),
            Creator(),
            Sorter(),
        ]
    )


    initial_task = {
        "task_id": tasks_storage.next_task_id(),
        "task_name": INITIAL_TASK
    }
    tasks_storage.append(initial_task)

    task = tasks_storage.get_left()
    content = json.dumps({"new_tasks_list":[task]})

    team.invest(investment=investment)
    team.run_project(content,send_to="Kobe")
    await team.run(n_round=n_round)




if __name__ == "__main__":
    fire.Fire(main)