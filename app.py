import streamlit as st
from dotenv import load_dotenv
import pickle
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os
 
# Sidebar contents

# Add the Google Ads script to your Streamlit app
# st.markdown("""
# <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6171822268442011"
#      crossorigin="anonymous"></script>
# """, unsafe_allow_html=True)

# # Create an ad unit
# st.markdown("""
# <ins class="adsbygoogle"
#      style="display:block"
#      data-ad-client="ca-pub-YOUR_PUBLISHER_ID"
#      data-ad-slot="YOUR_AD_SLOT_ID"
#      data-ad-format="auto"
#      data-full-width-responsive="true"></ins>
# <script>
#      (adsbygoogle = window.adsbygoogle || []).push({});
# </script>
# """, unsafe_allow_html=True)
with st.sidebar:
    st.title('Chatpdf')
    st.markdown('''
    ## About
    This app is an LLM-powered Chat PDF app
    ''')
    add_vertical_space(5)
    st.write('Made by [Shivaji Raut](https://www.linkedin.com/in/shivaji-raut-1b667822b/)')
 
load_dotenv()
 
def main():
    st.header("Chat with PDF")
 
 
    # upload a PDF file
    pdf = st.file_uploader("Upload your PDF", type='pdf')
 
    # st.write(pdf)
    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
 
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
        chunks = text_splitter.split_text(text=text)
 
        # # embeddings
        store_name = pdf.name[:-4]
        st.write(f'{store_name}')  
        # st.write(chunks)
 
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl", "rb") as f:
                VectorStore = pickle.load(f)
            # st.write('Embeddings Loaded from the Disk')s
        else:
            embeddings=OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f"{store_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)
 
        # embeddings = OpenAIEmbeddings()
        # VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
 
        # Accept user questions/query
        query = st.text_input("Ask questions about your PDF file:")
        # st.write(query)
 
        if query:
            docs = VectorStore.similarity_search(query=query, k=3)
 
            llm = OpenAI(model_name="gpt-3.5-turbo")
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query)
                print(cb)
            st.write(response)
 
if __name__ == '__main__':
    main()
