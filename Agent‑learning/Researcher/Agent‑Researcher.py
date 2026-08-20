from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# ============密钥配置============
DEEPSEEK_API_KEY = "sk-2aa52a3d208a44b6b97b1c2311e8b86e"
TAVILY_API_KEY = "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"
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# ============初始化大模型============
llm = ChatOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    temperature=0
)

# ============注册工具============
# 联网搜索工具
search_tool = TavilySearchResults(max_results=3)

@tool
def save_report(content: str, filename: str = "survey_report.md") -> str:
    """
    将生成的调研报告保存到本地Markdown文件
    Args:
        content: 需要写入报告的完整markdown文本
        filename:输出文件名，默认 survey_report.md
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅调研报告已保存到本地文件：{filename}"

tools = [search_tool, save_report]

# ============创建Agent============
agent = create_agent(llm, tools)

# ============启动调研任务============
if __name__ == "__main__":
    task = "调研2026年AI‑Agent方向实习生岗位的招聘要求以及主流技术栈，输出一份结构完整的调研报告，调研完成后调用save_report工具保存结果。"
    res = agent.invoke({"messages": [("user", task)]})
    print("\n====调研任务执行完毕====")
    print(res["messages"][-1].content)