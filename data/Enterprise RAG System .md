### How I Actually Implement an Enterprise RAG System (Not a Demo Toy)

Everyone has seen the “hello world” RAG demo:

Dump a few PDFs into a notebook
Call a load_and_split() helper
Push chunks into an in-memory vector DB
Wrap it in a FastAPI endpoint
That’s great for a weekend experiment — but it completely falls apart the moment you touch real enterprise systems:

Outlook / O365 mailboxes
SharePoint libraries
Local / network drives full of PDFs and Word docs
Multiple business units and tenants
Strict security, PII rules, audits and SLAs
In this blog, I’ll walk through how I actually think about implementing an enterprise-grade RAG system end to end — the kind you can defend in a design review and eventually put into production.

I’ll keep it practical and opinionated, not hand-wavy.

1. Start Before “RAG”: Clarify Use Case and Data Dynamics

Before talking about chunking or embeddings, I always nail down three things.

1.1 What problem are we solving?

Some examples:

Customer support assistant for B2C customers
Internal policy assistant for HR / legal
Developer assistant over internal code and design docs
For each use case, I want answers to:

Primary goal
Example: “Reduce L1 ticket load by 20%” or “Cut policy search time from 10 minutes to 30 seconds.”
User type
Internal employees, external customers, partners, or a mix.
Risk profile
How bad is a wrong answer? Annoying? Legal exposure? Medical risk?
The higher the risk, the more strict I’ll be with retrieval, prompts, and guardrails.

1.2 How does the data behave?

Concrete questions I ask:

Is the data mostly static (e.g., last 3 years of policies) or dynamic (new docs/emails every day)?
Which systems do documents live in today?
Outlook / O365 mailboxes
SharePoint sites
Local / shared drives
Wikis (Confluence, Notion), ticketing systems (Zendesk, ServiceNow), Jira, etc.
How frequently do policies or documents change?
Are deletions or deprecations important (e.g., old policies must not be used)?
If the data is dynamic (it usually is), the design must support continuous ingestion and re-indexing, not just a one-time data load.

2. Data Layer First: RAW → SILVER → GOLD

Most failed RAG systems skip proper data modeling and go straight from “source system” to “embeddings.” That works until you hit:

Duplicate or conflicting docs
Massive noise (irrelevant emails, random drafts)
PII everywhere
Multiple document versions with no clear “truth”
I prefer a data-lake-style approach with three logical layers: RAW, SILVER and GOLD.

2.1 RAW (Landing Zone)

Goal: store as-is copies from each source, with minimal technical metadata.

Conceptual layout (not tied to any cloud):

rag-data/
raw/
email/
source=o365/year=2025/month=12/day=06/…
docs/
source=sharepoint/site=kb/library=support_policies/year=2025/month=12/…
source=fileshare/…
Characteristics:

Sources are separated: email vs docs vs wiki vs tickets.
Partitioned by time for lifecycle rules and easier processing.
Original file types preserved: .eml, .json, .pdf, .docx, etc.
2.2 SILVER (Cleaned and Structured Text + Metadata)

Goal: extract text and structured metadata, clean it and normalize formats.

Examples:

Emails
subject, from, to, cc, date, thread_id, body_text, attachments, labels, folder_path, has_pii
Docs (PDF, Word, etc.)
title, full_text, source_system, url_or_path, last_modified, author, department, language
Cleaning typically includes:

Removing signatures, disclaimers and boilerplate.
Stripping HTML to plain text.
Removing repeated headers/footers in PDFs.
Fixing encodings and weird whitespace.
Optional masking of PII (email addresses, account numbers, phone numbers, etc.).
2.3 GOLD (RAG-Ready Canonical Documents)

Goal: unify all sources into a single “document abstraction” for RAG and search.

Example schema:

