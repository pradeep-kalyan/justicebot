import os
from flask import Flask, render_template, request
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate

app = Flask(__name__)
os.environ["GROQ_API_KEY"] = "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"

# Load API key from environment variable
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")


# Load content from DOJ website and cache it
def load_web_content(url):
    try:
        loader = WebBaseLoader(url)
        return loader.load().pop().page_content
    except Exception as e:
        app.logger.error(f"Error loading content from {url}: {e}")
        return ""


# Create a prompt template for the Groq model
def create_prompt_template(output, output1, output2,output3,output4,output5):
    return PromptTemplate.from_template(
        f"""
        ###scraped text from websites:
        {output},{output1},{output2},{output3},{output4},{output5}
        ###
        Instruction:
        analyze the users input to understand their needs and context.
        generate responses based on the information retrieved, ensuring they are accurate, relevant, and easy to understand.
        you are a bot working for DOJ website
        answer the data is from the Department of Justice websites. Your task is to extract answers based on the provided data and answer to questions asked by {{user_in}}. Ensure the answers are concise and clear and easy to understand. If the answers are not specified in the given data, provide your own information. Only plain text.(NO PREAMBLE)
        """
    )


# Define the Flask route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_in = request.form["query"]
        outputs = []
        for url in [
            "https://doj.gov.in/",
            "https://njdg.ecourts.gov.in/njdg_v3/",
            "https://doj.gov.in/supreme-court-3/",
            "https://dashboard.doj.gov.in/vacancy-position/",
            "https://njdg.ecourts.gov.in/hcnjdg_v2/",
            "https://njdg.ecourts.gov.in/scnjdg/",


        ]:
            output = load_web_content(url)
            outputs.append(output)

        prompt = create_prompt_template(*outputs[:7])
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0.9,
            max_retries=2,
            api_key=api_key,
        )
        prompt_in = prompt | llm
        try:
            data = prompt_in.invoke(
                input={
                    "output": outputs[0],
                    "output1": outputs[1],
                    "output2": outputs[2],
                    "output3": outputs[3],
                    "output4": outputs[4],
                    "output5": outputs[5],
                    "user_in": user_in,
                }
            )
            response = data.content
        except Exception as e:
            app.logger.error(f"Error invoking Groq model: {e}")
            response = "Error generating response. Please try again."

        return render_template("index.html", response=response, user_in=user_in)
    else:
        app.logger.debug("hello this is running")
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
