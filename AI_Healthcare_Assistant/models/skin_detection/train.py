import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# 📁 Exact folder path mapping matching your workspace tree
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "skin_disease")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
TEST_DIR = os.path.join(DATASET_DIR, "test")

OUTPUT_DIR = os.path.join(BASE_DIR, "models", "skin_detection")
MODEL_SAVE_PATH = os.path.join(OUTPUT_DIR, "mobilenet_skin.pt")

# 🎛️ Optimization Parametrics
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001
NUM_CLASSES = 19  # 🟢 FIXED: Updated from 20 to 19 to match your actual folders!

def train_skin_model():
    print("🚀 Initializing Dermatology Deep Learning Pipeline...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"💻 Utilizing execution hardware: {device}")

    # 🔄 Image Transforms and Data Augmentation
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 📥 Load Datasets via Automated Directory Parsing
    if not os.path.exists(TRAIN_DIR):
        raise FileNotFoundError(f"❌ Missing train directory path at: {TRAIN_DIR}")

    print(f"📦 Loading training assets from: {TRAIN_DIR}")
    train_dataset = datasets.ImageFolder(root=TRAIN_DIR, transform=train_transform)
    test_dataset = datasets.ImageFolder(root=TEST_DIR, transform=test_transform)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2, drop_last=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    # 🕸️ Initialize MobileNetV3 Large
    print("📥 Loading pre-trained MobileNetV3 Backbone weights...")
    model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)

    # Instead of freezing EVERYTHING, we unfreeze the final extraction block 
    # so the model can learn specific dermatology patterns (textures, spots, rashes).
    for param in model.features.parameters():
        param.requires_grad = False
        
    # Unfreeze the last two layers of the feature extractor for medical specialization
    for param in model.features[-2:].parameters():
        param.requires_grad = True

    # Modify the classification layer with structural regularization to combat overfitting
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),       # Normalizes activations to stabilize learning
        nn.ReLU(),
        nn.Dropout(0.5),           # Increased from 0.3 to 0.5 to penalize memorization
        nn.Linear(512, NUM_CLASSES)
    )
    
    model = model.to(device)
    model = model.to(device)

    # ⚖️ Loss & Optimization Framework
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)

    print("\n🏁 Commencing Model Fine-Tuning Execution...")
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)

        epoch_loss = running_loss / len(train_loader.dataset)

        # 🧪 Evaluation Validation Step
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs, dim=1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        epoch_acc = (correct / total) * 100
        print(f"Epoch [{epoch+1}/{EPOCHS}] -> Training Cross-Entropy Loss: {epoch_loss:.4f} | Validation Accuracy: {epoch_acc:.2f}%")

    # 💾 Save Weights Matrix to Disk
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"\n[🟢] Model Weights Successfully Serialized -> {MODEL_SAVE_PATH}")

    # 📝 Save the dynamic class list mapping file
    labels_file_path = os.path.join(OUTPUT_DIR, "classes.txt")
    with open(labels_file_path, "w") as f:
        for cls_name in train_dataset.classes:
            f.write(f"{cls_name}\n")
    print(f"[📝] Class labels dictionary generated at -> {labels_file_path}")

if __name__ == "__main__":
    train_skin_model()