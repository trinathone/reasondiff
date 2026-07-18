import re
from difflib import SequenceMatcher
from typing import List, Tuple, Dict, Any


def extract_reasoning(response_msg: Dict[str, Any]) -> str:
    """Extract reasoning content from various LLM response formats."""
    if isinstance(response_msg, dict):
        if 'reasoning_content' in response_msg:
            return response_msg['reasoning_content']

        content = response_msg.get('content', '')
        if not isinstance(content, str):
            content = str(content)

        think_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
        if think_match:
            return think_match.group(1).strip()

        reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', content, re.DOTALL)
        if reasoning_match:
            return reasoning_match.group(1).strip()

        return content.strip()

    return str(response_msg)


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences, handling multiple delimiters."""
    sentences = []
    current = ""

    for char in text:
        current += char
        if char == '.' or char == '\n':
            sentence = current.strip()
            if sentence:
                sentences.append(sentence)
            current = ""

    if current.strip():
        sentences.append(current.strip())

    return sentences


def compute_similarity(seq1: List[str], seq2: List[str]) -> float:
    """Compute similarity score between two sequences (0-100)."""
    if not seq1 and not seq2:
        return 100.0
    if not seq1 or not seq2:
        return 0.0

    matcher = SequenceMatcher(None, seq1, seq2)
    return matcher.ratio() * 100


def find_divergence_point(seq1: List[str], seq2: List[str]) -> int:
    """Find the sentence index where the sequences first diverge."""
    for i, (s1, s2) in enumerate(zip(seq1, seq2)):
        if s1 != s2:
            return i

    if len(seq1) != len(seq2):
        return min(len(seq1), len(seq2))

    return -1


def generate_diff_opcodes(seq1: List[str], seq2: List[str]) -> List[Tuple[str, int, int, int, int]]:
    """Generate diff opcodes (operation, i1, i2, j1, j2)."""
    matcher = SequenceMatcher(None, seq1, seq2)
    return matcher.get_opcodes()


def opcodes_to_colored_diff(opcodes: List[Tuple[str, int, int, int, int]],
                             seq1: List[str], seq2: List[str]) -> Tuple[str, str]:
    """Convert opcodes to HTML-formatted diff views for left and right panels."""
    left_html = ""
    right_html = ""

    for op, i1, i2, j1, j2 in opcodes:
        if op == 'equal':
            for s in seq1[i1:i2]:
                left_html += f'<span class="equal">{escape_html(s)}</span> '
            for s in seq2[j1:j2]:
                right_html += f'<span class="equal">{escape_html(s)}</span> '

        elif op == 'delete':
            for s in seq1[i1:i2]:
                left_html += f'<span class="deleted">{escape_html(s)}</span> '

        elif op == 'insert':
            for s in seq2[j1:j2]:
                right_html += f'<span class="inserted">{escape_html(s)}</span> '

        elif op == 'replace':
            for s in seq1[i1:i2]:
                left_html += f'<span class="deleted">{escape_html(s)}</span> '
            for s in seq2[j1:j2]:
                right_html += f'<span class="inserted">{escape_html(s)}</span> '

    return left_html, right_html


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def diff_reasoning_chains(reasoning_a: str, reasoning_b: str) -> Dict[str, Any]:
    """Compute diff between two reasoning chains."""
    sentences_a = split_into_sentences(reasoning_a)
    sentences_b = split_into_sentences(reasoning_b)

    similarity = compute_similarity(sentences_a, sentences_b)
    divergence_idx = find_divergence_point(sentences_a, sentences_b)
    opcodes = generate_diff_opcodes(sentences_a, sentences_b)
    left_diff, right_diff = opcodes_to_colored_diff(opcodes, sentences_a, sentences_b)

    return {
        'similarity_score': round(similarity, 2),
        'divergence_point': divergence_idx if divergence_idx >= 0 else None,
        'reasoning_a_length': len(reasoning_a),
        'reasoning_b_length': len(reasoning_b),
        'sentences_a_count': len(sentences_a),
        'sentences_b_count': len(sentences_b),
        'left_diff_html': left_diff.strip(),
        'right_diff_html': right_diff.strip(),
    }
