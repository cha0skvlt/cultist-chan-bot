# 🤖 AGENTS.md
```yaml
Agent Name: `GiftDemon`

> Autonomous crypto-earning Telegram agent powered by TinyLlama LLM.  
> Operates as a digital persona that hunts airdrops, evaluates NFTs, interacts with users, and evolves through prompts.

---

🎯 GOAL


goal: >
  Create a fully autonomous agent that:
  - hunts and joins token airdrops
  - analyzes and purchases valuable NFTs
  - communicates in Telegram as a living character
  - logs all actions to local database
  - evolves decision-making through embedded LLM (TinyLlama)
  - operates continuously with no human input
🧠 AGENT ROLES
Role	Description
scanner	Fetches NFT data and sends it to LLM for value assessment
hunter	Scans airdrop announcements, filters via LLM, joins automatically
persona	Formats Telegram messages with character-driven speech
scheduler	Triggers scans, hunts, reports on intervals
llm	Handles prompt calls to TinyLlama, provides natural-language output

📦 AGENT MODULES
bash
Копировать
Редактировать
giftdemon/
├── llm.py                # Query wrapper for TinyLlama (local/remote)
├── persona.py            # Stylized LLM prompt formatting
├── airdrop_hunter.py     # Drop fetch and decision logic
├── scanner.py            # NFT discovery and valuation
├── telegram_bot.py       # Telegram integration
├── db.py                 # Local event storage
├── prompts/              # Reusable prompt templates
💬 LLM USAGE
Every external decision goes through LLM:

"Is this a good NFT?"

"Should I join this drop?"

"What should I say to the user now?"

Telegram replies are fully LLM-generated with persona templates.

✅ SUCCESS CRITERIA
query_llm() used in every decision path

Telegram messages formatted by persona.py

No hardcoded replies or NFT filters

Logs show LLM prompt + decision per action

Agent operates 24/7 with no manual input

🔄 Evolving
This agent is meant to evolve.
It learns indirectly via improved prompts, modules, and persona logic — not via training.
