import os

def download_layer1_model():
    """Train or download Layer 1 DistilBERT model"""
    print("Training Layer 1 DistilBERT model...")
    os.system("python src/layer1_classifier/train.py")

def setup_layer2_model():
    """Layer 2 FLAN-T5 auto-download from Hugging Face"""
    print("FLAN-T5 model will auto-download when first used by the pipeline.")

if __name__ == "__main__":
    download_layer1_model()
    setup_layer2_model()