from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

sentence1 = "I love cats"
sentence2 = "I adore kittens"
sentence3 = "The stock market crashed"

embedding1 = model.encode(sentence1)
embedding2 = model.encode(sentence2)
embedding3 = model.encode(sentence3)

print(
    "Cats vs Kittens:",
    cosine_similarity([embedding1], [embedding2])[0][0]
)

print(
    "Cats vs Stock Market:",
    cosine_similarity([embedding1], [embedding3])[0][0]
)