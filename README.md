# 🤖 Website Chatbot with Groq AI

An intelligent chatbot that can answer questions about any website using AI. Simply provide a URL
and the chatbot will scrape the content and answer your questions using Groq's powerful Llama 3.3 70B model.


## ✨ Features

- 🌐 **Web Scraping**: Automatically extracts content from any website
- 🤖 **AI-Powered**: Uses Groq's Llama 3.3 70B model for intelligent responses
- 💬 **Interactive Chat**: Beautiful chat interface with conversation history
- ⚡ **Fast Responses**: Lightning-fast AI inference with Groq
- 🎨 **Modern UI**: Clean and intuitive Streamlit interface
- 🔒 **Secure**: API key validation and error handling
- 📱 **Responsive**: Works on desktop and mobile browsers

## 🚀 Demo

### How It Works:
1. Enter your Groq API key
2. Provide any website URL
3. Ask questions about the website
4. Get instant AI-powered answers!

### Example Questions:
- "What is this website about?"
- "What services are offered?"
- "What are the pricing options?"
- "How can I contact them?"

## 🛠️ Technologies Used

- **Python 3.8+**
- **Streamlit** - Web application framework
- **Groq API** - AI model inference (Llama 3.3 70B)
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP library
- **lxml** - HTML/XML parser

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Free Groq API key ([Get it here](https://console.groq.com/keys))

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/website-chatbot.git
cd website-chatbot
```

### Step 2: Install Dependencies
```bash
pip install streamlit groq beautifulsoup4 requests lxml
```

### Step 3: Run the Application
```bash
streamlit run complete_app.py
