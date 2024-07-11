#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/5/11 17:25
@Author  : GG-Lizen
@File    : search_cad.py
"""

import asyncio

from metagpt.roles import CADSearcher


async def main():
    await CADSearcher().run("抗干扰、抗电磁干扰的路由器")


if __name__ == "__main__":
    asyncio.run(main())
