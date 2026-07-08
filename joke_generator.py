from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
import os
import streamlit as st

load_dotenv()

MODEL1_NAME = "gpt-5.4-mini"
MODEL2_NAME = "claude-sonnet-5"

prompt1 = PromptTemplate.from_template(
    "Tell {no_of_jokes} dark jokes about {topic}"
)

prompt2 = PromptTemplate.from_template(
    """You are a comedy expert.
Analyze these jokes:
{joke}

Create a funnier version of each joke.
For each joke, return:
- Old joke: [original joke]
- New joke: [improved version]
- Analysis: [why the new version is funnier]
Make the new jokes DARKER and more SARCASTIC than the originals!"""
)


@st.cache_resource
def build_chain():
    model1 = ChatOpenAI(
        model=MODEL1_NAME,
        temperature=0.9,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    model2 = ChatAnthropic(
        model=MODEL2_NAME,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    parser = StrOutputParser()
    return (
        prompt1
        | model1
        | parser
        | RunnableLambda(lambda joke: {"joke": joke})
        | prompt2
        | model2
        | parser
    )


def validate_api_keys():
    missing_keys = [
        key
        for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
        if not os.getenv(key)
    ]

    if missing_keys:
        st.error(f"Missing API key(s): {', '.join(missing_keys)}")
        st.stop()


def generate_jokes(no_of_jokes, topic):
    chain = build_chain()
    return chain.invoke({
        "no_of_jokes": no_of_jokes,
        "topic": topic,
    })


st.set_page_config(
    page_title="Dark Joke Improver",
    page_icon=":performing_arts:",
    layout="centered",
)

st.title("Dark Joke Improver")
st.caption("Model 1 writes the jokes. Model 2 analyzes them and makes them sharper.")

validate_api_keys()

with st.sidebar:
    st.header("Pipeline")
    st.write(f"Generator: `{MODEL1_NAME}`")
    st.write(f"Comedy editor: `{MODEL2_NAME}`")

if "joke_history" not in st.session_state:
    st.session_state.joke_history = []

with st.form("joke_form"):
    topic = st.text_input("Topic", placeholder="Example: exams, coding, office meetings")
    no_of_jokes = st.number_input(
        "Number of jokes",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )
    submitted = st.form_submit_button("Generate")

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("Generating and improving jokes..."):
            try:
                response = generate_jokes(no_of_jokes, topic.strip())
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
            else:
                st.session_state.joke_history.insert(0, {
                    "topic": topic.strip(),
                    "no_of_jokes": no_of_jokes,
                    "response": response,
                })

if st.session_state.joke_history:
    latest = st.session_state.joke_history[0]
    st.subheader("Final Output")
    st.markdown(latest["response"])

    with st.expander("Previous generations"):
        for item in st.session_state.joke_history[1:]:
            st.markdown(f"**{item['no_of_jokes']} joke(s) about {item['topic']}**")
            st.markdown(item["response"])
            st.divider()
else:
    st.info("Choose a topic and generate jokes to see the final output here.")


