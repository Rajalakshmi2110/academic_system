import os

def download_layer1_model():
    print("Training Layer 1 DistilBERT model...")
    os.system("python src/layer1_classifier/train.py")

def setup_layer2_model():
    print("FLAN-T5 model will auto-download when first used by the pipeline.")

if __name__ == "__main__":
    download_layer1_model()
    setup_layer2_model()