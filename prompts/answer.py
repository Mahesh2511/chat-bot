def build_answer_prompt(summary: str, history: str, docs: str, question: str, lang: str) -> str:
    context_block = docs.strip()
    return f"""You are a helpful assistant for our company.

Conversation Summary:
{summary}

Recent Chat:
{history}

Relevant Context:
{context_block if context_block else "(no relevant documents found)"}

User Question:
{question}

Rules:
- If Relevant Context is "(no relevant documents found)", reply ONLY with:
  "I don't have information about that in our knowledge base. Please contact support."
  Do NOT use your general knowledge to fill the gap.
- Otherwise, answer ONLY from the Relevant Context. Do not add outside knowledge.
- Be concise (2-3 sentences max).
- Do not repeat history.
- YOU MUST respond in {lang} only. No exceptions.
  (Pure English question → English. Any Arabic characters present, even mixed → Arabic.)
"""
