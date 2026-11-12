# How LLMs Work in UdyamSathi

An LLM (large language model) learns patterns from a very large collection of
text. It breaks a user's message into tokens, predicts likely next tokens, and
repeats that process to produce an answer. It does not automatically know
whether an answer is current or true, so UdyamSathi should ground answers in
the scheme records and link users to the official source.

## UdyamSathi request flow

```text
User question
      |
      v
FastAPI /questions
      |
      v
TF-IDF search + cosine similarity
      |
      v
Relevant scheme records
      |
      v
LLM explains the evidence in simple language
      |
      v
Answer with limits and official-source reminder
```

The current service uses TF-IDF and cosine similarity to find relevant records.
This is a retrieval step, not an LLM: it compares important words in the
question with words in each record. A future LLM layer could use those
retrieved records as context and explain them without inventing unsupported
details.

## One function explained

`search_records` in `app/smart_search.py` accepts the records, turns each record
into searchable text, and builds a TF-IDF vector for every record. It converts
the question into another vector, calculates cosine similarity between the
question and every record, and returns the records from the highest score to
the lowest score. An empty question returns no matches.

## Important limitation

The records can answer facts that are present in the dataset, such as project
limits, subsidy descriptions, and broad eligibility rules. They cannot decide
whether a particular person will be approved, provide current application
status, or replace a bank or government decision. Those questions need more
information or an official verification step.
