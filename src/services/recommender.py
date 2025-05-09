import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional

from src.core.logger import logger

MODEL_DIR = "src/ml_models/recommendation_model"

# Type annotations for global variables
_cosine_sim: Optional[np.ndarray] = None
_film_ids: Optional[List[str]] = None
_title_to_id: Optional[Dict[str, str]] = None
_id_to_idx: Optional[Dict[str, int]] = None
_model_loaded: bool = False


def load_recommendation_model() -> bool:
    """
    Load the pre-computed recommendation model from disk.
    Call this during app startup.

    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global _cosine_sim, _film_ids, _title_to_id, _id_to_idx, _model_loaded

    try:
        # Check if model files exist
        required_files = [
            "cosine_sim_matrix.npy",
            "film_ids.pkl",
            "title_to_id.pkl"
        ]

        for file in required_files:
            if not os.path.exists(os.path.join(MODEL_DIR, file)):
                logger.error(f"Missing model file: {file}")
                return False

        # Load cosine similarity matrix
        # _cosine_sim = np.load(os.path.join(MODEL_DIR, "cosine_sim_matrix.npy"))
        _cosine_sim = np.load(
            os.path.join(MODEL_DIR, "cosine_sim_matrix.npy"),
            mmap_mode="r"
        )
        # Load film IDs
        with open(os.path.join(MODEL_DIR, "film_ids.pkl"), "rb") as f:
            _film_ids = pickle.load(f)

        # Load title to ID mapping
        with open(os.path.join(MODEL_DIR, "title_to_id.pkl"), "rb") as f:
            _title_to_id = pickle.load(f)

        # Create film ID to index mapping
        _id_to_idx = {film_id: idx for idx, film_id in enumerate(_film_ids)}

        _model_loaded = True
        logger.info(f"Recommendation model loaded with {len(_film_ids)} films")
        return True

    except Exception as e:
        logger.error(f"Failed to load recommendation model: {str(e)}")
        _model_loaded = False
        return False


def get_similar_movies(title_or_id: str, top_n: int = 5) -> List[str]:
    """
    Return the top_n film IDs most similar to the given title or film ID,
    or an empty list if not found or model not loaded.

    Args:
        title_or_id: Film title or ID to find similar films for
        top_n: Number of similar films to return

    Returns:
        List of film IDs similar to the given film
    """
    if not _model_loaded or _cosine_sim is None or _film_ids is None or _title_to_id is None or _id_to_idx is None:
        logger.warning("Recommendation model not loaded or incomplete")
        return []

    try:
        # Determine if input is a title or ID
        film_id = title_or_id

        # If it's a title, convert to ID
        if title_or_id in _title_to_id:
            film_id = _title_to_id[title_or_id]

        # Get the index for this film ID
        idx = _id_to_idx.get(film_id)
        if idx is None:
            logger.info(f"No film found with title or ID: {title_or_id}")
            return []

        # Get similarity scores
        sim_scores = list(enumerate(_cosine_sim[idx]))

        # Sort by similarity descending
        sim_scores.sort(key=lambda x: x[1], reverse=True)

        # Skip itself (first result) and pick the next top_n
        sim_scores_sliced = sim_scores[1:top_n + 1]
        top_idxs = [i for i, _ in sim_scores_sliced]

        # Map back to film IDs
        return [_film_ids[i] for i in top_idxs]

    except Exception as e:
        logger.error(f"Error getting similar movies: {str(e)}")
        return []


def get_model_stats() -> Dict[str, Any]:
    """
    Return statistics about the recommendation model.

    Returns:
        Dictionary with model statistics
    """
    if not _model_loaded:
        return {"loaded": False}

    return {
        "loaded": True,
        "film_count": len(_film_ids) if _film_ids is not None else 0,
        "unique_titles": len(_title_to_id) if _title_to_id is not None else 0,
        "matrix_shape": _cosine_sim.shape if _cosine_sim is not None else None
    }