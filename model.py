import torch.nn as nn
import torchvision.models as models

class ChestNet(nn.Module):
    def __init__(self, num_classes=14):
        super().__init__()

        base = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)

        # Replace classifier head
        base.classifier = nn.Linear(
            base.classifier.in_features,
            num_classes
        )

        self.model = base

    def forward(self, x):
        return self.model(x)
