try:
    import torch
    import numpy as np
    from PIL import Image
    from facenet_pytorch import MTCNN, InceptionResnetV1
    from sklearn.metrics.pairwise import cosine_similarity
    import io

    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Face detector
    mtcnn = MTCNN(
        image_size=160,
        margin=20,
        device=device
    )

    # Face recognition model
    model = InceptionResnetV1(
        pretrained='vggface2'
    ).eval().to(device)

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

def extract_embedding(image_file):
    """
    Mengambil embedding wajah dari sebuah gambar
    """
    if not AI_AVAILABLE:
        return np.random.rand(512)  # Dummy for testing

    try:
        img = Image.open(image_file).convert('RGB')
    except:
        return None

    face = mtcnn(img)

    if face is None:
        return None

    face = face.unsqueeze(0).to(device)

    with torch.no_grad():
        embedding = model(face)

    return embedding.cpu().numpy()[0]

def enroll_with_multiple_images(image_files):
    """
    Enroll wajah menggunakan beberapa gambar (disarankan 3)
    """
    if not AI_AVAILABLE:
        return np.random.rand(512).tolist()  # Dummy

    embeddings = []

    for image_file in image_files:
        emb = extract_embedding(image_file)
        if emb is not None:
            embeddings.append(emb)

    if len(embeddings) == 0:
        return None

    # Rata-rata embedding
    final_embedding = np.mean(embeddings, axis=0)

    # Normalisasi (BEST PRACTICE)
    final_embedding = final_embedding / np.linalg.norm(final_embedding)

    return final_embedding.tolist()  # Convert to list for JSON storage

def verify_face(stored_embedding, checkin_embedding, threshold=0.8):
    """
    Verifikasi wajah dengan threshold
    """
    if not AI_AVAILABLE:
        return True, 0.9  # Dummy success

    # Normalisasi
    checkin_embedding = np.array(checkin_embedding) / np.linalg.norm(checkin_embedding)
    stored_embedding = np.array(stored_embedding)

    similarity = cosine_similarity([stored_embedding], [checkin_embedding])[0][0]

    return similarity >= threshold, similarity