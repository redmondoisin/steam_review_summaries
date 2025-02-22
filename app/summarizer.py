import re
import time
import requests
from typing import List, Dict
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer
from .utils import clean_text

HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

def get_reviews(app_id: str, max_reviews: int = 50) -> List[Dict]:
    reviews: List[Dict] = []
    cursor: str = "*"
    base_url: str = f"https://store.steampowered.com/appreviews/{app_id}"
    params: Dict[str, object] = {
        'json': 1,
        'cursor': cursor,
        'language': 'english',
        'review_type': 'all',
        'purchase_type': 'all',
        'num_per_page': 100
    }
    while True:
        params['cursor'] = cursor
        response = requests.get(base_url, headers=HEADERS, params=params)
        data: Dict = response.json()
        batch: List[Dict] = data.get('reviews', [])
        if not batch:
            break
        reviews.extend(batch)
        new_cursor: str = data.get('cursor')
        if len(reviews) >= max_reviews or new_cursor == cursor:
            break
        cursor = new_cursor
        time.sleep(1)
    return reviews[:max_reviews]

def summarize_reviews(reviews: List[Dict], max_length: int = 60, min_length: int = 40, bullet: bool = False) -> str:
    review_texts: List[str] = [clean_text(r.get('review', '')) for r in reviews if r.get('review')]
    combined_text: str = " ".join(review_texts)
    if not combined_text.strip():
        return "No review content available."
    
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    
    max_input_length: int = tokenizer.model_max_length
    if max_input_length > 10000:
        max_input_length = 1024
    offset: int = 2
    safety_margin: int = 50
    max_chunk_tokens: int = max_input_length - offset - safety_margin

    input_tokens: List[int] = tokenizer.encode(combined_text, truncation=False)
    print(f"Total tokens: {len(input_tokens)}; Allowed per chunk: {max_chunk_tokens}")
    
    if len(input_tokens) > max_input_length:
        chunks: List[str] = []
        for i in range(0, len(input_tokens), max_chunk_tokens):
            chunk_ids: List[int] = input_tokens[i:i+max_chunk_tokens]
            if not chunk_ids:
                continue
            chunk_text: str = tokenizer.decode(chunk_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
            chunks.append(chunk_text)
        summaries: List[str] = []
        for chunk in chunks:
            summary_chunk = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False, truncation=True)
            summaries.append(summary_chunk[0]['summary_text'])
        final_summary: str = " ".join(summaries)
    else:
        summary = summarizer(combined_text, max_length=max_length, min_length=min_length, do_sample=False, truncation=True)
        final_summary: str = summary[0]['summary_text']
    
    if bullet:
        sentences = re.split(r'\.\s+', final_summary)
        bullet_summary = "\n".join(["- " + sentence.strip() for sentence in sentences if sentence.strip()])
        final_summary = bullet_summary

    print("Summary:", final_summary)
    return final_summary

def get_app_id_by_name(game_name: str) -> str:
    search_url: str = f"https://store.steampowered.com/search/?term={game_name.strip()}"
    response = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    result = soup.find("a", class_="search_result_row ds_collapse_flag")
    if result:
        href: str = result.get("href", "")
        match = re.search(r'/app/(\d+)/', href)
        if match:
            return match.group(1)
    return ""
