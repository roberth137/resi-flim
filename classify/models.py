import torch
import torch.nn as nn
#import torch.optim as optim
import torch.nn.functional as F


class HistogramClassifier(nn.Module):
    def __init__(self, num_bins=120, num_classes=3):
        super(HistogramClassifier, self).__init__()
        # Example architecture: 2 hidden layers + output
        self.network = nn.Sequential(
            nn.Linear(num_bins, 64),  # from histogram bins to 64 hidden units
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        return self.network(x)


class HistogramCNN(nn.Module):
    def __init__(self, num_bins, num_classes):
        super(HistogramCNN, self).__init__()

        # Convolutional layers
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2)
        self.conv3 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2)

        # Pooling layer
        self.pool = nn.AvgPool1d(kernel_size=2, stride=2)

        # Compute the final feature size dynamically
        with torch.no_grad():
            sample_input = torch.randn(1, 1, num_bins)  # Example input with one batch, one channel
            output_features = self._get_conv_output(sample_input)

        # Fully connected layers
        self.fc1 = nn.Linear(output_features, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def _get_conv_output(self, sample_input):
        """Pass a sample input through the conv layers to determine the flattened feature size."""
        x = self.pool(F.relu(self.conv1(sample_input)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        return x.numel()  # Total number of features after flattening

    def forward(self, x):
        x = x.unsqueeze(1)  # Add channel dimension: (batch_size, 1, num_bins)

        # Convolutional layers + Activation + Pooling
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))

        # Flatten before passing to fully connected layers
        x = x.view(x.shape[0], -1)  # Flatten tensor

        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.fc2(x)  # No activation here, handled by loss function

        return x


class HistogramClassifierWithAttention(nn.Module):
    def __init__(self, num_bins=120, num_classes=3):
        super(HistogramClassifierWithAttention, self).__init__()

        # Convolutional layers to extract features
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=5, stride=1, padding=2)

        # Attention pooling layer
        self.attention_pooling = AttentionPooling(input_dim=num_bins)

        # Fully connected output layer for classification
        self.fc = nn.Linear(32, num_classes)  # Output from pooled features to num_classes

    def forward(self, x):
        # Unsqueeze if input has no channel dimension
        if len(x.shape) == 2:  # Shape (batch_size, num_bins)
            x = x.unsqueeze(1)  # Shape (batch_size, 1, num_bins)

        # Apply convolutional layers
        x = F.relu(self.conv1(x))  # Shape (batch_size, 16, num_bins)
        x = F.relu(self.conv2(x))  # Shape (batch_size, 32, num_bins)

        # Reduce 32 channels to 1 using global average pooling
        x = x.mean(dim=1)  # Shape: (batch_size, num_bins)

        # Apply attention pooling
        pooled_output, attention_scores = self.attention_pooling(x)  # Shape (batch_size,)

        # Classification
        logits = self.fc(pooled_output)  # Shape (batch_size, num_classes)

        return logits, attention_scores



class AttentionPooling(nn.Module):
    def __init__(self, input_dim):
        super(AttentionPooling, self).__init__()
        # Learnable layer to compute attention scores
        self.attention_weights = nn.Linear(input_dim, 1)  # Output 1 attention score per bin

    def forward(self, x):
        # x shape: (batch_size, num_bins)

        # Compute attention scores and normalize them using softmax
        attention_scores = torch.softmax(self.attention_weights(x).squeeze(-1), dim=1)  # (batch_size, num_bins)

        # Weighted sum of the input using the attention scores
        pooled_output = (attention_scores * x).sum(dim=1)  # (batch_size,)

        return pooled_output, attention_scores  # Return pooled output and attention scores for analysis
