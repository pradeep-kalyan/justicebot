from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain.prompts import PromptTemplate
import gradio as gr

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.9,
    max_retries=2,
    api_key="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",
)


def load_web_content(url):
    try:
        loader = WebBaseLoader(url)
        return loader.load().pop().page_content
    except Exception as e:
        return ""


def scrape():
    outputs = []
    websites = [
        "https://doj.gov.in/",
        "https://njdg.ecourts.gov.in/njdg_v3/",
        "https://doj.gov.in/supreme-court-3/",
    ]
    for webpage in websites:
        output = load_web_content(webpage)
        outputs.append(output)
    return outputs


def create_prompt_template(output, output1, output2, user_in):
    return PromptTemplate.from_template(
        f"""
        ###scraped text from websites:
        {output},{output1},{output2},{user_in}
        ###
        Instruction:
        analyze the users input to understand their needs and context.
        generate responses based on the information retrieved, ensuring they are accurate, relevant, and easy to understand.
        you are a bot working for DOJ website
        answer the data is from the Department of Justice websites. Your task is to extract answers based on the provided data and answer to questions asked by {{user_in}}. Ensure the answers are concise and clear and easy to understand. If the answers are not specified in the given data, provide your own information. Only plain text.(NO PREAMBLE)
        """
    )


def hello(user_in):
    output = scrape()
    prompt = create_prompt_template(output[0], output[1], output[2], user_in)
    prompt_in = prompt | llm
    data = prompt_in.invoke(
        input={
            "output": output[0],
            "output1": output[1],
            "output2": output[2],
            "user_in": user_in,
        }
    )
    response = data.content
    return response


app = gr.Interface(
    fn=hello,
    inputs=[
        gr.Textbox(
            label="Query",
            placeholder="Enter your question related to Department of justice website",
        )
    ],
    outputs=[gr.Textbox(label="Response", placeholder="Here is your Response")],
)
app.launch()
