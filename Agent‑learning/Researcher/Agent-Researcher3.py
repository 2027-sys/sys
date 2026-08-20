from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage
import os
#拆分子任务但是不是自动的，下一版4进行升级
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

# ============工具定义============
search_tool = TavilySearch(max_results=3)

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
    full_path = os.path.abspath(filename)
    print(f"\n[日志‑保存文件] 报告已写入：{full_path}")
    return f"✅调研报告已保存到本地文件：{filename}"


tools = [search_tool, save_report]
agent = create_agent(llm, tools)


def generate_sub_tasks(main_query: str):
    """步骤1：将主调研任务拆分成子任务列表"""
    prompt = f"""
你是任务规划助手，请把下面这份调研需求，拆分成4‑5个独立的、适合上网搜索的子任务。
只输出json数组，不要多余文字。
调研需求：{main_query}
"""
    resp = llm.invoke([HumanMessage(prompt)])
    print("\n=====生成的子调研任务=====")
    print(resp.content)
    return resp.content


def run_sub_task(subtask: str) -> str:
    """步骤2：执行单个子任务调研，返回搜索素材"""
    print(f"\n-----开始执行子任务：{subtask}-----")
    res = agent.invoke({"messages": [("user", subtask+"，只搜集调研素材，不要生成最终报告。")]})
    return res["messages"][-1].content


def generate_final_report(main_query: str, all_material: str):
    """步骤3：汇总全部素材生成最终调研报告并保存"""
    final_prompt = f"""
基于下面搜集到的所有调研素材，针对问题：{main_query}
输出一份结构完整、逻辑清晰的markdown调研报告，完成后调用save_report工具保存报告。

调研素材汇总：
{all_material}
"""
    result = agent.invoke({"messages": [("user", final_prompt)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print("=====带任务规划调研Agent启动=====")
    main_task = "调研2026年双非学校的农业工程专业特别是yolo改进作为毕业论文的硕士研究生的就业情况"

    # 1、拆分任务
    sub_task_text = generate_sub_tasks(main_task)

    # 2、逐条搜索收集素材
    material_pool = ""
    sub_query_list = [
        "2026年双非农业工程硕士就业方向以及热门岗位",
        "YOLO目标检测改进项目经历 可以投递哪些岗位",
        "双非硕士投递计算机视觉CV岗难点、企业招聘偏好",
        "农业工程+计算机视觉方向应届生薪资、面经、提升路线建议"
    ]
    for sq in sub_query_list:
        one_result = run_sub_task(sq)
        material_pool += f"\n====素材板块：{sq}====\n{one_result}"

    # 3、汇总素材生成报告并自动保存
    final = generate_final_report(main_task, material_pool)
    print("\n====调研全部完成=====")
    print(final)
