import torch
import torch.nn as nn
from typing import Dict, Any, Optional


class MultimodalFusionNetwork(nn.Module):
    """
    Deep Multimodal Feature Fusion Network for Civic Priority Scoring.
    Fuses Text representations + Visual CV features + Geographic/Context features.
    """

    def __init__(self, text_dim: int = 64, vision_dim: int = 16, context_dim: int = 8, hidden_dim: int = 64):
        super().__init__()
        
        # Sub-networks
        self.text_fc = nn.Sequential(
            nn.Linear(text_dim, 32),
            nn.ReLU(),
            nn.BatchNorm1d(32)
        )
        self.vision_fc = nn.Sequential(
            nn.Linear(vision_dim, 16),
            nn.ReLU(),
            nn.BatchNorm1d(16)
        )
        self.context_fc = nn.Sequential(
            nn.Linear(context_dim, 16),
            nn.ReLU(),
            nn.BatchNorm1d(16)
        )

        # Fused classifier
        fused_dim = 32 + 16 + 16
        self.fusion = nn.Sequential(
            nn.Linear(fused_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()  # Outputs 0.0 - 1.0 (multiplied by 100 for priority score)
        )

    def forward(self, text_feat: torch.Tensor, vision_feat: torch.Tensor, context_feat: torch.Tensor) -> torch.Tensor:
        t = self.text_fc(text_feat)
        v = self.vision_fc(vision_feat)
        c = self.context_fc(context_feat)
        fused = torch.cat([t, v, c], dim=-1)
        priority = self.fusion(fused) * 100.0
        return priority
