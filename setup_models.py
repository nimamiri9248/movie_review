from src.ml_models.build_recommendation_model import build_and_save_model

if __name__ == "__main__":
    import asyncio
    asyncio.run(build_and_save_model())