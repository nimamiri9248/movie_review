import pickle
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer

from src.core.db import get_manager_db
from src.core.logger import logger
from src.persistence.film import get_films


MODEL_DIR = "src/ml_models/recommendation_model"


async def build_and_save_model():
    """
    Build the recommendation model and save all components to disk.
    """
    logger.info("Starting model build process")

    # Create directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Get database session
    async with get_manager_db() as db:
        films = await get_films(db, filters=None)
        logger.info(f"Fetched {len(films)} films from database")

        # 2. Prepare data for TF-IDF
        titles = []
        combined_features = []
        film_ids = []
        title_to_id = {}

        for film in films:
            film_id = str(film.id)
            film_ids.append(film_id)

            if film.title:
                titles.append(film.title)
                title_to_id[film.title] = film_id

            # Build combined feature text
            parts = []

            # Add director if available
            if film.director:
                parts.append(film.director)

            # Add genres
            if film.genres:
                parts.extend([g.name for g in film.genres if g.name])

            # Add description if available
            if film.description:
                parts.append(film.description)

            # Join all features with spaces
            combined_features.append(" ".join(p for p in parts if p))

        # 3. Fit TF-IDF on the combined text
        logger.info("Training TF-IDF vectorizer")
        tfidf = TfidfVectorizer(stop_words="english")
        tfidf_matrix = tfidf.fit_transform(combined_features)

        # 4. Compute cosine similarity matrix
        logger.info("Computing cosine similarity matrix")
        from sklearn.metrics.pairwise import linear_kernel
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        # 5. Save all components to disk
        logger.info("Saving model components to disk")

        # Save TF-IDF vectorizer
        with open(os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
            pickle.dump(tfidf, f)

        # Save cosine similarity matrix (using numpy for efficiency)
        np.save(os.path.join(MODEL_DIR, "cosine_sim_matrix.npy"), cosine_sim)

        # Save film IDs list
        with open(os.path.join(MODEL_DIR, "film_ids.pkl"), "wb") as f:
            pickle.dump(film_ids, f)

        # Save title to ID mapping
        with open(os.path.join(MODEL_DIR, "title_to_id.pkl"), "wb") as f:
            pickle.dump(title_to_id, f)

        logger.info(f"Model building completed. Files saved to {MODEL_DIR}")
        logger.info(f"Model stats: {len(films)} films, {len(title_to_id)} unique titles")


if __name__ == "__main__":
    import asyncio
    asyncio.run(build_and_save_model())