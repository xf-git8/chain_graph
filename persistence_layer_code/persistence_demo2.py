import os, uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables.config import RunnableConfig
from langchain_community.embeddings import OpenAIEmbeddings
from langgraph.graph import StateGraph, START, MessagesState

load_dotenv()
# 初始化模型
gpt_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
# 设置内存记忆

in_memory_store = InMemoryStore(
    index={
        "embed": OpenAIEmbeddings(
            model="text-embedding-ada-002",  # ← 改这里（原模型不存在导致404）
            api_key=os.getenv("OPENAI_API_KEY"),  # ← 改成 OpenAI key
            base_url=os.getenv("OPENAI_BASE_URL")  # ← 改成 OpenAI base_url
        ),
        'dims': 1536
    }
)


# store 参数传给节点
def call_mode(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    # 从存储中检索用户信息
    user_id = config['configurable']['user_id']
    namespace = ('memories', user_id)
    memories = store.search(namespace, query=state['messages'][-1].content)
    info = "\n".join([d.value['data'] for d in memories])
    sys_msg = f"你是一个正在与用户交谈的小助手。用户信息:{info}"
    # 如果用户要求模型记住信息，则存储新的记忆
    last_message = state['messages'][-1]
    if '记住' in last_message.content.lower() or 'remember' in last_message.content.lower():
        memory = "用户名字是tomiezhang"
        store.put(namespace, str(uuid.uuid4()), {'data': memory})
    response = gpt_llm.invoke(
        [{'role': 'system', 'content': sys_msg}] + state['messages'],
    )
    return {'messages': response}


graph = StateGraph(MessagesState)
graph.add_node('call_mode', call_mode)
graph.add_edge(START, 'call_mode')
graph_build = graph.compile(checkpointer=InMemorySaver(), store=in_memory_store)

# 配置线程id和用户id
config = {'configurable': {'thread_id': '1', 'user_id': '1'}}
input_message = {'role': 'user', 'content': '请记住我的名字叫tomiezhang'}
for chunk in graph_build.stream({'messages': [input_message]}, config, stream_mode='values'):
    print(chunk['messages'][-1].content)
config = {'configurable': {'thread_id': '2', 'user_id': '1'}}
input_message = {'role': 'user', 'content': '请问我叫什么名字？'}
for chunk in graph_build.stream({'messages': [input_message]}, config, stream_mode='values'):
    print(chunk['messages'][-1].content)
config = {'configurable': {'thread_id': '3', 'user_id': '2'}}
input_message = {'role': 'user', 'content': '请问我叫什么名字？'}
for chunk in graph_build.stream({'messages': [input_message]}, config, stream_mode='values'):
    print(chunk['messages'][-1].content)
