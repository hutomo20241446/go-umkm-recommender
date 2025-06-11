from fastapi import FastAPI, HTTPException
import tensorflow as tf
import numpy as np
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict
from src.data.database import DatabaseConnector
from src.data.preprocessing import DataPreprocessor
from src.models.similarity_model import SimilarityModel
from .schemas import RecommendationRequest, RecommendationResponse
from .config import settings  # Perubahan import

app = FastAPI(title="Go-UMKM Recommendation API")

# Load artifacts at startup
artifacts_path = Path("artifacts")
preprocessor = None
model = None
users_df = None
umkm_df = None
investor_df = None
similarity_matrix = None

@app.on_event("startup")
async def load_artifacts():
    global preprocessor, model, users_df, umkm_df, investor_df, similarity_matrix
    
    try:
        # Load preprocessor
        if (artifacts_path / "preprocessor.joblib").exists():
            preprocessor = joblib.load(artifacts_path / "preprocessor.joblib")
        
        # Load model
        if (artifacts_path / "similarity_model.h5").exists():
            model = tf.keras.models.load_model(artifacts_path / "similarity_model.h5")
        
        # Load and preprocess data
        db_connector = DatabaseConnector()
        data_processor = DataPreprocessor()
        
        data = db_connector.load_required_tables()
        merged_data = data_processor.merge_dataframes(data)
        umkm_df = merged_data['umkm']
        investor_df = merged_data['investor']
        
        # Create combined users dataframe
        umkm_clean = umkm_df.drop(columns=['umkm_id'])
        investor_clean = investor_df.drop(columns=['investor_id'])
        users_df = pd.concat([umkm_clean, investor_clean], ignore_index=True)
        
        # Generate embeddings and similarity matrix
        if model and preprocessor:
            features = preprocessor.transform(users_df)
            features_dense = features.toarray() if hasattr(features, 'toarray') else features
            embeddings = model.predict(features_dense)
            normalized_embeddings = tf.math.l2_normalize(embeddings, axis=1)
            similarity_matrix = tf.linalg.matmul(normalized_embeddings, normalized_embeddings, transpose_b=True)
        
    except Exception as e:
        print(f"Error loading artifacts: {e}")
    finally:
        if 'db_connector' in locals():
            db_connector.close()

def get_profile_type(user_id: str) -> str:
    """Check if user is UMKM or Investor"""
    if user_id in umkm_df['user_id'].values:
        return 'umkm'
    elif user_id in investor_df['user_id'].values:
        return 'investor'
    else:
        raise ValueError(f"User ID {user_id} not found")

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    try:
        # Validate user exists
        user_type = get_profile_type(request.user_id)
        
        # Get user index
        idx = users_df.index[users_df['user_id'] == request.user_id].tolist()[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(similarity_matrix[idx].numpy()))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:request.top_k+1]
        
        # Get recommended user IDs
        user_indices = [i[0] for i in sim_scores]
        recommended_user_ids = users_df.iloc[user_indices]['user_id'].tolist()
        
        # Filter based on user type
        if user_type == 'umkm':
            recommended_ids = investor_df[investor_df['user_id'].isin(recommended_user_ids)]['investor_id'].tolist()
        else:
            recommended_ids = umkm_df[umkm_df['user_id'].isin(recommended_user_ids)]['umkm_id'].tolist()
        
        return RecommendationResponse(
            recommendations=recommended_ids
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}