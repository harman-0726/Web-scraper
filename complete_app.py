"""
COMPLETE WEBSITE CHATBOT - ALL IN ONE FILE
===========================================

This file contains EVERYTHING:
- Web scraping with BeautifulSoup
- Groq AI integration
- Streamlit frontend

Created for Relinns Technologies Assessment

HOW TO RUN:
1. Install requirements:
   pip install streamlit groq beautifulsoup4 requests lxml

2. Run the app:
   streamlit run complete_app.py

3. Get FREE Groq API key:
   https://console.groq.com/keys

4. Enter API key, scrape website, ask questions!
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup, Tag
from groq import Groq


# ==================== BACKEND FUNCTIONS ====================

def test_groq_api(api_key):
    """
    Test if Groq API key is valid
    
    Args:
        api_key: Groq API key to test
        
    Returns:
        dict: {'success': bool, 'message': str}
    """
    if not api_key or len(api_key.strip()) == 0:
        return {
            'success': False,
            'message': "API key cannot be empty"
        }
    
    try:
        client = Groq(api_key=api_key.strip())
        
        # Make a simple test call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        return {
            'success': True,
            'message': "API key is valid! ✓"
        }
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "401" in error_msg:
            return {
                'success': False,
                'message': "Invalid API key. Please check and try again."
            }
        else:
            return {
                'success': False,
                'message': f"Error: {error_msg}"
            }


def scrape_website(url):
    """
    Download and extract text from a website
    
    Args:
        url: Website URL to scrape
        
    Returns:
        dict: {'success': bool, 'message': str, 'content': str}
    """
    try:
        # Add https:// if missing
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Download website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract text
        all_text = []
        
        # Get title
        if soup.title and soup.title.string:
            all_text.append(f"TITLE: {soup.title.string.strip()}")
        
        # Get meta description
        try:
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if isinstance(meta, Tag):
                    if meta.get('name') == 'description':
                        content = meta.get('content')
                        if content:
                            all_text.append(f"DESCRIPTION: {str(content).strip()}")
                            break
        except:
            pass  # Skip if meta description not found
        
        # Get headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True)
            if text and len(text) > 3:
                all_text.append(f"\n{text}")
        
        # Get paragraphs
        for paragraph in soup.find_all('p'):
            text = paragraph.get_text(strip=True)
            if text and len(text) > 30:
                all_text.append(text)
        
        # Get list items
        for item in soup.find_all('li'):
            text = item.get_text(strip=True)
            if text and len(text) > 10:
                all_text.append(f"• {text}")
        
        # Combine and clean text
        website_text = "\n\n".join(all_text)
        website_text = ' '.join(website_text.split())
        website_text = website_text.replace('. ', '.\n')
        
        # Limit size
        if len(website_text) > 15000:
            website_text = website_text[:15000] + "\n\n[Content truncated...]"
        
        # Validate content
        if not website_text or len(website_text) < 200:
            return {
                'success': False,
                'message': "Could not extract enough content. Try a different URL.",
                'content': ""
            }
        
        return {
            'success': True,
            'message': f"Successfully scraped! Extracted {len(website_text)} characters.",
            'content': website_text
        }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': "Request timeout. Website took too long to respond.",
            'content': ""
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': "Connection error. Check your internet or try a different URL.",
            'content': ""
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error: {str(e)}",
            'content': ""
        }


def ask_groq(groq_client, website_url, website_content, question, chat_history):
    """
    Ask Groq AI a question about the website
    
    Args:
        groq_client: Initialized Groq client
        website_url: URL of the website
        website_content: Scraped content
        question: User's question
        chat_history: Previous conversation
        
    Returns:
        dict: {'success': bool, 'answer': str}
    """
    if not question or len(question.strip()) == 0:
        return {
            'success': False,
            'answer': "Please enter a valid question."
        }
    
    try:
        # Build messages
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful AI assistant answering questions about websites.

WEBSITE URL: {website_url}

WEBSITE CONTENT:
{website_content}

INSTRUCTIONS:
- Answer using ONLY the website content above
- If info is not available, say "I don't see that information on this website"
- Be helpful, accurate, and concise
- Provide specific details from the website
- Format answers clearly with proper paragraphs
- Don't make up information"""
            }
        ]
        
        # Add recent chat history
        if len(chat_history) > 0:
            messages.extend(chat_history[-4:])
        
        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })
        
        # Call Groq API
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )
        
        # Get answer
        answer = response.choices[0].message.content.strip()
        
        return {
            'success': True,
            'answer': answer
        }
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower():
            error_msg = "Invalid API key. Please check your key."
        elif "rate limit" in error_msg.lower():
            error_msg = "Rate limit exceeded. Please wait and try again."
        
        return {
            'success': False,
            'answer': f"Error: {error_msg}"
        }


