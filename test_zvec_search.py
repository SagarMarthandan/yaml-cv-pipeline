"""
test_zvec_search.py — Test runner for the Zvec Portfolio Search tool.

Runs the parsing and ingestion of repo info.md into the Zvec database, then performs
two test searches (one for Data Engineering and one for RAG/AI) to verify
relevance ranking and output formats. All operations run fully offline.
"""
import os
import sys
from zvec_portfolio_search import ingest_portfolio, search_relevant_projects


def main():
    print("=== Step 1: Ingesting Portfolio ===")
    try:
        ingest_portfolio()
    except Exception as e:
        print(f"Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("\n=== Step 2: Testing Search for 'Data Engineering' ===")
    jd_de = (
        "Looking for a Senior Data Engineer experienced in designing ELT/ETL pipelines, "
        "orchestration using Apache Airflow or Dagster, data modeling with dbt, and "
        "warehousing using BigQuery, Snowflake, or Databricks."
    )
    try:
        results = search_relevant_projects(jd_de, top_k=3)
        titles = [r['title'].lower() for r in results]
        
        # Verify that Data Engineering related projects are in the top-3
        assert any("f1 ingestion" in t or "data engineering" in t or "elt platform" in t for t in titles), \
            f"DE query assertion failed. Got titles: {titles}"
            
        for idx, match in enumerate(results):
            print(f"{idx+1}. {match['title']} (Score: {match['score']:.4f})")
    except Exception as e:
        print(f"Search failed or assertion failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("\n=== Step 3: Testing Search for 'AI / RAG Developer' ===")
    jd_ai = (
        "We are hiring an AI Engineer to build Retrieval-Augmented Generation (RAG) systems, "
        "working with vector databases, embeddings, and large language models (LLMs)."
    )
    try:
        results = search_relevant_projects(jd_ai, top_k=3)
        titles = [r['title'].lower() for r in results]
        
        # Verify that AI or RAG related projects are in the top-3
        assert any("retrieval-augmented" in t or "rag" in t or "ats resume" in t for t in titles), \
            f"AI query assertion failed. Got titles: {titles}"
            
        for idx, match in enumerate(results):
            print(f"{idx+1}. {match['title']} (Score: {match['score']:.4f})")
    except Exception as e:
        print(f"Search failed or assertion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
