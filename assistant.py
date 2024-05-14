import json
from pathlib import Path
from textwrap import dedent

from phi.assistant.assistant import Assistant
from phi.knowledge.base import AssistantKnowledge
from phi.tools.toolkit import Toolkit
from phi.tools.exa import ExaTools
from phi.tools.shell import ShellTools
from phi.tools.calculator import Calculator
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.tools.file import FileTools
from phi.llm.openai.chat import OpenAIChat
from phi.embedder.openai import OpenAIEmbedder
from phi.assistant.duckdb import DuckDbAssistant
from phi.assistant.python import PythonAssistant
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.utils.log import logger
from phi.vectordb.pgvector.pgvector2 import PgVector2

from dotenv import load_dotenv

load_dotenv()

DB_URL: str = 'postgresql+psycopg://ai:ai@localhost:5532/ai'
cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath('scratch')
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)


def get_llm_os(
    llm_id: str = 'gpt-4o',
    calculator: bool = False,
    ddg_search: bool = False,
    file_tools: bool = False,
    shell_tools: bool = False,
    data_analyst: bool = False,
    python_assistant: bool = False,
    research_assistant: bool = False,
    investment_assistant: bool = False,
    user_id: str | None = None,
    run_id: str | None = None,
    debug_mode: bool = True,
) -> Assistant:

    logger.info(f'-*- Creating {llm_id} LLM OS -*-')

    # Add tools available to the LLM OS
    tools: list[Toolkit] = []
    extra_instructions: list[str] = []

    if calculator:
        tools.append(
            Calculator(
                add=True,
                subtract=True,
                multiply=True,
                divide=True,
                exponentiate=True,
                factorial=True,
                is_prime=True,
                square_root=True,
            )
        )

    if ddg_search:
        tools.append(DuckDuckGo(fixed_max_results=3))

    if shell_tools:
        tools.append(ShellTools())
        extra_instructions.append(
            'You can use the `run_shell_command` tool to run shell commands. For example, `run_shell_command(args="ls")`.'
        )

    if file_tools:
        tools.append(FileTools(base_dir=cwd))
        extra_instructions.append(
            'You can use the `read_file` tool to read a file, `save_file` to save a file, and `list_file` to list files in the working directory.'
        )

    # Add team members available to the LLM OS
    team: list[Assistant] = []

    if data_analyst:
        _data_analyst = DuckDbAssistant(
            name='Data Analyst',
            role='Analyze movie data and provide insights',
            semantic_model=json.dumps(
                {
                    'tables': [
                        {
                            'name': 'movies',
                            'description': 'CSV of my favorite movies.',
                            'path': 'https://phidata-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv',
                        }
                    ]
                }
            ),
            base_dir=scratch_dir,
            run_id=None,
        )
        team.append(_data_analyst)
        extra_instructions.append(
            'To answer questions about my favorite movies, delegate the task to the `Data Analyst`.'
        )

    if python_assistant:
        _python_assistant = PythonAssistant(
            name='Python Assistant',
            role='Write and run python code',
            pip_install=True,
            charting_libraries=['streamlit'],
            base_dir=scratch_dir,
            run_id=None,
        )
        team.append(_python_assistant)
        extra_instructions.append(
            'To write and run python code, delegate the task to the `Python Assistant`.'
        )

    if research_assistant:
        _research_assistant = Assistant(
            name='Research Assistant',
            role='Write a research report on a given topic',
            llm=OpenAIChat(model=llm_id),
            description='You are a Senior New York Times researcher tasked with writing a cover story research report.',
            instructions=[
                'For a given topic, use the `search_exa` to get the top 10 search results.',
                'Carefully read the results and generate a final - NYT cover story worthy report in the <report_format> provided below',
                'Make your report engaging, informative, and well-structured',
                'Remember: you are writing for the New York Times, so the quality of the report is important.',
            ],
            expected_output=dedent("""\
            An engaging, informative, and well-structured report in the following format:
            <report_format>
            ## Title

            - **Overview** Brief introduction of the topic.
            - **Important** Why is this topic significant now?

            ### Section 1
            - **Detail 1**
            - **Detail 2**

            ### Section 2
            - **Detail 1**
            - **Detail 2**

            ## Conclusion
            - **Sumarry of report:** Recap of the key findings from the report.
            - **Implications:** What these findings mean for the future.

            ## References
            - [Reference 1](Link to Source)
            - [Reference 2](Link to Source)
            </report_format>
            """),
            tools=[ExaTools(num_results=5, text_length_limit=1000)],
            markdown=True,
            add_datetime_to_instructions=True,
            debug_mode=debug_mode,
            run_id=None,
        )
        team.append(_research_assistant)
        extra_instructions.append(
            'To write a research report, delegate the task to the `Research Assistant`.'
            'Return the report in the <report_format> to the user as is, without any additional text like "here is the report".'
        )

    if investment_assistant:
        _investment_assitant = Assistant(
            name='Investment Assistnat',
            role='Write an investment report on a given company (stock) symbol',
            llm=OpenAIChat(model=llm_id),
            description='You are a Senior Investment Analyst for Goldman Sachs tasked with writing an investment report for a very important client.',
            instructions=[
                'For a given stock symbol, get the stock price, company information, analyst recommendations, and company news',
                'Carefully read the research and generate a final - Goldman Sachs worthy investment report in the <report_format> provided below.',
                'Provide thoughtful insights and recommendations based on the research.',
                'When you share numbers, make sure to include the units (e.g., millions/billions) and currency.',
                'REMEMBER: This report is for a very important client, so the quality of the report is important.',
            ],
            expected_output=dedent("""\
            <reoprt_format>
            ## [Comany Name]: Investment Report

            ### **Overview**
            {give a brief introduction of the company and why the user should read this report}
            {make this section engaging and create a hook for the reader}

            ### Core Metrics
            {provide a summary of core metrics and show the latest data}
            - Current price: {current price}
            - 52-week high: {52-week high}
            - 52-week low: {52-week low}
            - Market Cap: {Market Cap} in billions
            - P/E Ratio: {P/E Ratio}
            - Earnings per Share: {EPS}
            - 50-day average: {50-day average}
            - 200-day average: {200-day average}
            - Analyst Recommendations: {buy, hold, sell} (number of analysts)

            ### Financial Performance
            {analyze the company's financial performance}

            ### Growth Prospects
            {analyze the company's growth prospects and future potential}

            ### News and Updates
            {summarize relevant news that can impact the stock price}

            ### [Summary]
            {give a summary of the report and what are the key takeaways}

            ### [Recommendations]
            {provide a recommendation on the stock along with a thorough reasoning}

            </report_format>
            """),
            tools=[
                YFinanceTools(
                    stock_price=True,
                    company_info=True,
                    analyst_recommendations=True,
                    company_news=True,
                ),
            ],
            markdown=True,
            add_datetime_to_instructions=True,
            debug_mode=debug_mode,
            run_id=None,
        )
        team.append(_investment_assitant)
        extra_instructions.extend([
            'To get an investment report on a stock, delegate the task to the `Investment Assistant`.'
            'Return the report in the <report_format> to the user without any additional text like "here is the report".',
            'Answer any questions they may have using the information in the report.',
            'Neveer provide investment advise without the investment report.',
        ])

    # Create the LLM OS Assistant.
    llm_os = Assistant(
        name='llm_os',
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(model=llm_id),
        description=dedent("""\
        You are the most advanced AI system in the world called `LLM-OS`.
        You have access to a set of tools and a team of AI Assistants at your disposal.
        Your goal is to assist the user in the best way possible.\
        """),
        instructions=[
            'When the user sends a message, first **think** and determine if:\n'
            ' - You can answer by using a tool available to you\n'
            ' - You need to search the knowledge base\n'
            ' - You need to search the internet\n'
            ' - You need to delegate the task to a team member\n'
            ' - You need to ask clarifying question',
            'If the user asks about a topic, first ALWAYS search your knowledge base using the `search_knowledge_base` tool.',
            'If you don\'t find relevant information in your knowledge base, use the `duckduckgo_search` tool to search the internet.',
            'If the user asks to summarize the conversation or if you need to reference your chat history with the user, use the `get_chat_history` tool.',
            'If the user\'s message is unclear, ask clarifying questions to get more information.',
            'Carefully read the information you have gathered and provide a clear and concise answer to the user.',
            'Do not use phrases like "based on my knowledge" or "depending on the information".',
            'You can delegate tasks to an AI Assistant in your team depending on their role and the tools avialable to them.',
        ],
        extra_instructions=extra_instructions,
        # Add long-term memory to the LLM OS backed by a PostgreSQLd database.
        storage=PgAssistantStorage(table_name='llm_os_runs', db_url=DB_URL),
        # Add a knowledge base to the LLM OS.
        knowledge_base=AssistantKnowledge(
            vector_db=PgVector2(
                db_url=DB_URL,
                collection='llm_os_documents',
                embedder=OpenAIEmbedder(
                    model='text-embedding-3-small', dimensions=1536),
            ),
            # 3 references are added to the prompt when searching the knowledge base
            num_documents=3,
        ),
        # Add selected tools to the LLM OS.
        tools=tools,
        team=team,
        show_tool_calls=True,
        search_knowledge=True,
        read_chat_history=True,
        add_chat_history_to_messages=True,
        num_history_messages=4,
        markdown=True,
        add_datetime_to_instructions=True,
        introduction=dedent("""\
        Hi, I'm your LLM OS.
        I have access to a set of tools and AI Assistants to assist you.
        Let's solve some problems together!\
        """),
        debug_mode=debug_mode,
    )

    return llm_os
