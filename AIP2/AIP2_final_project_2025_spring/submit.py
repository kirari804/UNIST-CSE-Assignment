import pandas as pd
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader
from tqdm import tqdm

from my_model import MyModel

# 'test.csv' will replace 'val.csv' in the actual assessment.
# Therefore, in your final submission, change val.csv to test.csv
MY_STUDENT_ID = '20232006'
val_or_test_df = pd.read_csv('test.csv')
champ_df = pd.read_csv('champ.csv')


# Write your own dataloader code here.
champ_to_idx = dict(zip(champ_df['champ name'], champ_df['index']))
vectorize = np.vectorize(lambda x: champ_to_idx.get(x,x))

X_val_or_test_raw = vectorize(val_or_test_df.iloc[:,:21].values)
X_val_or_test = torch.tensor(np.delete(X_val_or_test_raw, [19], 1), dtype=torch.long)
y_val_or_test = torch.tensor(X_val_or_test_raw[:, 19], dtype=torch.long)

val_or_test_dataset = TensorDataset(X_val_or_test, y_val_or_test)
val_or_test_loader = DataLoader(val_or_test_dataset, batch_size=1)

# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('cpu')
vocab_size = len(champ_to_idx)

model = MyModel(vocab_size=vocab_size).to(device)
model.load_state_dict(torch.load('best_model.ckpt', map_location=device))
model.eval()


# Your final score will be computed in this way, using the test set.
correct = 0
total = 0

with torch.no_grad():
    for X_batch, y_batch in tqdm(val_or_test_loader, desc="Validating or testing"):
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        outputs = model(X_batch)
        preds = torch.argmax(outputs, dim=1)
        correct += (preds == y_batch).sum().item()
        total += y_batch.size(0)

print("My student ID is:", int(MY_STUDENT_ID))
print(f"Validation or test Accuracy: {correct/total:.2%} ({correct}/{total})")
