# Go-UMKM Recommendation System


## Features

- Content-based recommendation using TensorFlow(Keras) embeddings
- FastAPI for serving recommendations
- Modular and containerized architecture


### 1. Persiapan Awal
```bash
cd go-umkm-recommender

# Buat environment
```bash
conda create --name go-umkm python=3.9
conda activate go-umkm

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment Variables untuk Akses Database
Isi `.env` di root folder dengan ini:
```
DB_HOST=go-umkm.c9e8y4qwgzqq.ap-southeast-1.rds.amazonaws.com
DB_PORT=*****
DB_USER=remote_user_go_umkm
DB_PASSWORD=capstone_project
DB_NAME=go_umkm
```

### 3. Eksekusi Secara Berurutan

#### Langkah 1: Training Model
Jalankan script training:
```bash
python -m src.models.train
```

**Apa yang terjadi**:
1. Program akan:
   - Membaca data dari database
   - Melakukan preprocessing
   - Melatih model similarity
   - Menyimpan artifacts di folder `artifacts/`

**Verifikasi sukses**:
- Cek folder `artifacts` harus berisi:
  ```
  preprocessor.joblib
  similarity_model.h5
  ```

#### Langkah 2: Jalankan API
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```
```

**Verifikasi**:
1. Buka `http://localhost:8000/health` di browser, harus dapat response:
   ```json
   {"status":"healthy","model_loaded":true}
   ```
2. Untuk test endpoint rekomendasi:
```bash
   python test-api.py
```
harus dapat response:
{  
   "user_id_1",
   "user_id_2,
    # ...
}

## Deployment (Sedang dalam proses)

1. Build the Docker image:
   ```bash
   docker build -t go-umkm-recommender .        


