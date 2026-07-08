import re
from typing import List, Dict
from urllib.parse import quote

import requests

STOP_WORDS = {
    'the', 'and', 'is', 'in', 'to', 'of', 'a', 'an', 'for', 'on', 'with', 'by', 'from', 'as', 'at', 'it', 'that', 'this', 'are', 'be', 'was', 'were', 'has', 'have', 'not', 'yet'
}


def _tokenize(s: str) -> List[str]:
    return re.findall(r"\w+", s.lower())


def _extract_support_words(text: str, source: str, max_words: int = 3) -> List[str]:
    claim_tokens = [tok for tok in _tokenize(text) if tok not in STOP_WORDS]
    source_tokens = set(_tokenize(source))
    support_words = []
    for tok in claim_tokens:
        if tok in source_tokens and tok not in support_words:
            support_words.append(tok)
    if not support_words:
        support_words = claim_tokens[:max_words]
    return support_words[:max_words]


def _is_question(text: str) -> bool:
    return bool(re.match(r"^(is|are|was|were|did|does|do|has|have|had|will|can|could|should|would|may|might)\b", text.strip().lower()))


def _has_negation(text: str) -> bool:
    return bool(re.search(r"\b(no|not|never|none|neither|nor|unless|without|n't)\b", text.lower()))


def _detect_death_query(text: str) -> bool:
    lower = text.lower()
    return bool(re.search(r"\b(dead|died|death|deceased|passed away|passed|obituary)\b", lower))


def _contains_death_evidence(text: str) -> bool:
    lower = text.lower()
    return bool(re.search(r"\b(die|died|dead|death|deceased|passed away|obituary|killed|murdered)\b", lower))


def _claim_support_score(claim: str, text: str) -> float:
    claim_tokens = [tok for tok in _tokenize(claim) if tok not in STOP_WORDS]
    if not claim_tokens:
        return 0.0
    text_tokens = set(_tokenize(text))
    overlap = [tok for tok in claim_tokens if tok in text_tokens]
    return len(overlap) / len(claim_tokens)


def _infer_verdict(claim: str, wiki_matches: List[Dict], is_death_claim: bool) -> Dict[str, str]:
    top_match = wiki_matches[0]
    evidence_text = f"{top_match.get('title', '')} {top_match.get('snippet', '')}"
    support_score = _claim_support_score(claim, evidence_text)
    has_negation = _has_negation(evidence_text)

    if is_death_claim:
        if _contains_death_evidence(evidence_text):
            verdict = "Likely true"
            note = "The top Wikipedia result contains death-related evidence."
        else:
            verdict = "Likely false"
            note = "The top Wikipedia result does not include death evidence, so the claim appears incorrect."
    elif has_negation and support_score > 0:
        verdict = "Likely false"
        note = "The top Wikipedia result contains negation language, suggesting the claim is incorrect."
    elif support_score >= 0.4:
        verdict = "Likely true"
        note = "The top Wikipedia result contains supporting evidence for the claim."
    elif support_score >= 0.15:
        verdict = "Possible"
        note = "The top Wikipedia result contains some matching terms but not strong evidence."
    else:
        verdict = "Unknown"
        note = "The top Wikipedia result does not clearly support or contradict the claim."

    return {
        "verdict": verdict,
        "note": note,
        "evidence": evidence_text,
    }


def find_local_matches(text: str, trusted_corpus: List[str]) -> List[Dict]:
    tokens = set(_tokenize(text))
    results = []
    for entry in trusted_corpus:
        snippet_tokens = set(_tokenize(entry))
        overlap = tokens.intersection(snippet_tokens)
        score = len(overlap) / max(len(tokens), 1)
        results.append({"snippet": entry, "score": score})
    return sorted(results, key=lambda item: item["score"], reverse=True)


def search_wikipedia(query: str, limit: int = 3) -> List[Dict]:
    endpoint = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srprop": "snippet|titlesnippet",
        "format": "json",
        "formatversion": 2,
        "utf8": 1,
    }
    headers = {
        "User-Agent": "FakeNewsDetection/1.0 (https://example.com)"
    }
    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=7)
        response.raise_for_status()
        data = response.json()
        search_hits = data.get("query", {}).get("search", [])
    except Exception:
        return []

    results = []
    for rank, hit in enumerate(search_hits, start=1):
        title = hit.get("title")
        snippet = re.sub(r"<.*?>", "", hit.get("snippet", "")).strip()
        pageid = hit.get("pageid")
        url = f"https://en.wikipedia.org/?curid={pageid}" if pageid else None
        results.append({
            "title": title,
            "snippet": snippet,
            "url": url,
            "score": float(1.0 / rank),
        })
    return results


def score_match(text: str, snippet: str) -> float:
    t_tokens = set(_tokenize(text))
    s_tokens = set(_tokenize(snippet))
    if not t_tokens or not s_tokens:
        return 0.0
    overlap = t_tokens.intersection(s_tokens)
    return len(overlap) / max(len(t_tokens), 1)


def fact_check_text(text: str) -> Dict:
    """Run simple fact-check using Wikipedia search and a local fallback."""
    trusted_corpus = [
        "Official statement from government confirms new policy",
        "Press release: company launches new eco initiative",
        "Local council publishes minutes confirming project approval",
        "Study shows eating chocolate cures common cold (peer-reviewed)",
        "Financial regulators confirm the new banking rules",
    ]
    claims = [c.strip() for c in re.split(r"(?<=[.!?])\s+", text) if c.strip()]
    claim_results = []
    for claim in claims:
        is_death_claim = _detect_death_query(claim)
        wiki_matches = search_wikipedia(claim)
        if wiki_matches:
            top_match = wiki_matches[0]
            support_source = f"{top_match.get('title', '')} {top_match.get('snippet', '')}"
            support_words = _extract_support_words(claim, support_source)
            verdict_data = _infer_verdict(claim, wiki_matches, is_death_claim)
            claim_results.append({
                "claim": claim,
                "verdict": verdict_data["verdict"],
                "source": "wikipedia",
                "support_words": support_words,
                "top_matches": wiki_matches,
                "note": verdict_data["note"],
            })
        else:
            matches = find_local_matches(claim, trusted_corpus)
            top_match = matches[0] if matches else {"snippet": "", "score": 0.0}
            support_words = _extract_support_words(claim, top_match.get("snippet", ""))
            if is_death_claim:
                verdict = "Likely false"
                note = "No Wikipedia matches found and the query is death-related, so the claim appears unlikely."
            else:
                verdict = "Possible"
                note = "No Wikipedia matches found; using local heuristic fallback."
            claim_results.append({
                "claim": claim,
                "verdict": verdict,
                "source": "local heuristic",
                "support_words": support_words,
                "top_matches": matches[:3],
                "note": note,
            })
    return {"claims": claim_results}
