import streamlit as st
from streamlit_chat import message
from langchain.retrievers import AzureCognitiveSearchRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from mainIdea import get_main_idea
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
from Scraper.scrap import scrape
import subprocess
import time

load_dotenv()

memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True, output_key="answer"
)


def load_chain():
    prompt_template = """You are a helpful assistant for questions about Donald Trump.

    {context}

    Question: {question}
    Answer here:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    retriever = AzureCognitiveSearchRetriever(content_key="content", top_k=10)
    #print(retriever)
    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(),
        memory=memory,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": PROMPT},
    )
    return chain


chain = load_chain()

st.set_page_config(page_title="Trust me, bro", page_icon=":robot:")
st.header("Trust me, bro")

c2 = st.columns(2)

# Displaying an image within a stylable container
with c2[0]:
    with stylable_container(
        key="logo_image",
        css_styles="""
        img {
            border-radius: 2em;
        }
        """,
    ):
        st.image("./logo.png")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []


def get_text():
    input_text = st.text_input("You: ", "", key="input")
    mainIdea = get_main_idea(input_text)
    print("getting main idea")
    data = scrape(mainIdea)

    with open('Data/data.txt', 'w') as f:
        f.write(data)
    subprocess.run(['python', 'blob.py'])
    subprocess.run(['python', 'AiSearch.py'])
    return input_text


user_input = get_text()

if user_input:
    output = chain.run(question=user_input) #where info is sent
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state["generated"]:
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")