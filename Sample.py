import os
from vanna.base import VannaBase
from vanna.chromadb import ChromaDB_VectorStore
from google import genai
from google.genai import types

# --- Configuration ---
# Get this from https://aistudio.google.com/
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
GEMINI_MODEL = "gemini-1.5-flash"

# --- Custom Class Definition ---
# This connects the NEW Google SDK to the STABLE Vanna library
class MyVanna(ChromaDB_VectorStore, VannaBase):
    def __init__(self, config=None):
        # 1. Initialize Vector Store (ChromaDB)
        ChromaDB_VectorStore.__init__(self, config=config)
        # 2. Initialize Base Class
        VannaBase.__init__(self, config=config)
        
        # 3. Initialize the New Google Client
        self.client = genai.Client(api_key=config['api_key'])
        self.model_name = config['model']

    # -- Required Vanna Methods --
    def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "model", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        # Convert Vanna's internal message format to the new Google GenAI format
        system_instruction = None
        last_user_message = ""

        # Extract system prompt and the actual question
        for msg in prompt:
            if msg['role'] == 'system':
                system_instruction = msg['content']
            elif msg['role'] == 'user':
                last_user_message = msg['content']

        # Call the New Google GenAI SDK
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=last_user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0, # Keep it 0 for precise SQL
                )
            )
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {e}"

# --- Main Logic ---
# 1. Initialize
# Note: We pass the API key here, but our custom class handles it manually above.
vn = MyVanna(config={'api_key': GEMINI_API_KEY, 'model': GEMINI_MODEL})

# 2. Connect to SQL Server
vn.connect_to_mssql(
    odbc_conn_str=(
        "DRIVER={ODBC Driver 17 for SQL Server};" # Check if you have Driver 18 installed if this fails
        "SERVER=YOUR_SERVER_NAME;"  # e.g., localhost
        "DATABASE=YOUR_DB_NAME;"
        "Trusted_Connection=yes;"   # Use Windows Authentication
    )
)

# 3. Test it
question = "What are the top 5 tables?"
print(f"Asking: {question}...")

# Optional: Train on schema if this is the first time
# df_info = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
# plan = vn.get_training_plan_generic(df_info)
# vn.train(plan=plan)

response = vn.ask(question)