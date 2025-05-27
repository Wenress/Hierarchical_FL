from torch import nn
class ModelV2(nn.Module):
    def __init__(self, input_shape: int, hidden_units: int, output_shape: int) -> None:
        super().__init__()

        # input shape: [batch_size, 1, 28, 28]
        # output shape: [batch_size, hidden_units, 14, 14]
        # No padding, so the size is reduced by 1
        # MaxPool2d reduces the size by half
        self.conv1_block = nn.Sequential(
            nn.Conv2d(in_channels=input_shape, out_channels=hidden_units, kernel_size=3, padding=1, stride=1),
            nn.ReLU(), 
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=3, padding=1, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )

        # input shape: [batch_size, hidden_units, 14, 14]
        # output shape: [batch_size, hidden_units, 7, 7]
        # No padding, so the size is reduced by 1
        # MaxPool2d reduces the size by half
        self.conv2_block = nn.Sequential(
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=3, padding=1, stride=1),
            nn.ReLU(), 
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=3, padding=1, stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2)
        )

        # input shape: [batch_size, hidden_units, 7, 7]
        # output shape: [batch_size, output_shape]
        self.linear_block = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=hidden_units*7*7, out_features=output_shape)
        )
    
    def forward(self, x):
        return self.linear_block(self.conv2_block(self.conv1_block(x)))
