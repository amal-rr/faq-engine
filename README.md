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
Use **semantic grouping** to merge lookalike questions into a clean general FAQ.

**Example:**
- “Does this integrate with QuickBooks?”  
- “Can invoices sync to QuickBooks?”  
- “How does accounting connection work?”  
  → **Unified Question:** “How does Rose Rocket integrate with QuickBooks?”

### **Step 4 — Auto-Generate Draft Responses**
- Pull from **internal docs** (enablement rules, help center, troubleshooting guides).  
- Or let **AI draft an answer** for internal review.

### **Step 5 — Publish a Dynamic FAQ**
Export options:
- Google Doc  
- Notion database  
- In-app FAQ for reps  
- Weekly “Top Questions” dashboard  
- Optional leadership insight reports

---

## **3. Example Output**

| **Category**     | **FAQ**                                      | **Volume** | **Trend** |
|------------------|----------------------------------------------|-------------|------------|
| Integrations     | “How do you integrate with QuickBooks?”      | 42          | Up 19%     |
| Visibility       | “Can shippers see real-time truck status?”   | 28          | Flat       |
| LTL              | “Do you support LTL carrier API rating?”     | 17          | Up 33%     |

---

## **4. Business Value**

### **Sales**
- Faster onboarding and training.  
- Real-time objection handling.  
- Consistent messaging across reps.  

### **Marketing**
- True **voice of customer (VOC)** insights for campaigns.  
- Better persona segmentation.  
- More accurate landing page copy.  

### **Product**
- Quantified feature demand.  
- Better roadmap prioritization.  
- Stronger competitive intelligence.  

### **Leadership**
- Clearer market trend visibility.  
- Better GTM alignment validation.  
- Reduced anecdotal decision-making.  

---

## **5. Internal Quick-Searchable FAQ for Reps**

### **Goal**
Give **Sales**, **BDRs**, and **CSMs** a single, lightning-fast search hub to instantly find:
- Most frequently asked prospect questions  
- Best-practice answers  
- Optional talk tracks  
- Product links and demo snippets  

---

### **How It Works**

#### **1. Create an FAQ Database**
Use **Notion** or **Google Sheets** with columns for:
- **Question:** Normalized, clustered version  
- **Short Answer:** Quick 30-second response  
- **Long Answer:** Detailed talk track  
- **Related Workflows**  
- **Links:** Help Center or Support KB  
- **Tags:** Integrations, LTL, pricing, onboarding, etc.  
- **Volume Score:** Auto-updated from Gong  
- **Last Updated**  

#### **2. Connect the FAQ Search Engine**
AI automatically:
- Updates volume counts  
- Flags new questions  
- Suggests improved answers  
- Highlights outdated talk tracks  

#### **3. Provide Easy Access Points**
Accessible across multiple platforms:
- Pinned Notion page  
- **Browser extension** (Chrome/Safari)  
- **Salesforce** or **HubSpot** sidebar embed  
- **Slack slash-command**  
  - Example: `/faq QuickBooks` → instantly returns the answer  

#### **4. Optional: Inline Use During Live Calls**
Add a small **AI Assist Panel** for live meetings where reps can search in real time:
- “LTL API rating”  
- “EDI integrations”  
- “Driver app differences”  

Optional integration with **Gong’s Live Assist** for contextual, in-call suggestions.

---

## **6. Summary: What the Internal FAQ Provides**

| **Attribute** | **Benefit** |
|----------------|-------------|
| **Fast** | Reps type 1–2 keywords and instantly get the best answer. |
| **Reliable** | Answers are based on aggregated call data, not assumptions. |
| **Consistent** | Every rep uses the same talk tracks. |
| **Evolving** | Automatically updates as new questions emerge and trends shift. |
