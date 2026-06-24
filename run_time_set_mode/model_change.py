# 图的运行时配置
import os,operator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Annotated, Sequence
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage, HumanMessage
# 加载环境
load_dotenv()
# 初始化模型
deepseek_model = ChatDeepSeek(
    model = 'deepseek-chat',
    api_key = os.getenv('DEEPSEEK_API_KEY'),
    base_url = os.getenv('DEEPSEEK_BASE_URL'),
    temperature = 0.0,

)
openai_model = ChatOpenAI(
    model = 'gpt-3.5-turbo',
    api_key = os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL'),
    temperature = 0.0,
    )
# 定义切换模型的结构
models = {
    'deepseek': deepseek_model,
    'openai': openai_model
}
# 定义消息列表
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],operator.add]
# 定义模型执行节点
def _call_model(state: AgentState, config:RunnableConfig):
    # 获取模型名称
    model_name = config['configurable'].get('model', 'deepseek')
    # 获取模型
    model = models[model_name]
    response = model.invoke(state['messages'])
    return {'messages':[response]}
# 创建图
graph = StateGraph(AgentState)
graph.add_node('call_model', _call_model)

graph.add_edge(START, 'call_model')
graph.add_edge('call_model', END)

# 编译运行
graph_build = graph.compile()
# 运行 默认使用deepseek 配置切换模型
config = {'configurable': {'model': 'openai'}}

result = graph_build.invoke({'messages':[HumanMessage(content='hi,你是谁？')]}, config=config)
print(result)
mermaid_png = graph_build.get_graph().draw_mermaid_png()
with open("graph_structure.png", "wb") as f:
    f.write(mermaid_png)

os.startfile(os.path.abspath("graph_structure.png"))