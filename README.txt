CUSTOMER PURCHASE PATTERN ANALYSIS - STREAMLIT

RUN LOCALLY ON WINDOWS CMD (requires Python):
1. Open CMD in the extracted folder.
2. Run: py -m pip install -r requirements.txt
3. Run: py -m streamlit run app.py
4. Open the Local URL printed in CMD, usually http://localhost:8501

DEPLOY ONLINE (no local Python installation):
1. Upload app.py and requirements.txt to a GitHub repository.
2. Sign in at https://share.streamlit.io/
3. Create app; choose repository, branch main, main file app.py.
4. Click Deploy.

CSV columns required:
Customer_ID,Customer_Name,Product,Quantity,Price
