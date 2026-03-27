"""import os
import json
import numpy as np
import tensorflow as tf
from schemas import SentenceResult

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = os.getenv("MODEL_PATH", "../saved_models/skimlit_model5_best")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "../saved_models/class_names.json")

_model = None
_class_names = None


def load_models():
    global _model, _class_names
    print("Loading SkimLit model...")
    _model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH) as f:
        _class_names = json.load(f)
    print(f"Model loaded. Classes: {_class_names}")


def model_loaded() -> bool:
    return _model is not None


def split_into_sentences(abstract: str) -> list[str]:
    Split abstract into sentences, filtering empties.
    sentences = [s.strip() for s in abstract.split(".") if s.strip()]
    return sentences


def classify_abstract(abstract: str) -> list[SentenceResult]:
    Run inference on an abstract.
    Returns a list of SentenceResult with label and confidence per sentence.
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_models() first.")

    sentences = split_into_sentences(abstract)
    if not sentences:
        return []

    # Build inputs — Model 5 needs token, char, line_number, total_lines
    total_lines = len(sentences)
    line_numbers = list(range(total_lines))

    # Character-split sentences
    char_sentences = [" ".join(list(s.lower())) for s in sentences]

    # Normalise positional features
    line_number_input = np.array(line_numbers) / max(total_lines - 1, 1)
    total_lines_input = np.array([total_lines] * total_lines) / 20.0  # normalise by max expected

    pred_probs = _model.predict({
        "token_inputs": np.array(sentences),
        "char_inputs":  np.array(char_sentences),
        "line_number_input":  line_number_input.reshape(-1, 1),
        "total_lines_input":  total_lines_input.reshape(-1, 1),
    }, verbose=0)

    pred_classes = np.argmax(pred_probs, axis=1)
    confidences   = np.max(pred_probs, axis=1)

    return [
        SentenceResult(
            sentence=sentence,
            label=_class_names[pred_class],
            confidence=float(confidence)
        )
        for sentence, pred_class, confidence
        in zip(sentences, pred_classes, confidences)
    ]
"""
import os
import json
import re
import numpy as np
import tensorflow as tf
from schemas import SentenceResult

MODEL_PATH = os.getenv("MODEL_PATH", "./saved_models/skimlit_model5_best")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "./saved_models/class_names.json")

_model = None
_class_names = None


def load_models():
    global _model, _class_names
    print("Loading SkimLit model...")
    _model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH, "r") as f:
        _class_names = json.load(f)
    print(f"Model loaded. Classes: {_class_names}")


def model_loaded() -> bool:
    return _model is not None


def split_into_sentences(abstract: str) -> list[str]:
    """Split abstract into sentences and remove empty strings."""
    sentences = re.split(r"(?<=[.!?])\s+", abstract.strip())
    return [s.strip() for s in sentences if s.strip()]


def classify_abstract(abstract: str) -> list[SentenceResult]:
    """Run inference on an abstract and return sentence-level predictions."""
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_models() first.")
    if _class_names is None:
        raise RuntimeError("Class names not loaded. Call load_models() first.")

    sentences = split_into_sentences(abstract)
    if not sentences:
        return []

    n_sentences = len(sentences)

    # Match training shapes
    """
    line_depth = 15
    line_depth = int(_model.get_layer("line_number_input").shape[-1])
    total_depth = int(_model.get_layer("total_line_input").shape[-1])
    """
    line_depth = int(_model.get_layer("line_number_input").batch_shape[-1])
    total_depth = int(_model.get_layer("total_line_input").batch_shape[-1])

    line_number_input = tf.one_hot(np.arange(n_sentences), depth=line_depth).numpy().astype(np.float32)
    total_lines_input = tf.one_hot(np.repeat(n_sentences, n_sentences), depth=total_depth).numpy().astype(np.float32)
    line_number_input = tf.one_hot(np.arange(n_sentences), depth=line_depth).numpy().astype(np.float32)
    total_lines_input = tf.one_hot(np.repeat(n_sentences, n_sentences), depth=total_depth).numpy().astype(np.float32)

    """token_input = np.array(sentences, dtype=object).reshape(-1, 1)
    char_input = np.array([" ".join(list(s.lower())) for s in sentences], dtype=object).reshape(-1, 1)
    """
    token_input = tf.constant(sentences, dtype=tf.string)[:, tf.newaxis]
    char_input = tf.constant([" ".join(list(s.lower())) for s in sentences],dtype=tf.string)[:, tf.newaxis]
    pred_probs = _model.predict(
        {
            "line_number_input": line_number_input,
            "total_line_input": total_lines_input,
            "token_input": token_input,
            "char_input": char_input,
        },
        verbose=0,
    )

    pred_classes = np.argmax(pred_probs, axis=1)
    confidences = np.max(pred_probs, axis=1)

    return [
        SentenceResult(
            sentence=sentence,
            label=_class_names[pred_class],
            confidence=float(confidence),
        )
        for sentence, pred_class, confidence in zip(sentences, pred_classes, confidences)
    ]