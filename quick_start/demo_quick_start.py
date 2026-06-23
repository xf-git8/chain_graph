import os, operator
from typing import Literal
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph,START,END
from typing_extensions import TypedDict,Annotated
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

# 加载环境
load_dotenv()


# 定义工具
@tool
def multiply(a: int, b: int):
    """Multiply two numbers.
    Args:
        a (int): The first number.
        b (int): The second number.
    """
    return a * b


@tool
def add(a: int, b: int):
    """Add two numbers.
    Args:
        a (int): The first number.
        b (int): The second number.
    """
    return a + b


@tool
def divide(a: int, b: int):
    """Divide two numbers.
    Args:
        a (int): The first number.
        b (int): The second number.
    """
    return a / b


tools = [multiply, add, divide]
tools_name = {tool.name: tool for tool in tools}
# 初始化模型并绑定工具
gpt_llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)
# 定义状态
class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
# 定义模型节点
def llm_call(state: MessageState):
    """模型决定是否调用工具"""
    return {
        "messages": [
            gpt_llm.invoke([
                               SystemMessage(
                                   content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")
                           ] + state["messages"]),
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# 定义工具节点
def tool_node(state: MessageState):
    """Performs the tool call"""
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_name[tool_call['name']]
        observation = tool.invoke(tool_call['args'])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call['id']))
    return {
        "messages": result
    }


# 定义逻辑决定是否结束
# Conditional edge function to route to the tool node or end
# based upon whether the LLM made a tool call
def should_continue(state: MessageState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"
    # Otherwise, we stop (reply to the user)
    return END


# 定义agent
# build the graph
agent_builder = StateGraph(MessageState)
# 添加节点
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
# 添加变连接节点
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")
# 编译agent
agent = agent_builder.compile()
# 运行agent
messages = agent.invoke({
    "messages": [HumanMessage(content="Add 3 and 4.")],
    "llm_calls": 0
})
for m in messages['messages']:
    m.pretty_print()
# 保存图为图片
mermaid_png = agent.get_graph().draw_mermaid_png()
with open("graph_structure.png", "wb") as f:
    f.write(mermaid_png)

os.startfile(os.path.abspath("graph_structure.png"))