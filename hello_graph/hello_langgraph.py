# TypedDict:Python标准库Typing模块部分，提供静态类型检查，运行时不执行验证
# Pydantic:Python第三方库，提供数据验证、序列化和文档生成功能，支持静态类型检查
import os
from typing import Annotated
from langgraph.graph import START,END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage


# 定义state:节点和节点之间的数据流
class MessageState():
    # 可以自动处理列表消息合并
    message: Annotated[list[AnyMessage], add_messages]
    extra_field: int = 0


# 定义节点
def node_ai(state: MessageState) -> dict[str, int | list[AIMessage]]:
    """模拟 AI 回复"""
    print(">>> 正在执行 node_ai ...")
    new_message = AIMessage(content="你好，我是AI助手！有什么可以帮你的吗？")
    return {
        'messages': [new_message],
        'extra_field': state.extra_field + 1
    }


def node_human(state: MessageState) -> dict[str, int | list[HumanMessage]]:
    """模拟用户回复"""
    print(">>> 正在执行 node_human ...")
    new_message = HumanMessage(content="你好，我是Tony,我想了解Python！")
    return {
        'messages': [new_message],
        'extra_field': state.extra_field + 1
    }
# 创建图 包含节点和边
graph = StateGraph(MessageState)
graph.add_node("node_ai", node_ai)
graph.add_node("node_human", node_human)
graph.add_edge(START, "node_ai")
graph.add_edge("node_ai", "node_human")
graph.add_edge("node_human", END)
# 编译图
graph_build = graph.compile()
mermaid_png = graph_build.get_graph().draw_mermaid_png()
with open("graph_structure.png", "wb") as f:
    f.write(mermaid_png)

os.startfile(os.path.abspath("graph_structure.png"))