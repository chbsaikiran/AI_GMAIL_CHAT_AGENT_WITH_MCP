import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=api_key)
genai.configure(api_key=api_key)

def build_gmail_search_query(natural_question: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    system_prompt = f"""
You are an AI expert at writing Gmail search queries.
Convert the following user question into a Gmail search query syntax.
Only output the Gmail query string. Do not explain anything.

IMPORTANT RULES:
1. For "this month" queries in May 2025, ALWAYS use exactly:
   after:2025/05/01 before:2025/05/31
2. Include the ENTIRE day in date ranges
3. Never skip any days in the range

Examples:
"Swiggy orders this month" -> "Swiggy after:2025/05/01 before:2025/05/31"
"IRCTC last week" -> "IRCTC after:2025/05/10 before:2025/05/17"
"OTP from SBI yesterday" -> "OTP SBI after:2025/05/17 before:2025/05/18"

User Query:
{natural_question}
"""
    response = model.generate_content(system_prompt)
    return response.text.strip().strip('"')

def summarize_emails_with_query(user_query: str, snippets: list[str]) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    combined_emails = "\n\n".join(snippets[:50])  # Increased to match max_results
    final_prompt = f"""
You are an assistant who analyzes Gmail content and answers user queries accurately.
Your task is to:
1. Understand the specific question being asked
2. Analyze the email snippets to find relevant information
3. Provide a clear, concise answer that directly addresses the user's query
4. When analyzing expenses or orders:
   - Include ALL transactions from the entire date range
   - List each transaction with its date, restaurant, item ordered and amount
   - Don't Calculate the total amount leave it as Total Amount Spent is : TO BE ADDED LATER, I will later replace the "TO BE ADDED LATER" with correct total amount later.
5. If the query is about travel or other topics:
   - Focus on the specific information requested
   - Provide relevant details from the emails like date, location and amount spent for the travel.
   - Maintain chronological order when relevant
   - Don't Calculate the Total amount leave it as "Total Amount Spent is : TO BE ADDED LATER", I will later replace the "TO BE ADDED LATER" with correct total amount.

EMAIL SNIPPETS:
{combined_emails}

USER QUESTION:
{user_query}

TASK: 
1. Answer the question based on the email snippets, focusing specifically on what was asked.
2. When analyzing expenses or orders: Answer the question based on ALL emails in the snippets. For expenses/orders:
  - List each transaction with its date
  - Show the total amount
  - Include all orders in the date range
"""
    response = model.generate_content(final_prompt)
    return response.text

def get_total_expenses_from_emails_with_query(summarized_answer: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    final_prompt = f"""
You are an assistant who analyzes summarized answer to a gmail query, and sees if there are expenses in the summarized answer if the answer is yes then:
From ALL these transactions, just give all expenses separated by | and with prefix FUNCTION_CALL: add_list . Don't give any other output, only the expenses separated by | and with prefix FUNCTION_CALL: add_list .
if the summary has amounts like this below(the actual data may look different) but your task is to separate out the amounts for each transaction.
    Eg: Zomato order of amount on 29th March 2025 is Rs 250.50
    Zomato order of amount on 7th April 2025 is Rs 260.50
    Zomato order of amount on 9th May 2025 is Rs 1500.60
    Then you should give result as "FUNCTION_CALL: add_list|250.50|260.50|1500.60" without quotes and nothing else needs to be output
    if they are no expenses in the summary then just output "FUNCTION_CALL: add_list|0" without quotes and nothing else needs to be output

Summarized answer to gmail query:
{summarized_answer}
"""
    response = model.generate_content(final_prompt)
    return response.text

def Replace_total_expenses_from_emails_with_query(summarized_answer: str, Total_Expenses: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    final_prompt = f"""
You are an assistant who analyzes summarized answer to a gmail query, and your job is to fill in the text "Total Amount Spent is : TO BE ADDED LATER" in the place of TO BE ADDED LATER put {Total_Expenses}, remaining all text remains the same, don't change anything else.
Eg: if the input looks like this(actual may differ) but your tsk is to only replace TO BE ADDED LATER with {Total_Expenses}
    Zomato order amount on 29th March 2025 is Rs 250.50
    Zomato order amount on 7th April 2025 is Rs 260.50
    Zomato order amount on 9th May 2025 is Rs 1500.60
    Total Amount Spent is : TO BE ADDED LATER

   You need to output:
    Zomato order amount on 29th March 2025 is Rs 250.50
    Zomato order amount on 7th April 2025 is Rs 260.50
    Zomato order amount on 9th May 2025 is Rs 1500.60
    Total Amount Spent is : {Total_Expenses}

Summarized answer to gmail query:
{summarized_answer}
"""
    response = model.generate_content(final_prompt)
    return response.text
