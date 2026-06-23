import os, operator
from typing import Annotated, TypedDict, Literal

from langgraph.errors import GraphRecursionError
from langgraph.graph import StateGraph, START, END

# 定义状态类型
class AggregateState(TypedDict):
    aggregate: Annotated[list, operator.add]

# 定义节点函数
def node_a(state: AggregateState):
    print(f'Node A sees {state["aggregate"]}')
    return {"aggregate": ["A"]}


def node_b(state: AggregateState):
    print(f'Node B sees {state["aggregate"]}')
    return {"aggregate": ["B"]}
# 创建状态图 添加节点
graph = StateGraph(AggregateState)
graph.add_node('node_a', node_a)
graph.add_node('node_b', node_b)
# 定义route
def route(state: AggregateState)-> Literal["node_b", END]:
    if len(state['aggregate']) < 7:
        return 'node_b'
    else:
        return END
# 添加边以及条件边
graph.add_edge(START, "node_a")
graph.add_conditional_edges("node_a", route)
graph.add_edge("node_b", 'node_a')
# 编译图
graph_build = graph.compile()
# 保存图为图片
mermaid_png =graph_build.get_graph().draw_mermaid_png()
with open("graph_structure2.png", "wb") as f:
    f.write(mermaid_png)
os.startfile(os.path.abspath("graph_structure2.png"))
# 执行图 并限制次数
try:
    result = graph_build.invoke({'aggregate': []}, {'recursion_limit': 5})
    print(result)
except GraphRecursionError as e:
    print(f"⚠️ 达到递归限制，程序已安全停止。")
    print(f"错误信息：{e}")
