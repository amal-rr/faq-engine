# **Product Proposal – “FAQ Engine”**
Automated extraction of prospect questions → consolidated dynamic FAQ → insights for Sales, Enablement, and Product.

---

## **1. Problem Summary**

Sales teams record hundreds of calls every month using tools like **Gong**, **Zoom**, and **HubSpot**. Inside these calls lie the real questions prospects care about — buying triggers, workflow blockers, integration needs, risk concerns, and misconceptions about product capabilities.

### **Current State**
- Reps individually interpret questions and objections.  
- Enablement updates FAQs and objection guides manually after listening to long calls.  
- Product teams rely on anecdotal feedback instead of call data.  
- Marketing lacks real buyer language for messaging.  
- There is no unified, searchable place for reps to find the most common prospect questions and best responses.  

**Result:** A large gap remains between raw conversations and actionable insights.

---

## **2. Solution Overview**

Build a lightweight **AI engine** that automates the process end-to-end.

### **Step 1 — Pull Call Transcripts from Gong**
- Use **Gong’s API** to ingest calls.  
- Filter by **team, timeframe, persona, or pipeline stage**.  
- Detect **prospect vs. rep** speaker turns.  
- Identify question phrasing automatically.

### **Step 2 — Extract Prospect Questions**
Use NLP to identify question patterns:
- “Can it…?”
- “Do you support…?”
- “How does … work?”
- “What’s the cost?”
- “Does it integrate with…?”

Categorize into key domains: **onboarding**, **dispatch**, **billing**, **LTL**, **integrations**, **pricing**, **security**, etc.

### **Step 3 — Cluster Similar Questions**