gold.unified_docs:
doc_id # unique row id for this version
logical_doc_id # persistent id across versions of the same doc
version_number
source_system # email | sharepoint | wiki | ticketing | fileshare
source_type # policy | faq | ticket_resolution | runbook | announcement | …
title
full_text
language
tenant_id
business_unit
created_at
updated_at
valid_from
valid_to
is_active # for deletions / deprecations
metadata_json # tags: product, region, category, etc.
This is the layer from which we chunk and embed.
Not RAW, not SILVER — GOLD.

3. Ingestion: Backfill and Continuous Updates

Enterprise RAG fails if it only understands yesterday’s data.

3.1 Backfill (Historical Load)

For each source, I design a one-off historical load:

Email (Outlook / O365)

Use Microsoft Graph API.
Filter on specific folders (e.g., Inbox/CSD-Tickets) or subject patterns ([CSD], ticket IDs).
Dump to RAW (JSON or EML), then transform to SILVER/GOLD.
SharePoint

Use SharePoint / Graph APIs.
Enumerate configured sites and libraries.
Download docs with metadata → RAW → SILVER.
Local / shared drives
Use a sync tool or DataSync-style job to upload to RAW.
Attach provenance metadata: original path, server, share name.
3.2 Incremental Ingestion (Daily or Near Real Time)

Each connector maintains an offset:

last_received_datetime for emails.
last_modified for SharePoint docs.
(path, last_modified) and checksum for file shares.
Then I schedule:

Batch jobs (hourly/daily) via Airflow, Step Functions, Argo, etc.
Or streaming flows where needed (events → queue/stream → transformer jobs).
New and updated items flow RAW → SILVER → GOLD.
Deletions or deprecations are represented by is_active = false or by updating valid_to.

4. Don’t Jump into Chunking Blindly: Analyze the Data

Before splitting any document, I want to understand it.

Questions I usually answer:

How big are the documents on average?
How skewed is the distribution of lengths?
Are emails mostly short while policy PDFs are 100+ pages?
How much PII is present?
Are we ingesting a lot of noise (notifications, spam, marketing)?
4.1 Relevance Estimation at Scale

You can’t manually open 100k PDFs, so I do:

Random sampling + domain review
Take 100–200 docs, have domain experts mark “useful / not useful”.
Cluster-based sampling
Use fast embeddings to cluster docs by similarity.
Sample from each cluster to ensure coverage.
Label clusters as “mostly relevant / mostly noise”.
If a large portion is irrelevant, I improve filters at the ingestion stage (folders, labels, paths, whitelists).

4.2 PII Detection and Handling

For emails and tickets, PII is everywhere.

Typical approach:

Rule-based regex for emails, phone numbers, account IDs.
An additional PII detection model (Presidio, custom NER, etc.) for names and addresses.
For customer-facing RAG, mask or hash PII in GOLD.
For internal-only RAG, keep PII but lock everything down via IAM, encryption and detailed logging.
5. Chunking and Embeddings: Data-Driven, Not Magic Numbers

Now that we know our data, we can design chunking and choose embedding models.

5.1 Choosing an Embedding Model

I look at:

Maximum input tokens (this constrains max chunk size).
Vector dimension (affects index size and memory).
Latency and throughput for batch embedding.
Where we can run it (OpenAI, Bedrock, Vertex, in-house, etc.).
Licensing and cost.
For most systems, I prefer one core embedding model for all text sources (emails, docs, tickets, wiki). Multiple models means multiple indices and tricky retrieval logic unless there is a very strong reason.

5.2 Chunk Size and Overlap

I make this token-based, not word-based.

Good starting point:

Chunk size: 300–800 tokens.
Overlap: 20–80 tokens.
Then I tune based on:

Typical section/paragraph sizes.
Domain — legal contracts behave differently from FAQs.
Embedding model’s context limit (leave headroom so you don’t sit at the limit).
Strategies that work well:

Fixed-size chunking as a simple baseline.
Recursive / structure-aware splitting:
Split on headings → paragraphs → sentences → characters as a last resort.
Parent–child chunking:
Small “child” chunks for retrieval.
Larger “parent” chunks for providing extra context to the LLM.
The key idea: chunking is an experiment, not a “set it once and forget it” decision. Measure retrieval quality and iterate.

