# AI Content Crawling Project

## Overview
This project enhances traditional web scraping by integrating AI to handle dynamic web architectures, bypass CAPTCHAs, and process unstructured data. Focused on e-commerce data from [www.tukku.net](https://www.tukku.net), it uses Ollama AI to analyze product descriptions and generate additional attributes, creating a robust relational database for AI-powered product recommendations.

## Key Features
- **AI-Powered Data Extraction**: Uses Ollama 3.2 to translate and generate 400+ product attributes from Finnish descriptions.
- **Scalable Crawling**: Optimized with asynchronous programming to handle large datasets efficiently.
- **High-Performance Processing**: Deployed on CSC's Mahti GPU platform for fast AI model execution.
- **Structured Database**: MySQL database with relational tables for efficient data management.
- **Ethical Compliance**: Adheres to website guidelines and minimizes server strain during crawling.

## Technologies Used
- **Web Crawling**: BeautifulSoup, Python Requests library
- **AI Model**: Ollama 3.2 (hosted on CSC Mahti)
- **Database**: MySQL Workbench, phpMyAdmin
- **Data Processing**: Python (Pandas, Regex)
- **Project Management**: Jira, Confluence
- **Infrastructure**: CSC Mahti (GPU-accelerated computing)

## Workflow
Data Crawling: Extract product data using BeautifulSoup

AI Processing: Generate additional attributes with Ollama

Data Cleaning: Standardize formats and remove duplicates

Database Integration: Store in MySQL relational tables

Model Training: Prepare data for recommendation system

## Database Schema

Primary Table: Core product information

Secondary Tables: 400+ generated attributes linked by product ID
