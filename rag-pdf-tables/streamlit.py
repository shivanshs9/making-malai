import logging
import os

import pandas as pd
import pandasai as pdai
import streamlit as st
from dotenv import load_dotenv
from langchain_community.chat_models import ChatPerplexity
from pandasai.chat.response.response_types import Base
from pandasai_langchain import LangchainLLM

load_dotenv()
logger = logging.getLogger(__name__)

dataset_folder = os.path.join(os.path.dirname(__file__), "dataset")
dataset_metadata = {
    "2022-all-prefectures": {
        "description": "Dataset containing counts of different class of driving license holders in all prefectures of Japan in 2022",
    },
    "2022-new-prefectures": {
        "description": "Dataset containing new licenses issued for different class of driving license in all prefectures of Japan in 2022",
    },
    "2022-new-ages": {
        "description": "Dataset containing new licenses issued for different class of driving license across different age ranges in Japan in 2022",
    },
}

META_DATA_URL = (
    "https://www.npa.go.jp/publications/statistics/koutsuu/menkyo/r04/r04_sub1.pdf"
)


def get_smart_agent():
    datalake = []
    llm = ChatPerplexity(
        temperature=0,
        model="llama-3.1-sonar-large-128k-online",
        pplx_api_key=os.environ.get("PPLX_API_KEY"),
    )
    pdai.config.set({"llm": LangchainLLM(llm)})
    for data_name, meta in dataset_metadata.items():
        data_path = os.path.join(dataset_folder, f"{data_name}.parquet")
        df = pd.read_parquet(data_path)
        # Remove last row as it contains total (really skewes the data)
        df.drop(df.tail(1).index, inplace=True)
        datalake.append(
            pdai.DataFrame(df, name=data_name, description=meta["description"])
        )
    return pdai.Agent(datalake)


def main():
    agent = get_smart_agent()

    st.title("Analysis of 2022 Japan Driving license data")
    with st.expander("ℹ️ Disclaimer"):
        st.caption(
            f"""
            No gurarantees that the answers will be 100% hallucination-free; take with a grain of salt.

            [Datasource]({META_DATA_URL}) provided by [National Police Agency of Japan](https://www.npa.go.jp/)
            """
        )
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                answer = None
                if len(st.session_state.messages) == 1:
                    answer = agent.chat(prompt)
                else:
                    answer = agent.follow_up(prompt)
                json_answer = {"type": "string", "value": answer}
                if isinstance(answer, Base):
                    json_answer = answer.to_dict()
                markdown_answer = json_answer["value"]
                if json_answer["type"] == "plot":
                    markdown_answer = f"![plot]({json_answer['value']})"
                    st.image(json_answer["value"], use_container_width=True)
                else:
                    st.write(markdown_answer)
                agent.add_message(answer, is_user=False)
                st.session_state.messages.append(
                    {"role": "assistant", "content": markdown_answer}
                )
            except Exception as e:
                logger.error("Agent failed to answer", exc_info=True)
                humane_msg = """
                    Oops! Sorry, there's been some error. Checking logs might be helpful!
                """
                st.session_state.messages.append(
                    {"role": "assistant", "content": humane_msg}
                )
                st.rerun()


if __name__ == "__main__":
    main()
