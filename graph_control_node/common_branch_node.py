import os, operator
from typing import Any,Annotated,TypedDict
from langgraph.graph import StateGraph,START,END

# 定义消息状态
class AggregateState(TypedDict):
    aggregate:Annotated[list,operator.add]

# 定义节点
def node_a(state:AggregateState):
    print(f"添加'A'到{state['aggregate']}")
    return {'aggregate':['A']}
def node_b(state:AggregateState):
    print(f"添加'B'到{state['aggregate']}")
    return {'aggregate':['B']}
def node_c(state:AggregateState):
    print(f"添加'C'到{state['aggregate']}")
    return {'aggregate':['C']}
def node_d(state:AggregateState):
    print(f"添加'D'到{state['aggregate']}")
    return {'aggregate':['D']}
# 创建图
graph = StateGraph(AggregateState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)
# 添加边
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_a", "node_c")
graph.add_edge("node_b", "node_d")
graph.add_edge("node_c", "node_d")
graph.add_edge("node_d", END)
# 编译
graph = graph.compile()
mermaid_png = graph.get_graph().draw_mermaid_png()
# 保存图为图片
with open("graph_structure1.png", "wb") as f:
    f.write(mermaid_png)
os.startfile(os.path.abspath("graph_structure1.png"))
result = graph.invoke({"aggregate":[]},{"configurable":{"thread_id":"foo"}})
print(result)