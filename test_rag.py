import chromadb
from chromadb.utils import embedding_functions

# 1. Inisialisasi ChromaDB (simpan di folder ./chroma_db)
client = chromadb.PersistentClient(path="./chroma_db")

# 2. Buat  "koleksi" (seperti tabel di SQL)
collection = client.get_or_create_collection(name="batch_knowledge")

# 3. Data contoh ( data dari database )
data_batch = [
    {"id": "1", "teks": "Batch B001 reject 5 unit karena kemasan penyok."},
    {"id": "2", "teks": "Batch B002 reject 50 unit karena warna tidak sesuai standar."},
    {"id": "3", "teks": "Batch B003 reject 2 unit karena kesalahan label."},
    {"id": "4", "teks": "Batch B004 reject 30 unit karena mesin overheat."},
    {"id": "5", "teks": "Batch B005 reject 1 unit karena operator salah input."},
]

# 4. Masukkan ke Vector DB
collection.add(
    ids=[d["id"] for d in data_batch],
    documents=[d["teks"] for d in data_batch]
)

print("Data berhasil disimpan ke Vector Database!")
print(f"Total data: {collection.count()}")

# 5. Cari data berdasarkan makna (Retrieval)
print("\n--- MENCARI: 'wadahnya rusak' ---")

hasil = collection.query(
    query_texts=["wadahnya rusak"],  
    n_results=2                      
)

for i in range(len(hasil["documents"][0])):
    print(f"Data {i+1}: {hasil['documents'][0][i]}")
    print(f"Jarak kemiripan: {hasil['distances'][0][i]}")