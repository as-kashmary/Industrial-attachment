# RAG_LLM_project
Supported python version: 3.11.0

# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download Models
python model_download.py

# 5. Initiate the server
uvicorn main:app --reload

# Descriptions about endpoints:
    /docs : to check the details of endpoints
    /admin: to get the admin page(file upload)
    /user: to get the user page(query and responsne)
    change the DB_url in database.py to access the database

# descriptions of pages:
    Webpages are in admin folder(I didn't change the folder name, as it was colliding with static folder)

# Risks:
    There might be and error while installing packages. llama_cpp_python may require nmake version of 4.0.2. It may require cmake installation of previous versions(Currently I forgot the version)