# ==================== STREAMLIT FRONTEND ====================

# Page configuration
st.set_page_config(
    page_title="Website Chatbot - Groq AI",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86DE;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .user-msg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .user-msg b {
        color: #FFD700;
        font-size: 1.1rem;
    }
    .bot-msg {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .bot-msg b {
        color: #FFFF00;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'groq_client' not in st.session_state:
    st.session_state.groq_client = None

if 'website_scraped' not in st.session_state:
    st.session_state.website_scraped = False

if 'website_content' not in st.session_state:
    st.session_state.website_content = ""

if 'website_url' not in st.session_state:
    st.session_state.website_url = ""

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_validated' not in st.session_state:
    st.session_state.api_validated = False

# Header
st.markdown('<div class="main-title">🤖 Website Chatbot with Groq AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask intelligent questions about any website using AI</div>', unsafe_allow_html=True)
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Setup & Configuration")
    
    # Step 1: API Key
    st.subheader("Step 1: Groq API Key")
    api_key_input = st.text_input(
        "Enter API Key",
        type="password",
        help="Get free key from https://console.groq.com/keys",
        placeholder="gsk_..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Validate", use_container_width=True):
            if api_key_input:
                with st.spinner("Validating..."):
                    result = test_groq_api(api_key_input)
                    if result['success']:
                        st.session_state.groq_client = Groq(api_key=api_key_input)
                        st.session_state.api_validated = True
                        st.success(result['message'])
                    else:
                        st.session_state.api_validated = False
                        st.error(result['message'])
            else:
                st.warning("Enter API key first")
    
    with col2:
        if st.button("ℹ️ Get Key", use_container_width=True):
            st.info("Visit:\nconsole.groq.com/keys")
    
    st.divider()
    
    # Step 2: Website URL
    st.subheader("Step 2: Website URL")
    url_input = st.text_input(
        "Enter URL",
        placeholder="https://example.com",
        value=st.session_state.website_url
    )
    
    if st.button("🌐 Scrape Website", use_container_width=True):
        if not st.session_state.api_validated:
            st.error("❌ Validate API key first!")
        elif not url_input:
            st.warning("⚠️ Enter a URL")
        else:
            with st.spinner(f"Scraping {url_input}..."):
                result = scrape_website(url_input)
                
                if result['success']:
                    st.session_state.website_scraped = True
                    st.session_state.website_content = result['content']
                    st.session_state.website_url = url_input
                    st.session_state.messages = []
                    st.session_state.chat_history = []
                    st.success(result['message'])
                else:
                    st.session_state.website_scraped = False
                    st.error(result['message'])
    
    st.divider()
    
    # Actions
    st.subheader("🔧 Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.success("Cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset All", use_container_width=True):
            st.session_state.clear()
            st.success("Reset!")
            st.rerun()
    
    st.divider()
    
    # Status
    st.subheader("📊 Current Status")
    if st.session_state.api_validated:
        st.success("✓ API Key Valid")
    else:
        st.error("✗ API Key Not Set")
    
    if st.session_state.website_scraped:
        st.success("✓ Website Scraped")
        if st.session_state.website_url:
            st.caption(f"{st.session_state.website_url[:40]}...")
    else:
        st.error("✗ No Website Scraped")
    
    st.divider()
    
    # Help
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - What is this website about?
        - What services are offered?
        - What are the pricing plans?
        - How can I contact them?
        - What are the main features?
        - Tell me about the company
        """)
    
    with st.expander("🌐 Sample URLs to Try"):
        st.code("https://botpenguin.com")
        st.code("https://streamlit.io")
        st.code("https://groq.com")
        st.code("https://anthropic.com")
        st.code("https://python.org")

# Main content area
if not st.session_state.api_validated:
    st.info("👈 **Step 1:** Enter your Groq API key in the sidebar and click 'Validate'")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("**100% Free**\n\nNo credit card needed!")
    with col2:
        st.success("**Lightning Fast**\n\nLlama 3.3 70B model")
    with col3:
        st.success("**Easy Setup**\n\nReady in 1 minute")
    
    st.divider()
    
    st.subheader("📋 How to Get Started:")
    st.markdown("""
    1. **Get FREE Groq API Key** → Visit [console.groq.com/keys](https://console.groq.com/keys)
    2. **Sign up** → Takes less than 1 minute (no credit card!)
    3. **Create API Key** → Copy the key that starts with `gsk_`
    4. **Paste it** → In the sidebar input box
    5. **Click Validate** → You're ready to go! 🚀
    """)

elif not st.session_state.website_scraped:
    st.info("👈 **Step 2:** Enter a website URL in the sidebar and click 'Scrape Website'")
    
    st.subheader("🎯 Try These Popular Websites:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🤖 AI & Tech:**")
        st.code("https://openai.com")
        st.code("https://anthropic.com")
        st.code("https://groq.com")
        
    with col2:
        st.markdown("**💼 Business & Tools:**")
        st.code("https://botpenguin.com")
        st.code("https://streamlit.io")
        st.code("https://python.org")

else:
    # Show ready status
    st.success(f"✅ **Ready to chat!** Currently analyzing: **{st.session_state.website_url}**")
    st.divider()
    
    # Display chat messages
    st.subheader("💬 Conversation")
    
    if len(st.session_state.messages) == 0:
        st.info("👋 **Start the conversation!** Ask any question about the website below.")
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-msg"><b>🙋 You:</b><br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bot-msg"><b>🤖 Bot:</b><br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
    
    st.divider()
    
    # Question input
    st.subheader("💭 Ask Your Question")
    
    question = st.text_input(
        "Type your question here",
        placeholder="What is this website about?",
        key="question_input",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        ask_btn = st.button("🚀 Ask Question", use_container_width=True, type="primary")
    
    with col2:
        if st.button("🔄 Clear Input", use_container_width=True):
            st.rerun()
    
    # Handle question submission
    if ask_btn and question:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        
        # Get AI response
        with st.spinner("🤔 AI is thinking..."):
            result = ask_groq(
                st.session_state.groq_client,
                st.session_state.website_url,
                st.session_state.website_content,
                question,
                st.session_state.chat_history
            )
            
            # Add bot response
            st.session_state.messages.append({
                "role": "assistant",
                "content": result['answer']
            })
            
            # Update chat history
            if result['success']:
                st.session_state.chat_history.append({"role": "user", "content": question})
                st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})
                
                # Keep history manageable
                if len(st.session_state.chat_history) > 8:
                    st.session_state.chat_history = st.session_state.chat_history[-8:]
        
        st.rerun()
    
    st.divider()
    
    # Quick question buttons
    st.subheader("⚡ Quick Questions (Click to Ask)")
    
    col1, col2, col3 = st.columns(3)
    
    quick_questions = [
        "What is this website about?",
        "What services are offered?",
        "What are the pricing options?",
        "How can I contact them?",
        "What are the main features?",
        "Tell me about the company"
    ]
    
    for idx, q in enumerate(quick_questions):
        col = [col1, col2, col3][idx % 3]
        with col:
            if st.button(q, key=f"quick_{idx}", use_container_width=True):
                # Add user message
                st.session_state.messages.append({
                    "role": "user",
                    "content": q
                })
                
                # Get response
                result = ask_groq(
                    st.session_state.groq_client,
                    st.session_state.website_url,
                    st.session_state.website_content,
                    q,
                    st.session_state.chat_history
                )
                
                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer']
                })
                
                # Update history
                if result['success']:
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    st.session_state.chat_history.append({"role": "assistant", "content": result['answer']})
                
                st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🤖 Powered by <b>Groq AI</b> (Llama 3.3 70B) | Built with <b>Streamlit</b> & <b>Python</b></p>
    <p>Created for <b>Relinns Technologies</b> Assessment</p>
    <p style='font-size: 0.9rem; margin-top: 0.5rem;'>
        Web Scraping: BeautifulSoup | AI Model: Llama 3.3 70B | Framework: Streamlit
    </p>
</div>
""", unsafe_allow_html=True)