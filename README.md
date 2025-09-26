📊 PeterAgents — NGX Stock Picker

An AI-powered multi-agent system that finds trending companies on the Nigerian Exchange (NGX), researches them, and picks the best investment candidate.
Built with CrewAI
, Serper API, and custom tools.

🚀 Features

🔎 Find Trending NGX Companies in a given sector

📑 Research Reports on company performance, market position, and outlook

📈 Stock Picker Agent chooses the best company and explains why

💾 Decision Logs saved locally for reference

📡 Push Notifications for instant results

⚙️ Installation
1. Clone the Repo
   git clone https://github.com/Peter-ConX/PeterAgents.git
   cd PeterAgents
2. Setup Virtual Environment
   uv venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows PowerShell
3. Install Dependencies
   pip install -r requirements.txt
 🔑 Environment Variables

You need a Serper API key:
 # macOS/Linux
 export SERPER_API_KEY=your_key_here

 # Windows PowerShell
$env:SERPER_API_KEY="your_key_here"

▶️ Usage

Run the crew with a sector of your choice (Technology, Banking, Oil & Gas, Consumer Goods, etc.):
 python src/stock_picker/main.py

Output:

Console: final decision

output/decision.log: saved decision report


📂 Project Structure
PeterAgents/
│── src/stock_picker/
│   ├── crew.py              # Crew + Agents + Tasks
│   ├── main.py              # Entry point
│   ├── tools/               # Custom tools (PushNotificationTool)
│── config/
│   ├── agents.yaml          # Agent roles, goals, backstories
│   ├── tasks.yaml           # Task descriptions, expected outputs
│── output/                  # Saved reports & logs


🛠 Common Errors & Fixes
1. NameError: name 'CrewBase' is not defined

CrewAI >=0.186.0 removed CrewBase.

Fix: Remove @CrewBase, just use class StockPicker:.

2. Failed Search the internet with Serper

Usually caused by invalid API key or queries too strict.

Fix:

Ensure $SERPER_API_KEY is set.

Loosen task prompt:
Find trending companies in the {sector} sector on the NGX OR covered in Nigerian financial news.

3. exchange placeholder not working

We removed {exchange} and hardcoded NGX in agents.yaml and tasks.yaml.

Fix: Remove "exchange": "NGX" from main.py inputs. Only pass "sector".

4. EntityMemory or ShortTermMemory errors

OpenAI embeddings (text-embedding-3-small) not wanted.

Fix: In crew.py set:
short_term_memory=None
entity_memory=None


5. Missing output/ folder

Fix: Already handled in main.py:
os.makedirs("output", exist_ok=True)

6. Wrong companies (e.g. Apple/Tesla)

Caused by Serper pulling foreign stocks.

Fix:

Hardcode NGX in prompts.

Validate results against a local ngx_tickers.json.

{
  "chosen_company": {
    "name": "MTN Nigeria",
    "rationale": "MTN Nigeria is the largest telecommunications operator in Nigeria..."
  },
  "not_selected_companies": [
    { "name": "Jumia", "reason": "Volatility and competition" },
    { "name": "Globacom", "reason": "Smaller scale vs MTN" }
  ]
}

🌍 Roadmap

 Add NGX ticker validation step

 Add fallback to Nigerian news sites (BusinessDay, Nairametrics, NGXGroup)

 Support for multiple exchanges (future expansion)

 Better visualization of research reports

🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

📜 License

MIT
