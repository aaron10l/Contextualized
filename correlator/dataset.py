import numpy as np
from sklearn.decomposition import PCA
import torch


def onehot_task(t_i, k):
    task_rep = np.zeros(k)
    task_rep[t_i] = 1
    return task_rep


def to_pairwise(C, X, Y, task_fn=onehot_task, dtype=torch.float):
    """
    Load a pairwise (X x Y) dataset of C, T, X, Y
    """
    n, p_x = X.shape
    _, p_y = Y.shape
    N = n * p_x * p_y
    C_pairwise = np.repeat(C, p_x * p_y, axis=0)
    T_pairwise = np.zeros((N, p_x + p_y))
    X_pairwise = np.zeros(N)
    Y_pairwise = np.zeros(N)
    for n in range(N):
        t_i = (n // p_y) % p_x
        t_j = n % p_y
        m = n // (p_x * p_y)
        # k = n // (k_n * self.p ** 2)
        x_i = X[m, t_i]
        y_j = Y[m, t_j]
        X_pairwise[n] = x_i
        Y_pairwise[n] = y_j
        task_x = task_fn(t_i, p_x)
        task_y = task_fn(t_j, p_y)
        taskpair = np.concatenate((task_x, task_y))
        T_pairwise[n] = taskpair
    C_pairwise = torch.tensor(C_pairwise, dtype=dtype)
    T_pairwise = torch.tensor(T_pairwise, dtype=dtype)
    X_pairwise = torch.tensor(X_pairwise, dtype=dtype)
    Y_pairwise = torch.tensor(Y_pairwise, dtype=dtype)
    return C_pairwise, T_pairwise, X_pairwise, Y_pairwise


class Dataset:
    """
    Dataset
    """
    def __init__(self, C, X, Y, task_fn=onehot_task, seed=1, dtype=torch.float):
        self.seed = seed
        np.random.seed(self.seed)
        self.dtype = dtype
        self.task_fn = task_fn
        self.C, self.X, self.Y = C, X, Y
        self.N, self.p_x = X.shape
        _, self.p_y = Y.shape
        self.c = C.shape[-1] 
        # Train/test split
        self.train_idx = np.random.permutation(self.N)

    def load_data(self, batch_size=None, batch_start=None):
        """
        Return a batch from the test set
        batch_size = None gives the full test set
        batch_start = None gives a random subset of batch_size elements
        batch_start = i gives the elements specified by test_idx[batch_start:batch_start+batch_size]
        """
        batch_idx = None
        if batch_size is None:
            batch_idx = self.train_idx
        elif batch_start is None:
            batch_idx = np.random.choice(self.train_idx, size=batch_size, replace=False)
        else:
            if batch_start < 0:
                batch_start += self.N
            batch_end = min(self.N, batch_start + batch_size)
            batch_idx = self.train_idx[batch_start:batch_end]
        return to_pairwise(self.C[batch_idx], self.X[batch_idx], self.Y[batch_idx])
    
#     def load_data(self, batch_size=32, device=None):
#         """
#         Load batch_size samples from the training set
#         A single epoch should see training samples exactly once
#         """
#         batch_end = min(self.N, self.batch_i + batch_size)
#         batch_idx = self.train_idx[self.batch_i:batch_end]
#         if batch_end >= self.N:
#             self.batch_i = 0
#             self.epoch += 1
#         else:
#             self.batch_i += batch_size
#         C_batch, T_batch, X_batch, Y_batch = self.pairwise(self.C[batch_idx], self.X[batch_idx], self.Y[batch_idx])
#         if device is None:
#             return C_batch.detach(), T_batch.detach(), X_batch.detach(), Y_batch.detach()
#         return C_batch.to(device), T_batch.to(device), X_batch.to(device), Y_batch.to(device)

