#####################################################
### Benchmark code for class final project: AIP 2 ###
### Credit: BYEONGHUN PARK                        ###
### Year 2025                                     ###
#####################################################

import time

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import torch.optim as optim
from hypergrad import SGDHD, AdamHD
from sklearn.model_selection import train_test_split


class MyModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=128, num_classes=5):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim) 
        self.pos = nn.Embedding(5, embed_dim)
        self.lstm = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)
        self.pos_ids = torch.tensor([0,1,2,3,4,0,1,2,4], dtype=torch.long)

    def forward(self, x):
        embedded = self.embedding(x)  # (B, 9, embed_dim)
        # pos_ids = self.pos_ids.unsqueeze(0).expand(x.size(0), -1)   
        pos_ids = self.pos_ids.to(x.device).unsqueeze(0).expand(x.size(0), -1)
        # pos_emb = self.pos(pos_ids)
        # embedded = embedded + pos_emb
        _, (h) = self.lstm(embedded)  # h: (1, B, hidden_dim)
        h = h.squeeze(0)  # (B, hidden_dim)

        output = self.fc(h)
        # output = self.fc(h.squeeze(0))  # (B, num_classes)
        return output


'''
out, (h_n, c_n) = self.lstm(input)

out:
A tensor containing the hidden state for every time step in the sequence.
Shape: (batch_size, sequence_length, hidden_dim) if batch_first=True.

h_n (hidden state):
The last hidden state of the sequence (i.e., the final time step).
Shape: (num_layers * num_directions, batch_size, hidden_dim)

c_n (cell state):
The last cell state from the LSTM, representing internal memory.
Shape: same as h_n
''', 

if __name__ == "__main__":

    # (1) Load data
    train_df = pd.read_csv('train.csv')
    champ_df = pd.read_csv('champ.csv')

    champ_to_idx = dict(zip(champ_df['champ name'], champ_df['index']))
    vectorize = np.vectorize(lambda x: champ_to_idx.get(x, x))

    # (2) Make dataset
    train_df, val_df = train_test_split(train_df, test_size=0.05, random_state=42)

    X_train_raw = vectorize(train_df.iloc[:,:21].values)
    X_val_raw = vectorize(val_df.iloc[:,:21].values)

    X_train = torch.tensor(np.delete(X_train_raw, [19], 1), dtype=torch.long)
    y_train = torch.tensor(X_train_raw[:, 19], dtype=torch.long)

    # from sklearn.decomposition import PCA
    # pos = PCA(2).fit_transform(np.delete(X_train_raw, [19], 1)[:3000,5:10])
    # x = pos[:,0]
    # y = pos[:,1]
    # colors = "green", "red", "purple", "blue", "gray"
    # c = [colors[i] for i in X_train_raw[:3000,19]]
    # from matplotlib import pyplot
    # pyplot.scatter(x,y,c=c)
    # pyplot.show()

    X_val = torch.tensor(np.delete(X_val_raw, [19], 1), dtype=torch.long)
    y_val = torch.tensor(X_val_raw[:, 19], dtype=torch.long)

    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)


    # (3) Hyperparameters
    batch_size = 400
    eval_iter = 1
    epochs = 30
    vocab_size = len(champ_to_idx)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    # (4) DataLoader
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,       
        pin_memory=True 
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        pin_memory=True
    )

    # (5) Model, Optimizer, Loss function
    model = MyModel(vocab_size=vocab_size).to(device)
    # optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    optimizer = SGDHD(model.parameters(), lr=1e-3, hypergrad_lr=1e-8)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    best_val_loss = float('inf')

    total_time = time.time()

    for epoch in range(epochs):
        start_time = time.time()
        model.train() # train mode
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device, non_blocking=True), y_batch.to(device, non_blocking=True)
            pred = model(X_batch)
            loss = criterion(pred, y_batch)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        elapsed = (time.time() - start_time) 
        
        if epoch % eval_iter == 0:
            model.eval() # eval mode
            total_loss = 0
            correct = 0
            total = 0
            rand_correct = 0
            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    X_batch, y_batch = X_batch.to(device, non_blocking=True), y_batch.to(device, non_blocking=True)
                    pred = model(X_batch)
                    total_loss += criterion(pred, y_batch).item()
                    
                    predicted = torch.argmax(pred, dim=1)
                    correct += (predicted == y_batch).sum().item()
                    total += y_batch.size(0)

                    rand_correct += (0 == y_batch).sum().item()
              

            avg_val_loss = total_loss / len(val_loader)
            accuracy = correct / total * 100
            print(f"[Eval iter {epoch}] : Val Loss: {avg_val_loss:.4f} | Val Acc: {accuracy:.2f}%")
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                torch.save(model.state_dict(), "best_model.ckpt")
                print("Model updated")
        # else:
        if True:
            print(f"[Train iter {epoch}] : Train Loss: {loss.item():.4f} | Time: {elapsed:.2f} sec")
            print(f"Total time : {(time.time() - total_time)/60:.2f} min")

        

