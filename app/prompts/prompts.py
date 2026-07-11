"""
Why this file exists:
    Prompt templates are easier to understand and maintain when they live in one
    file instead of being scattered across the codebase.

Responsibility:
    - Store prompts for answering, knowledge graph extraction, and tool routing.

How it connects to the project:
    LangGraph workflow nodes import these prompts before calling Gemini.
"""

ANSWER_PROMPT = """
You are a helpful memory-augmented assistant for a beginner AI project.
Use the available information to answer the user.

Rules:
- Prefer the provided context, knowledge graph facts, memory, and tool output.
- If information is missing, say what is missing instead of inventing facts.
- Be clear, beginner-friendly, and concise.
- Never mention OpenAI.

User memory:
{memory}

Hybrid RAG context:
{context}

Knowledge graph context:
{graph_context}

Tool output:
{tool_output}

User question:
{question}

Answer:
"""

KG_EXTRACTION_PROMPT = """
Extract a small knowledge graph from the text below.
Return ONLY valid JSON in this exact format:
{{
  "entities": [{{"name": "Entity Name", "type": "Person|Organization|Place|Concept|Other"}}],
  "relationships": [{{"source": "Entity A", "relationship": "RELATIONSHIP_NAME", "target": "Entity B"}}]
}}

Keep only important entities and relationships. Use uppercase snake case for relationship names.

Text:
{text}
"""

TOOL_ROUTER_PROMPT = """
Decide if the user question needs an external tool.
Available tools:
1. tavily_search: for latest/current information, web search, news, facts not in local docs.
2. weather: for current weather of a city.
3. none: when no external tool is needed.

Return ONLY valid JSON:
{{"tool": "tavily_search|weather|none", "query": "short query or city name", "reason": "short reason"}}

Question: {question}
"""
