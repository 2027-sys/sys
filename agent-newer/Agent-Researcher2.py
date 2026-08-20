from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
import os

# ============密钥配置============
DEEPSEEK_API_KEY = "sk-2aa52a3d208a44b6b97b1c2311e8b86e"
TAVILY_API_KEY = "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"
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# ============初始化大模型============
llm = ChatOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",   # DeepSeek接口地址
    model="deepseek-chat",                  # 选用的大模型
    temperature=0                            # 越低，回答越稳定，随机性越小
)

# ============注册工具============
search_tool = TavilySearch(max_results=3)  # 新版独立包Tavily搜索工具

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
    print(f"\n[日志‑保存文件] 报告已写入：{os.path.abspath(filename)}")
    return f"✅调研报告已保存到本地文件：{filename}"


tools = [search_tool, save_report]

# 新版create_agent不再支持verbose参数
agent = create_agent(llm, tools)

# ============启动调研任务============
if __name__ == "__main__":
    print("=====调研任务开始=====")
    task = "调研2026年双非学校的农业工程专业特别是yolo改进作为毕业论文的硕士研究生的就业情况，输出一份结构完整的调研报告，调研完成后调用save_report工具保存结果。"
    res = agent.invoke({"messages": [("user", task)]})
    print("\n====调研任务执行完毕====")
    print(res["messages"][-1].content)