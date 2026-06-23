import os
import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END


# 1. 定义状态
class AggregateState(TypedDict):
    # 使用 operator.add 让列表自动拼接
    aggregate: Annotated[list, operator.add]


# 2. 定义节点函数
def node_a(state: AggregateState):
    print(f"添加'A'到{state['aggregate']}")
    return {'aggregate': ['A']}


def node_b(state: AggregateState):
    print(f"添加'B'到{state['aggregate']}")
    return {'aggregate': ['B']}


def node_c(state: AggregateState):
    print(f"添加'C'到{state['aggregate']}")
    return {'aggregate': ['C']}


def node_d(state: AggregateState):
    print(f"添加'D'到{state['aggregate']}")
    return {'aggregate': ['D']}


def router(state: AggregateState):
    if len(state['aggregate']) < 7:
        return "node_b"
    else:
        return END


# 3. 构建图
graph = StateGraph(AggregateState)

# 添加所有节点
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)

# --- 连接边 (关键部分) ---

# 1. Start -> A
graph.add_edge(START, "node_a")

# 2. A -> B (串行)
graph.add_conditional_edges(
    "node_a",
    router,
    {
        "node_b": "node_b",
        END: END,
    }
)

graph.add_edge("node_b", "node_c")
graph.add_edge("node_b", "node_d")
graph.add_edge("node_c", "node_a")
graph.add_edge("node_d", "node_a")

# 4. 编译并绘图
# 4. 编译并绘图
try:
    graph_build = graph.compile()

    # 尝试生成 Mermaid PNG
    mermaid_png = graph_build.get_graph().draw_mermaid_png()
    filename = "graph_structure4.png"
    with open(filename, "wb") as f:
        f.write(mermaid_png)

    print(f"图片已生成：{filename}")
    # Windows 下自动打开图片
    if os.name == 'nt':
        os.startfile(os.path.abspath(filename))

except Exception as e:
    print(f"绘图失败: {e}")
    # 如果 PNG 生成失败（比如缺 Graphviz），打印 Mermaid 文本供你在线查看
    print("--- Mermaid 源码 (可复制到 mermaid.live 查看) ---")
    print(graph_build.get_graph().draw_mermaid())
