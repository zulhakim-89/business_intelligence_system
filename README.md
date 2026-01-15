#  AI-Powered Catering Operations Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenAI](https://img.shields.io/badge/AI-GPT--4o--mini-green)

### 🚀 Project Overview
**ZuljaOS** is a comprehensive Business Intelligence & Operations System designed for **Zulja Catering**, a Malaysian SME. It leverages **Generative AI** and **Machine Learning** to transform fragmented legacy workflows (WhatsApp/Paper) into a centralized, data-driven ecosystem.

**Key Problem Solved:** The client struggled with manual order entry, unpredictable staffing needs, and lack of revenue visibility. ZuljaOS automates these processes to increase operational efficiency by ~40%.

---

### 🌟 Key Features

#### 1. 🤖 AI CRM (WhatsApp Parser)
* **Technology:** OpenAI (GPT-4o-mini).
* **Function:** Extracts unstructured text from WhatsApp (e.g., "Nak order nasi minyak 50 pax...") and converts it into structured JSON data.
* **Benefit:** Eliminates manual data entry errors.

#### 2. 🔮 Hybrid Forecasting Engine
* **Technology:** Scikit-Learn (Linear Regression) + GPT-4o-mini.
* **Function:** Predicts **Revenue** and **Staffing Requirements** for future months based on historical data.
* **Strategic AI:** An LLM analyzes the numerical forecast to generate a text-based **"Executive Risk Report"**, warning managers about capacity limits or low-demand periods.

#### 3. 📊 Interactive Business Intelligence
* **Technology:** Altair & Pandas.
* **Function:** Real-time dashboards tracking Top VIP Clients, Dish Popularity, and Delivery Heatmaps.
* **UI:** Modern dark-mode interface with interactive charts.

#### 4. 🔐 Secure & Modular Architecture
* **Security:** Password-protected login gateway to prevent unauthorized API usage.
* **Structure:** Clean, modular codebase using a `tabs/` directory structure for scalability.

---

### 🛠️ Tech Stack
* **Frontend:** Streamlit
* **AI/LLM:** OpenAI API
* **Machine Learning:** Scikit-Learn
* **Data Manipulation:** Pandas, NumPy
* **Deployment:** Streamlit Community Cloud

---

### 💻 Installation & Setup

**1. Clone the Repository**
```bash
git clone [https://github.com/zulhakim-89/business_intelligence_system.git](https://github.com/zulhakim-89/business_intelligence_system.git)
cd business_intelligence_system