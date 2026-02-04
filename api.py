from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from PIL import Image
import torch
import torchvision.transforms as transforms
from io import BytesIO

from model import ChestNet
from auth import router as auth_router
from database import Base, engine

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB ----------------
Base.metadata.create_all(bind=engine)

# ---------------- AUTH ROUTES ----------------
app.include_router(auth_router, prefix="/auth")

# ---------------- ML MODEL ----------------
model = ChestNet()
model.load_state_dict(torch.load("global_model.pth", map_location="cpu"))
model.eval()

labels = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural_Thickening", "Hernia"
]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = torch.sigmoid(model(image))[0]

    return {
        labels[i]: round(outputs[i].item(), 4)
        for i in range(len(labels))
    }

# ---------------- SERVE REACT BUILD ----------------
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_BUILD = BASE_DIR / "build"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_BUILD / "static"),
    name="static",
)

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    return FileResponse(FRONTEND_BUILD / "index.html")
