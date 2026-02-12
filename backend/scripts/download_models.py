import os

def download_layer1_model():
    """Train Layer 1 DistilBERT model"""
    print("Training Layer 1 DistilBERT model...")
    os.system("python src/layer1_classifier/train.py")

if __name__ == "__main__":
    download_layer1_model()