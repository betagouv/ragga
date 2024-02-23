import random
import streamlit as st

# import chromadb
import logging
# import sys

# from llama_index.vector_stores import ChromaVectorStore
# from llama_index import VectorStoreIndex
from llama_index.core.chat_engine.types import ChatMode
from index import index

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# stream_handler = logging.StreamHandler(stream=sys.stdout)
# stream_handler.setLevel(logging.DEBUG)

# file_handler = logging.FileHandler("logs.log")
# file_handler.setLevel(logging.DEBUG)

# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

# chroma_client = chromadb.PersistentClient(path="./chroma_db")
# chroma_collection = chroma_client.get_collection("standup-fabrique")
# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
# index = VectorStoreIndex.from_vector_store(vector_store)

# #index = load_data()


st.set_page_config(
    page_title="LlamaIndex + OpenAI + Markdown",
    page_icon="🐫",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)
st.header("LlamaIndex + OpenAI + Markdown")
st.title(
    "Interrogez la doc de betagouv",
)
st.info(
    "Sources utilisées : \n\n - [doc.incubateur.net](https://doc.incubateur.net)\n\n - [beta.gouv.fr/startups](https://github.com/betagouv/beta.gouv.fr/blob/master/content/_startups/)\n\n:warning:  Bot expérimental, retours bienvenus [sur GitHub](https://github.com/betagouv/ragga/issues/new)\n\n",
    icon="💡",
)

if "messages" not in st.session_state.keys():  # Initialize the chat message history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour, je suis betabot, posez-moi vos questions!",
        }
    ]

if "chat_engine" not in st.session_state:
    # set the initial default value of the slider widget
    chat_engine = index.as_chat_engine(
        chat_mode=ChatMode.CONTEXT,
        verbose=True,
        similarity_top_k=5,
        system_prompt="""
Tu es un expert de la documentation betagouv et tu réponds à des questions de manière structurée en t'appuyant uniquement sur le contexte fourni et en ne faisant jamais appel à tes propres connaissances.

Quand des liens sont indiqués dans le contexte, propose les toujours à l'utilisateur en complément de ta réponse.

Lorsqu'un contact est demandé, indiques le contact fourni dans le contexte""",
    )
    st.session_state["chat_engine"] = chat_engine

waiters = [
    "Je refléchis...",
    "Hummmm laissez moi chercher...",
    "Je cherche des réponses...",
]

input = st.chat_input("A votre écoute :)")

if prompt := input:
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 3.6. Pass query to chat engine and display response
# If last message is not from assistant, generate a new response
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         with st.spinner("Je refléchis..."):
#             response = chat_engine.stream_chat(prompt)
#             for token in response.response_gen:
#                 #print(token, end="")
#                 st.write(token, end="")
#             message = {"role": "assistant", "content": response.response}
#             st.session_state.messages.append(message)  # Add response to message history


#
# query_engine = index.as_query_engine(streaming=True)
# response = query_engine.query("What did the author do growing up?")
# response.print_response_stream()
#


# def get_source_link(description: str, filename):
#     source = [src for src in sources if src.get("description") == description]
#     if source:
#         get_url = source[0].get("get_url")
#         if get_url:
#             return get_url(description, filename)
#         return source[0].get("url")
#     return filename


# def get_source_links(source_nodes):
#     sources = filter(
#         lambda a: True,
#         set(
#             map(
#                 lambda node: get_source_link(
#                     description=node.metadata.get("source"),
#                     filename=node.metadata.get("filename"),
#                 ),
#                 source_nodes,
#             )
#         ),
#     )
#     return "\n".join(map(lambda row: f" - {row}", sources))


if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        message = str(random.choice(waiters))
        with st.spinner(message):
            message_placeholder = st.empty()
            source_nodes = []

            #             chat_engine = index.as_chat_engine(
            #                 chat_mode=ChatMode.CONTEXT,
            #                 verbose=True,
            #                 similarity_top_k=5,
            #                 system_prompt="""
            # Tu es un expert de la documentation de la fabrique numérique des ministères sociaux et tu réponds à des questions en t'appuyant uniquement sur le contexte fourni et en ne faisant jamais appel à tes propres connaissances.
            # Si tu cherches des contacts, cherches les contacts de la fabrique numérique des ministères sociaux en priorité
            # Pour les questions techniques cherches dans la documentation SRE
            # """,
            #             )
            if prompt:
                streaming_response = st.session_state["chat_engine"].stream_chat(prompt)

                # streaming_response.print_response_stream()

                full_response = ""
                source_nodes += streaming_response.source_nodes

                for text in streaming_response.response_gen:
                    full_response += text
                    message_placeholder.markdown(full_response)

                    # print(source_nodes)
                    # str_sources = get_source_links(source_nodes)
                    # if str_sources:
                    #     full_response += "\n\nSources utilisées : \n\n" + str_sources
                message_placeholder.markdown(full_response)
                # print("str_sources", str_sources)
                #   full_response += f"\n\n{str_sources}"
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
