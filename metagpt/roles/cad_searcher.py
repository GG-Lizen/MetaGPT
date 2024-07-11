#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/11 17:25
@Author  : GG-Lizen
@File    : cad_searcher.py
"""


from typing import Optional

from pydantic import Field, model_validator

from metagpt.actions import CADSearchAndSummarize
from metagpt.actions.action_node import ActionNode
from metagpt.actions.action_output import ActionOutput
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.tools.search_engine import SearchEngine


class CADSearcher(Role):
    """
    Represents a Searcher role responsible for providing search services to users.

    Attributes:
        name (str): Name of the searcher.
        profile (str): Role profile.
        goal (str): Goal of the searcher.
        constraints (str): Constraints or limitations for the searcher.
        search_engine (SearchEngine): The search engine to use.
    """

    name: str = Field(default="Faker")
    profile: str = Field(default="Smart Assistant")
    goal: str = "Provide search services for users"
    constraints: str = "Answer is rich and complete"
    search_engine: Optional[SearchEngine] = None

    @model_validator(mode="after")
    def post_root(self):
        if self.search_engine:
            self.set_actions([CADSearchAndSummarize(search_engine=self.search_engine, context=self.context)])
        else:
            self.set_actions([CADSearchAndSummarize])
        return self

    async def _act_sp(self) -> Message:
        """Performs the search action in a single process."""
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        
        response = await self.rc.todo.run(self.rc.memory.get(k=0))

        if isinstance(response, (ActionOutput, ActionNode)):
            msg = Message(
                content=response.content,
                instruct_content=response.instruct_content,
                role=self.profile,
                cause_by=self.rc.todo,
            )
        else:
            msg = Message(content=response, role=self.profile, cause_by=self.rc.todo)
        self.rc.memory.add(msg)
        return msg

    async def _act(self) -> Message:
        """Determines the mode of action for the searcher."""
        return await self._act_sp()