6. Vector Database and Retrieval Pipeline

Once GOLD documents become chunks and embeddings, we need somewhere robust to store and search them.

6.1 Choosing a Vector Store


Great for POCs: Chroma, in-memory FAISS.

For production, I look at:

Managed services: Pinecone, managed Qdrant/Weaviate, OpenSearch with vector support.
Self-hosted: Qdrant, Weaviate, Milvus, FAISS with your own service layer.
Selection criteria:

ANN algorithm (HNSW, IVF, PQ) and scalability.
Metadata filtering capabilities.
Latency under concurrent load.
Operational aspects: backups, high availability, VPC/VNet, IAM, observability.
6.2 Record Schema in the Vector DB

Each chunk roughly looks like this:

{
"id": "doc123::chunk007",
"vector": [ … ],
"metadata": {
"doc_id": "doc123",
"logical_doc_id": "L-456",
"chunk_index": 7,
"source_system": "sharepoint",
"source_type": "policy",
"title": "Internet Usage Policy",
"tenant_id": "TENANT_001",
"language": "en",
"region": "EU",
"product": "Fiber",
"version_number": 3,
"is_active": true,
"has_pii": false,
"created_at": "2025–09–01T12:00:00Z",
"updated_at": "2025–11–20T09:32:00Z"
}
}
This metadata is essential for:

Multi-tenant isolation and authorization.
Region or product-specific filtering.
Preferring the latest active versions of documents.
6.3 Retrieval Flow for Each Query

At runtime, I like a multi-stage retrieval pipeline:

Preprocess query

Normalize, expand common acronyms, optionally spell-check.
Embed query

Use the same embedding model as for chunks.
Vector search (ANN)

Get top K₁ (e.g., 20–50) chunks.
Apply strict metadata filters: tenant, region, business unit, doc type, is_active.
Keyword / BM25 search (Hybrid)

Run parallel keyword search in a text index (OpenSearch / Elasticsearch).
Especially useful for IDs, exact terms and rare keywords.
Fusion and reranking

Merge candidate sets and deduplicate by chunk ID.
Techniques:
Score fusion (weighted combination of vector and BM25 scores).
Cross-encoder reranker over the best 20–50 chunks.
Optional MMR (Maximal Marginal Relevance) to promote diversity.
Select top K chunks for the LLM

Usually 3–10 chunks depending on the model’s context window.
Send to LLM with system prompt and user query

Generate answer and include citations.
Think “retrieve wide, read narrow”: K₁ can be large, K₂ must fit context.

7. LLM Orchestration, Prompting and Multi-Turn RAG

7.1 Grounded Prompt Template

I use a strict system prompt to reduce hallucinations:

You are an enterprise assistant. Answer only using the information in the context below. If the answer is not present, say: “I don’t have enough information in the current documents to answer that.” Always mention which document(s) you used (e.g., policy name or document ID). If documents contradict each other, call it out explicitly.

Then the actual call looks like:

System prompt: [as above]
Context:
[Doc 1: …]
[Doc 2: …]
[Doc 3: …]
User question: { user_query }
Assistant: { Output }
Whenever possible, I ask the model to return structured output (JSON with fields like answer, citations, reasoning) so it’s easier to log, display and post-process.

7.2 Conversational RAG (Multi-Turn Chat)

For chat interfaces, I:

Maintain conversation history keyed by a session ID.
Use the LLM to rewrite the current turn into a standalone query using history.
Example:

User: “How long does it take?”
Rewritten: “How long does the return process take for Fiber customers in Germany?”
Run retrieval for the rewritten query, not the raw one.
Periodically summarize older history into a short summary to avoid overflowing context.
8. Security, Privacy and Multi-Tenancy

Enterprise RAG is dead on arrival if security is an afterthought.

8.1 Authentication and Authorization

Typical setup:

Authenticate against existing IdP (Okta, Azure AD, Google Workspace, etc.).
Pass a JWT or access token to the backend containing:
sub (user ID)
tenant_id
roles and groups
Optional data classification permissions.
Every retrieval call:

