import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph,START,MessagesState, END

load_dotenv()
gpt_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
def call_mode(state: MessagesState):
    response = gpt_llm.invoke(state['messages'])
    return {'messages': response}
graph = StateGraph(MessagesState)
graph.add_node('call_mode', call_mode)
graph.add_edge(START, 'call_mode')
memory = InMemorySaver()
# 开启持久化
graph_build = graph.compile(checkpointer=memory)
config = {'configurable':{'thread_id':1}}
input_message = {'role': 'user', 'content': 'hi,我是Tony'}
for chunk in graph_build.stream({'messages':[input_message]},config,stream_mode="values"):
    chunk['messages'][-1].pretty_print()
input_message = {'role': 'user', 'content': '我叫什么名字？'}
for chunk in graph_build.stream({'messages':[input_message]},config,stream_mode="values"):
    chunk['messages'][-1].pretty_print()
config = {'configurable':{'thread_id':2}}
input_message = {'role': 'user', 'content': '我叫什么名字？'}
for chunk in graph_build.stream({'messages':[input_message]},config,stream_mode="values"):
    chunk['messages'][-1].pretty_print()
# graph_build = graph.compile()
# mermaid_png =graph_build.get_graph().draw_mermaid_png()
# with open("graph_structure3.png", "wb") as f:
#     f.write(mermaid_png)
# os.startfile(os.path.abspath("graph_structure3.png"))
# 没有激活持久层是模型恢复没有记忆状态
# input_message = {'role': 'user', 'content': 'hi,我是Tony'}
# for chunk in graph_build.stream({'messages':[input_message]},stream_mode="values"):
#     chunk['messages'][-1].pretty_print()
# input_message = {'role': 'user', 'content': '我叫什么名字？'}
# for chunk in graph_build.stream({'messages':[input_message]},stream_mode="values"):
#     chunk['messages'][-1].pretty_print()
