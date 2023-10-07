import frontmatter
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index.readers.base import BaseReader
from llama_index.prompts import PromptTemplate

from llama_index.node_parser.file.markdown import MarkdownNodeParser
from MarkdownReader import MarkdownReader, dictStringValues
from llama_index.node_parser import SentenceWindowNodeParser
import re
import chromadb
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import HuggingFaceLLM

from llama_index.node_parser.extractors import (
    MetadataExtractor,
    TitleExtractor,
    QuestionsAnsweredExtractor,
)


def get_file_metadata(filename):
    post = frontmatter.load(filename)
    # print(post)
    # if not post.metadata:
    #   post.metadata["title"] = "xxx"
    return {"filename": filename, **post.metadata}


SreFilesMapping = {
    "content/support-sre/init/.*": {
        "topics": [
            "Présentation générale de la plateforme et des services technique de la fabrique"
        ],
    },
    "content/support-sre/infrastructure/.*": {
        "topics": ["Questions sur l'infrastructure technique de la fabrique"],
    },
    "content/support-sre/standards/.*": {
        "topics": [
            "Questions sur les standards techniques et conventions de la fabrique"
        ],
    },
    "content/support-sre/workshops/.*": {
        "topics": ["Workshops proposés aux développeurs(ses) de la fabrique"],
    },
}


def get_sre_metadata(filename):
    # print(filename)
    metadata = get_file_metadata(filename)
    for path in SreFilesMapping.keys():
        if bool(re.match(path, filename)):
            return {
                **dictStringValues(SreFilesMapping[path]),
                **metadata,
            }
    return metadata


def get_se_metadata(filename):
    metadata = get_file_metadata(filename)
    return {
        "title": metadata.get("title"),
        "description": metadata.get("mission"),
        "incubateur": metadata.get("incubator"),
        # "sponsors": metadata.get("sponsors"),
    }


def get_documents(source):
    reader = SimpleDirectoryReader(
        input_dir=source.get("path"),
        required_exts=[".md"],
        recursive=True,
        file_extractor={".md": MarkdownReader},
        file_metadata=source.get("file_metadata"),
    )
    # use MarkdownReader and split top-level paragraphs into documents
    docs = reader.load_data()
    # for doc in docs:
    #     doc.metadata = source.get("file_metadata")(doc.filename)
    return docs


sources = [
    # {
    #     "id": "startups-beta-gouv-sample",
    #     "topics": [
    #         "Questions concernant les startups beta.gouv",
    #         "Questions concernant les startups de la fabrique numérique",
    #     ],
    #     "path": "./content/sample",
    #     "file_metadata": get_se_metadata,
    # },
    {
        "id": "startups-beta-gouv",
        "topics": [
            "Questions concernant les startups beta.gouv",
            "Questions concernant les startups de la fabrique numérique",
        ],
        "path": "./content/startups",
        "file_metadata": get_se_metadata,
        "examples": [
            "Aide dans mon parcours administratif",
            "Reconnaissance d'image",
            "Formation continue",
            "c'est quoi MonAideCyber ?",
            "cybersécurité",
            "startups dans l'écologie",
        ],
    },
    {
        "id": "support-techique-sre-socialgouv",
        "topics": [
            "Questions techniques sur le fonctionnent de l'hebergement",
            "Questions sur kubernetes et la plateforme de la fabrique",
        ],
        "path": "./content/support-sre",
        "file_metadata": get_sre_metadata,
        "examples": [
            "Me connecter à ma base de données",
            "Configurer mes ressources",
            "Demander de l'aide",
        ],
    },
]


# metadata_extractor = MetadataExtractor(
#     extractors=[
#         # TitleExtractor(nodes=5),
#         # QuestionsAnsweredExtractor(questions=3),
#     ],
# )

# text_splitter = SentenceWindowNodeParser(
#     window_size=3,
# )


# node_parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)

node_parser = MarkdownNodeParser.from_defaults()

# node_parser = SentenceWindowNodeParser.from_defaults(
#     # text_splitter=text_splitter,
#     window_size=0,
#     metadata_extractor=metadata_extractor,
# )
# assume documents are defined -> extract nodes


chroma_client = chromadb.PersistentClient(path="./chroma_db")
# chroma_client = chromadb.EphemeralClient()


# define embedding function
# embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# llm = OpenAI(model="text-davinci-003", temperature=0, max_tokens=256)

# system_prompt = """<|SYSTEM|># StableLM Tuned (Alpha version)
# - StableLM is a helpful and harmless open-source AI language model developed by StabilityAI.
# - StableLM is excited to be able to help the user, but will refuse to do anything that could be considered harmful to the user.
# - StableLM is more than just an information source, StableLM is also able to write poetry, short stories, and make jokes.
# - StableLM will refuse to participate in anything that could harm a human.
# """


# query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")


# llm = HuggingFaceLLM(
#     context_window=2048,
#     max_new_tokens=256,
#     generate_kwargs={"temperature": 0.25, "do_sample": False},
#     # system_prompt=system_prompt,
#     query_wrapper_prompt=query_wrapper_prompt,
#     # tokenizer_name="StabilityAI/stablelm-tuned-alpha-3b",
#     # model_name="StabilityAI/stablelm-tuned-alpha-3b",
#     tokenizer_name="Writer/camel-5b-hf",
#     model_name="Writer/camel-5b-hf",
#     device_map="auto",
#     # stopping_ids=[50278, 50279, 50277, 1, 0],
#     # tokenizer_kwargs={"max_length": 2048},
#     # uncomment this if using CUDA to reduce memory usage
#     # model_kwargs={"torch_dtype": torch.float16}
# )

service_context = ServiceContext.from_defaults(
    # chunk_size=512,
    # embed_model=embed_model,
    node_parser=node_parser,
    # llm=llm,
)


for source in sources:
    docs = get_documents(source)
    try:
        chroma_collection = chroma_client.get_collection(source.get("id"))
        print("==> Collection {} already exist\n\n".format(source.get("id")))
    except ValueError:
        chroma_collection = chroma_client.create_collection(source.get("id"))
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        # for doc in docs:
        #    print(doc.metadata)
        nodes = node_parser.get_nodes_from_documents(docs)
        # for node in nodes:
        # print(node.metadata)
        #     nodes = node_parser.get_nodes_from_documents([doc], show_progress=True)
        #     print(doc.metadata.get("filename"), len(nodes))
        # for node in nodes:
        #     print(node.metadata)
        #     print(node.relationships)
        # print(doc.metadata)
        # print(dir(doc))
        # print(doc.json())
        # print(len(nodes))
        # for node in nodes:
        # print("\n")
        # print(node)
        # print(node.metadata)
        print(
            "index {} documents and {} nodes in {}".format(
                len(docs), len(nodes), source.get("id")
            )
        )
        index = VectorStoreIndex.from_documents(
            docs, storage_context=storage_context, service_context=service_context
        )
        print(f"==> Loaded {len(docs)} docs\n\n")
    finally:
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store)

    query_engine = index.as_query_engine()
    for query in source.get("examples"):
        response = query_engine.query(query)
        print("\n", source.get("id"), ":", query)
        print(str(response))