Extracts tenant_id and roles from the token.
Applies mandatory metadata filters (tenant_id, data classification).
Logs who accessed what.
8.2 Preventing PII and Policy Leaks

Defense in depth:

PII masking or hashing in GOLD where required.
Strict filters at retrieval time: tenant, region, classification, legal hold.
Guardrails in prompts: never invent account numbers, never paraphrase private information not present in context.
Comprehensive logging of:
Query text (possibly redacted).
Retrieved document IDs.
Answer returned.
User and timestamp.
8.3 Multi-Tenancy Strategies

Common patterns:

Soft isolation

Single shared index with a tenant_id field.
Enforcement happens via metadata filters.
Hard isolation

One index (or even one deployment) per tenant.
Stronger isolation but higher cost and operational overhead.
Hybrid

Big or regulated tenants get dedicated indices.
Small tenants share a multi-tenant index.
Choice depends on regulatory risk, number of tenants and budget.

9. Observability, Evaluation and Feedback Loops

“Looks good in the demo” is not a metric.

9.1 System Metrics

Track basic SRE metrics:

Latency for each stage:
Embedding, vector DB, BM25, reranker, LLM.
P50 / P95 / P99 latency for the entire request.
Error rates and timeouts.
Resource usage for embedding and LLM servers.
9.2 Retrieval and Answer Quality

You need both offline evaluation and online signals.

Offline:

Build a labeled evaluation set:
(query, set of relevant documents) pairs.
Measure IR metrics:
Recall@K, Precision@K, NDCG, MRR.
Run automated “LLM-as-judge” evaluations:
Ask another model to rate answers on correctness, groundedness, completeness.
Online:

Track user feedback (thumbs up/down).
Track escalation to human agents.
Capture when users immediately rephrase the same question (signal of dissatisfaction).
9.3 Feedback Into the System

From these signals, you can:

Create new training pairs for fine-tuning embeddings.
Identify missing documentation (queries that consistently fail).
Discover bad or outdated documents that cause confusion.
A/B test changes: new prompts, chunking parameters, rerankers or LLMs.
A healthy Enterprise RAG is a living system. It continuously improves as you collect data.

10. Cost Optimization and Advanced Roadmap

Once the system is reliable, the next steps are usually cost and sophistication.

10.1 Cost Levers

Embeddings

Use smaller, cheaper models where acceptable.
Cache embeddings per (doc_id, chunk_index).
Only re-embed changed chunks, not entire docs.
Vector store
Use cheaper storage tiers for old or rarely used data.
Consider quantization or product quantization for huge corpora.
LLM

Use a smaller, fast model for RAG (the knowledge is in your docs, not in the model).
Stream responses and batch requests when possible.
Cache frequent answers, both exact and semantically similar queries.
10.2 Advanced Patterns for Later

Once the basics are solid, you can explore:

Agentic RAG

Let the LLM decide when to search, which tools to call, or when to ask clarification questions.
Graph-augmented RAG (Graph RAG)

Build an explicit knowledge graph (entities, relations) from your documents.
Use it for multi-hop reasoning (great for legal, financial, or complex products).
Multimodal RAG

Incorporate images, diagrams, tables and code snippets, not just plain text.
Domain-specific fine-tuning

Fine-tune embeddings and/or the LLM on your domain for tougher verticals.
Closing Thoughts

Implementing an Enterprise RAG system is not about importing a library and calling similarity_search. It’s about:

Treating documents as data assets with lifecycle, versions and governance.
Designing a robust data layer before touching embeddings.
Building a retrieval pipeline, not a single vector search call.
Taking security, privacy and multi-tenancy seriously from day one.
Accepting that iteration is the product: chunk sizes, models, prompts and indices will evolve.
If you approach RAG this way, you won’t just build another flashy demo. You’ll ship something your infra, security and business teams can actually trust — and that’s when RAG becomes truly valuable in the enterprise.