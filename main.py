from langchain_groq import ChatGroq
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate

# Securely set environment variables
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
os.environ['GROQ_API_KEY'] = 'your_api_key_here'  # Replace with your actual API key

def load_web_content(url):
    """Load content from a given URL using WebBaseLoader."""
    loader = WebBaseLoader(url)
    return loader.load().pop().page_content

def create_prompt_template(output, output1, output2):
    """Create a prompt template for the LLM."""
    return PromptTemplate.from_template(
        f"""
        ###scraped text from websites:
        {output},{output1},{output2}
        ###
        Instruction:
        analyze the users input to understand their needs and context.
        generate responses based on the information retrieved, ensuring they are accurate, relevant, and easy to understand.
        you are a bot working for DOJ website
        answer the data is from the Department of Justice websites. Your task is to extract answers based on the provided data and answer to questions asked by {{user_in}}. Ensure the answers are clear and easy to understand. If the answers are not specified in the given data, provide your own information. Only plain text.(NO PREAMBLE)
        """
    )

def main():
    # Load web content
    output = load_web_content("https://doj.gov.in/")
    output1 = load_web_content("https://njdg.ecourts.gov.in/scnjdg/")
    output2 = load_web_content("https://doj.gov.in/supreme-court-3/")
    output3 = load_web_content("https://dashboard.doj.gov.in/vacancy-position/")

    # Create prompt template
    prompt = create_prompt_template(output, output1, output2)

    # Initialize LLM
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.9,
        max_retries=2,
        api_key=os.environ['GROQ_API_KEY']
    )

    # Combine prompt with LLM
    prompt_in = prompt | llm

    # Get user input and generate response
    user_in = input("Enter your query: ")
    data = prompt_in.invoke(input={'output': output, 'output1': output1, 'output2': output2, 'output3': output3, 'user_in': user_in})
    print(data.content)

if __name__ == "__main__":
    main()
