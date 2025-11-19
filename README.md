Bank of Maharashtra Loans RAG Chatbot

A complete end-to-end Retrieval-Augmented Generation (RAG) system built using scraped content from the Bank of Maharashtra – Loans section.
This project demonstrates real-world web scraping, vector search, semantic chunking, and LLM-powered chatbot development.

Project Overview

The goal of this project is to build a chatbot that can accurately answer queries related to different loan products of the Bank of Maharashtra (Home Loan, Car Loan, Personal Loan, etc.) using real data scraped from the website.

The project pipeline includes:

Web Crawling – Extracting all loan-related URLs

Web Scraping – Fetching page content from Selenium

Data Cleaning & Merging – Saving each page as .txt and combining them

Semantic Chunking – Splitting text based on meaning

Embedding & Vector DB – Storing chunks in a FAISS index

RAG Pipeline – Retrieving relevant text during Q&A

Chat Interface – Gemini model + custom conversation memory
Features

Crawls and scrapes dynamic pages using Selenium
Extracts all loan-related sections from the Bank of Maharashtra
Saves each page’s text separately for transparency
Uses Semantic Chunker for intelligent text segmentation
Creates a FAISS IndexFlatL2 vector store
Implements an efficient and scalable RAG pipeline
Integrates Google Gemini as the LLM
Custom lightweight chat memory using Python lists
Clean and modular code for maintainability


Web Scraping Approach

The website did not provide a sitemap and contained dynamic content.
So the scraping workflow included:

Selenium in headless mode

Auto-scrolling to load dynamic components

Extracting text using XPath filters

Filtering loan-related internal links

Saving each page’s content into separate .txt files

A merged all.txt file is then used for vector indexing.

Semantic Chunking

Instead of fixed-size chunks, this project uses SemanticChunker, which groups sentences based on similarity and meaning.

This results in:

Better retrieval accuracy

Less redundancy

More context-aligned chunks

Vector Database (FAISS)

The vector database is built using:

Embedding Model: (Gemini / Any LLM embedding model)

FAISS IndexFlatL2: ideal for small-to-medium datasets where accuracy and latency matter

Each chunk is stored with:

Its vector embedding

A UUID

Reference to the original text

RAG Workflow

User asks a question

Query is embedded

FAISS returns top-k relevant chunks

Chunks are passed to the Gemini LLM

LLM generates an answer grounded in real scraped data

This ensures factual and domain-specific responses.

Chat Interface & Memory

Instead of using LangChain’s memory modules, a simple Python list maintains chat history:

history.append({"user": user_msg, "bot": response})


Before generating each answer, the last few turns of history are included to keep the conversation coherent.

This is lightweight, fast, and easily controllable.

Installation
git clone https://github.com/pragya/maharashtra-bank-rag.git
cd maharashtra-bank-rag

pip install -r requirements.txt


For FAISS (Windows):

pip install faiss-cpu

How to Run
Scrape the website
python scraping/crawler.py
python scraping/scraper.py

Build the vector database
python vector_db/build_vector_db.py

Run the chatbot
python app/chat.py

Future Improvements

Add UI using Streamlit

Add rate-limit handling during scraping

Store conversation memory in FAISS itself

Create embeddings for metadata and tables

Deploy RAG API using FastAPI

Author

Pragya Bharti
RAG Engineer • Data Science & AI﻿# Loan-Product-Assistant



