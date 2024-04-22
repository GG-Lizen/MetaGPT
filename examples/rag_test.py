import asyncio

from metagpt.rag.engines import SimpleEngine
from metagpt.rag.schema import BM25RetrieverConfig, BM25IndexConfig
from metagpt.const import EXAMPLE_DATA_PATH

DOC_PATH = EXAMPLE_DATA_PATH / "rag/car.pdf"


async def main():
    persist_dir = "./tmp_storage"
    retriever_configs = [BM25RetrieverConfig()]

    # 1. save index
    SimpleEngine.from_docs(input_files=[DOC_PATH], retriever_configs=retriever_configs).persist(persist_dir)

    # 2. load index
    engine = SimpleEngine.from_index(index_config=BM25IndexConfig(persist_path=persist_dir), retriever_configs=retriever_configs)

    # 3. query
    answer = await engine.aquery("在国家环保法要求下，哪些情况下需要对车辆进行报废处理？")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())