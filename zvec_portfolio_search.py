"""
zvec_portfolio_search.py — Zvec Vector Database Portfolio RAG tool.

Parses repo info.md into project chunks, embeds them using a local offline
SentenceTransformer model (all-MiniLM-L6-v2), stores them in a local embedded
Zvec database, and provides query methods to search relevant projects based on
a job description.
"""
import os
import re
import shutil
import zvec
from sentence_transformers import SentenceTransformer

# Default configurations
DEFAULT_MD_PATH = r"C:\Users\sagar\Documents\YAML-CV\Base Files\Repo Info\repo info.md"
DEFAULT_DB_PATH = r"C:\Users\sagar\Documents\YAML-CV\Base Files\Repo Info\zvec_portfolio"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 maps text to 384-dimensional vectors

# Global model instance for caching
_model_instance = None


def get_embedding(text: str) -> list[float]:
    """Fetch local vector embeddings using sentence-transformers."""
    global _model_instance
    if _model_instance is None:
        print(f"Loading local SentenceTransformer model '{EMBEDDING_MODEL_NAME}'...")
        _model_instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Generate embedding on local CPU/GPU and convert to normal list of floats
    vector = _model_instance.encode(text)
    return [float(x) for x in vector]


def parse_repo_markdown(file_path: str) -> list[dict]:
    """
    Parses repo info.md into individual project chunks by section headers.
    Avoids splitting on nested code block headers or build instruction headers.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Markdown portfolio file not found at {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    in_code_block = False
    current_project_title = None
    current_project_lines = []
    projects = []
    
    # Standard headers we want to filter out that are instructions/notes rather than project titles
    ignored_keywords = {
        "create", "install", "on", "replace", "running", 
        "troubleshooting", "prerequisites", "packages", 
        "transform", "run", "using", "assert"
    }
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
        
        # Check for a project header (starts with '# ' and is not inside code blocks)
        if not in_code_block and line.startswith('# '):
            # Extract header text
            header_text = line[2:].strip()
            # Clean emojis and special characters (e.g. "📄 ATS Resume" -> "ATS Resume")
            cleaned_title = re.sub(r'[^\w\s\(\)\+\-\.:]', '', header_text).strip()
            
            # Verify it's not a generic setup/config step header
            first_word = cleaned_title.split()[0].lower() if cleaned_title else ""
            if first_word in ignored_keywords:
                if current_project_title is not None:
                    current_project_lines.append(line)
                continue
                
            # Save previous project if it exists
            if current_project_title and current_project_lines:
                projects.append({
                    "title": current_project_title,
                    "content": "\n".join(current_project_lines).strip()
                })
            current_project_title = cleaned_title
            current_project_lines = [line]
        else:
            if current_project_title is not None:
                current_project_lines.append(line)
    
    # Append the last project
    if current_project_title and current_project_lines:
        projects.append({
            "title": current_project_title,
            "content": "\n".join(current_project_lines).strip()
        })
        
    return projects


def ingest_portfolio(markdown_path: str = DEFAULT_MD_PATH, db_path: str = DEFAULT_DB_PATH, force_recreate: bool = True):
    """Chunks, embeds, and saves projects to Zvec."""
    print(f"Reading markdown file: {markdown_path}")
    projects = parse_repo_markdown(markdown_path)
    print(f"Found {len(projects)} projects/repositories to index.")
    
    if force_recreate and os.path.exists(db_path):
        print(f"Recreating database at: {db_path}")
        import time
        import stat
        
        def on_rm_error(func, path, exc_info):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass
                
        for attempt in range(5):
            try:
                shutil.rmtree(db_path, onerror=on_rm_error)
                break
            except Exception as e:
                if attempt == 4:
                    raise e
                time.sleep(1)
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Define collection schema with 384 dimensions matching all-MiniLM-L6-v2
    schema = zvec.CollectionSchema(
        name="portfolio",
        fields=[
            zvec.FieldSchema(name="title", data_type=zvec.DataType.STRING),
            zvec.FieldSchema(name="text", data_type=zvec.DataType.STRING)
        ],
        vectors=zvec.VectorSchema("embedding", zvec.DataType.VECTOR_FP32, EMBEDDING_DIMENSION),
    )
    
    collection = zvec.create_and_open(path=db_path, schema=schema)
    
    docs = []
    for idx, proj in enumerate(projects):
        print(f"[{idx+1}/{len(projects)}] Embedding and indexing: {proj['title']}")
        embedding = get_embedding(proj['content'])
        
        docs.append(zvec.Doc(
            id=f"proj_{idx}",
            vectors={"embedding": embedding},
            fields={"title": proj['title'], "text": proj['content']}
        ))
        
    collection.insert(docs)
    print("Database indexing complete.")


def search_relevant_projects(job_description: str, top_k: int = 4, db_path: str = DEFAULT_DB_PATH) -> list[dict]:
    """Queries Zvec to find the most relevant projects for a given JD."""
    if not os.path.exists(db_path):
        raise ValueError(f"Database not found at {db_path}. Please run ingestion first.")
        
    collection = zvec.open(path=db_path)
    
    print(f"Generating query embedding locally...")
    jd_embedding = get_embedding(job_description)
    
    print(f"Searching Zvec collection for top {top_k} matches...")
    results = collection.query(
        zvec.VectorQuery("embedding", vector=jd_embedding),
        topk=top_k
    )
    
    matched_projects = []
    for doc in results:
        matched_projects.append({
            "id": doc.id,
            "score": doc.score,
            "title": doc.fields.get("title", ""),
            "content": doc.fields.get("text", "")
        })
        
    return matched_projects


if __name__ == '__main__':
    import sys
    import yaml
    
    if len(sys.argv) < 3:
        print("Usage: python zvec_portfolio_search.py <job_description_path> <output_project_info_path>")
        sys.exit(1)
        
    jd_path = sys.argv[1]
    out_path = sys.argv[2]
    
    if not os.path.exists(jd_path):
        print(f"Error: Job description file not found at {jd_path}")
        sys.exit(1)
        
    # Parse Job Description inputs (handles Job_Description.yaml or raw text JDs)
    if jd_path.lower().endswith(('.yaml', '.yml')):
        try:
            with open(jd_path, 'r', encoding='utf-8') as f:
                jd_data = yaml.safe_load(f)
        except Exception as e:
            print(f"Error parsing YAML job description: {e}")
            sys.exit(1)
        
        query_parts = []
        if isinstance(jd_data, dict):
            if 'position' in jd_data:
                query_parts.append(f"Position: {jd_data['position']}")
            sections = jd_data.get('sections', [])
            for sec in sections:
                if isinstance(sec, dict):
                    title = sec.get('title', '')
                    content = sec.get('content', '')
                    bullets = sec.get('bullets', [])
                    query_parts.append(f"{title}: {content}")
                    if bullets:
                        query_parts.extend(bullets)
        jd_text = "\n".join(query_parts)
    else:
        with open(jd_path, 'r', encoding='utf-8') as f:
            jd_text = f.read()
            
    try:
        # Auto-seed database if it doesn't exist yet
        if not os.path.exists(DEFAULT_DB_PATH):
            print("Zvec database not found. Indexing portfolio first...")
            ingest_portfolio(DEFAULT_MD_PATH, DEFAULT_DB_PATH, force_recreate=True)
            
        # Query matching projects
        matched = search_relevant_projects(jd_text, top_k=4)
        
        # Format matched projects into markdown portfolio format
        portfolio_md = "# Tailored Project Portfolio\n\n"
        for proj in matched:
            portfolio_md += f"{proj['content']}\n\n---\n\n"
            
        # Write outputs
        out_dir = os.path.dirname(os.path.abspath(out_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(portfolio_md)
            
        print(f"Successfully wrote {len(matched)} tailored projects to {out_path}")
        
    except Exception as e:
        print(f"Error executing portfolio search: {e}")
        sys.exit(1)
