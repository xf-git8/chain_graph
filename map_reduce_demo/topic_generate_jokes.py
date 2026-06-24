import os, operator
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.types import Send
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# 加载环境
load_dotenv()

# 定义提示词
subjects_prompt = """生成一个逗号分割的列表，包含5-8个与以下主题相关的例子：{topic}"""
joke_prompt = """生成一个关于{subject}的笑话，要求简短有趣，不要超过50字"""
best_joke_prompt = """以下是关于{topic}的笑话，从以下笑话中选择最好的一个，返回最佳笑话的ID：\n{jokes}"""

# 定义模型（只定义一次）
gpt_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# 定义数据模型
class Subjects(BaseModel):
    subjects: str

class Joke(BaseModel):
    joke: str

class BestJoke(TypedDict):
    id: int = Field(description='最佳笑话的索引,从0开始', ge=0)

# 定义状态
class OverState(TypedDict):
    topic: str
    subjects: list
    jokes: Annotated[list, operator.add]
    best_joke: str

class JokeState(TypedDict):
    subject: str

# 节点：生成子话题
def generate_topics(state: OverState):
    prompt = subjects_prompt.format(topic=state['topic'])
    response = gpt_llm.with_structured_output(Subjects).invoke(prompt)
    # 将逗号分隔的字符串转为列表
    subjects_list = [s.strip() for s in response.subjects.split(",")]
    return {"subjects": subjects_list}

# 节点：根据子话题生成笑话
def generate_jokes(state: JokeState):
    prompt = joke_prompt.format(subject=state['subject'])
    response = gpt_llm.with_structured_output(Joke).invoke(prompt)
    return {"jokes": [response.joke]}  # ← 修复：key 改为 "jokes"，值为 list

# 边缘逻辑：动态扇出到 generate_jokes
def continue_to_jokes(state: OverState):
    return [Send("generate_jokes", {"subject": s}) for s in state['subjects']]

# 节点：选择最佳笑话
def best_joke(state: OverState):
    # 带编号格式，方便 LLM 识别
    jokes = "\n\n".join([f"ID {i}: {j}" for i, j in enumerate(state['jokes'])])
    prompt = best_joke_prompt.format(topic=state['topic'], jokes=jokes)
    response = gpt_llm.with_structured_output(BestJoke).invoke(prompt)
    return {"best_joke": state['jokes'][response['id']]}

# 构建图
graph = StateGraph(OverState)
graph.add_node("generate_topics", generate_topics)
graph.add_node("generate_jokes", generate_jokes)
graph.add_node("best_joke", best_joke)

graph.add_edge(START, "generate_topics")
graph.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_jokes"])
graph.add_edge("generate_jokes", "best_joke")
graph.add_edge("best_joke", END)

app = graph.compile()
mermaid_png =app.get_graph().draw_mermaid_png()
with open("graph_structure3.png", "wb") as f:
    f.write(mermaid_png)
os.startfile(os.path.abspath("graph_structure3.png"))
# 运行
result = app.invoke({"topic": "动物"})
print("主题：", result['topic'])
print("子话题：", result['subjects'])
print("所有笑话：")
for i, joke in enumerate(result['jokes']):
    print(f"  [{i}] {joke}")
print("最佳笑话：", result['best_joke'])