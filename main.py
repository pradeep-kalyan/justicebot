from langchain_groq import ChatGroq
import os
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.9,
    max_retries=2,
    api_key="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"
)
print(data.content)
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://doj.gov.in/")
output=loader.load().pop().page_content
loader1 = WebBaseLoader("https://njdg.ecourts.gov.in/scnjdg/")
output1=loader1.load().pop().page_content
loader2 = WebBaseLoader("https://doj.gov.in/supreme-court-3/")
output2=loader2.load().pop().page_content
loader3 = WebBaseLoader("https://dashboard.doj.gov.in/vacancy-position/")
output3=loader3.load().pop().page_content
from langchain_core.prompts import PromptTemplate
prompt = PromptTemplate.from_template(
    """
    ###scraped text from websites:
    {output},{output1},{output2}
    ###
    Instruction:
    analyze the users input to understand their needs and context.
    generate responses based on the information retrieved, ensuring they are accurate, relevant, and easy to understand.
    you are a bot working for DOJ website
    answer the data is from the Department of Justice websites. Your task is to extract answers based on the provided data and answer to questions asked by {user_in}. Ensure the answers are clear and easy to understand. If the answers are not specified in the given data, provide your own information. Only plain text.(NO PREAMBLE)
    """
)

prompt_in = prompt | llm
user_in=input("enter your Query : ")
data = prompt_in.invoke(input={'output':output,'output1':output1,'output2':output2,'output3':output3,'user_in':user_in})
print(data.content)