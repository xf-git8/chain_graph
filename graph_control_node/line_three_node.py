import operator
import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# 定义状态类型
class StrState(TypedDict):
    value_1: Annotated[list[str], operator.add]
    value_2: Annotated[list[str], operator.add]


# 定义步骤节点
def node_step1(state: StrState) -> StrState:
    print (">>> 正在执行 node_step1 ...")
    return {'value_1':['cc']}


def node_step2(state: StrState) -> StrState:
    current_value_1 = state['value_1']
    print(">>> 正在执行 node_step2 ...")
    print(">>> 当前 value_1:", current_value_1)
    return {'value_1': ['254'], 'value_2': ['world']}


def node_step3(state: StrState) -> StrState:
    current_value_1 = state['value_1']
    current_value_2 = state['value_2']
    print(">>> 正在执行 node_step3 ...")
    return {}


# 定义图
graph = StateGraph(StrState)
graph.add_node("node_step1", node_step1)
graph.add_node("node_step2", node_step2)
graph.add_node("node_step3", node_step3)
graph.add_edge(START, "node_step1")
graph.add_edge("node_step1", "node_step2")
graph.add_edge("node_step2", "node_step3")
graph.add_edge("node_step3", END)
# 编译图
graph_build = graph.compile()
# 保存图为图片
mermaid_png = graph_build.get_graph().draw_mermaid_png()
with open("graph_structure3.png", "wb") as f:
    f.write(mermaid_png)
os.startfile(os.path.abspath("graph_structure3.png"))
# 运行
result = graph_build.invoke({"value_1": ["initial"], "value_2": ["hello"]})
print(result['value_1'])
print(result['value_2'])
