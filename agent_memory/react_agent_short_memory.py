import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState,StateGraph,START,END

# 加载环境
load_dotenv()

# 使用内存来存储记忆
memory = MemorySaver()
# 定义工具
@tool
def search(query: str) -> str:
    """调用此函数可以浏览网络"""
    # 模拟一个网络搜索返回
    return "北京天气晴朗 大约22度 湿度30%"
tools = [search]
# langgraph的内置工具 返回工具执行的值
tool_node = ToolNode(tools)
# 初始化模型
deepseek_llm= ChatDeepSeek(
    model= 'Pro/deepseek-ai/DeepSeek-V3',
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url=os.getenv('DEEPSEEK_BASE_URL'),
    temperature=0.0
    )
bound_model = deepseek_llm.bind_tools(tools)
# 定义节点
def should_continue(state: MessagesState):
    """返回下一个要执行的节点"""
    last_message = state['messages'][-1]
    if not last_message.tool_calls:
        return END
    return 'action'
# 定义调用模型的函数
def call_model(state: MessagesState):
    response = bound_model.invoke(state['messages'])
    # 返回列表
    return {'messages': response}
# 定义图
workflow = StateGraph(MessagesState)
# 添加节点
workflow.add_node("agent", call_model)
workflow.add_node("action",tool_node)
# 添加边
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["action", END]
)
workflow.add_edge("action", "agent")
app = workflow.compile(checkpointer=memory)
ermaid_png = app.get_graph().draw_mermaid_png()
with open("graph_structure.png", "wb") as f:
    f.write(ermaid_png)

os.startfile(os.path.abspath("graph_structure.png"))