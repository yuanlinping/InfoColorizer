from argparse import ArgumentParser
from copy import deepcopy
from importlib import import_module
from math import ceil
# from os.path import exists, join
import os
from sys import stderr
import warnings

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from .datasets import compute_normalization
from .imputation_networks import get_imputation_networks
from .train_utils import extend_batch, get_validation_iwae
from .VAEAC import VAEAC

warnings.filterwarnings("ignore", category=UserWarning)

num_imputations = 10
one_hot_max_sizes = [1, 1, 1, 1, 1, 1, 1, 112, 1, 1, 1, 1, 1, 1, 1, 2, 61, 1, 1, 1, 1, 1, 1, 1, 4, 41, 1, 1, 1, 1, 1, 1, 1, 6, 27, 1, 1, 1, 1, 1, 1, 1, 8, 35, 1, 1, 1, 1, 1, 1, 1, 10, 47, 1, 1, 1, 1, 1, 1, 1, 12, 111, 1, 1, 1, 1, 1, 1, 1, 14, 110, 1, 1, 1, 1, 1, 1, 1, 16, 37, 1, 1, 1, 1, 1, 1, 1, 18, 31, 1, 1, 1, 1, 1, 1, 1, 20, 67, 1, 1, 1, 1, 1, 1, 1, 22, 29, 1, 1, 1, 1, 1, 1, 1, 24, 37, 1, 1, 1, 1, 1, 1, 1, 26, 39, 1, 1, 1, 1, 1, 1, 1, 28, 49, 1, 1, 1, 1, 1, 1, 1, 30, 59, 1, 1, 1, 1, 1, 1, 1, 32, 59, 1, 1, 1, 1, 1, 1, 1, 34, 47, 1, 1, 1, 1, 1, 1, 1]
model_name = "trained_vaeac_model"
def impute(imputed_data):
    input_size = len(imputed_data)
    # Read and normalize input data
    dirname = os.path.dirname(__file__)

    load_data = np.loadtxt(os.path.join(dirname, 'training_groundtruth.tsv'), delimiter='\t')
    raw_data = np.concatenate((imputed_data, load_data), axis=0)
    raw_data = torch.from_numpy(raw_data).float()
    norm_mean, norm_std = compute_normalization(raw_data, one_hot_max_sizes)
    norm_std = torch.max(norm_std, torch.tensor(1e-9))
    data = (raw_data - norm_mean[None]) / norm_std[None]

    verbose = True
    # Non-zero number of workers cause nasty warnings because of some bug in
    # multiprocess library. It might be fixed now, but anyway there is no need
    # to have a lot of workers for dataloader over in-memory tabular data.
    num_workers = 0

    # design all necessary networks and learning parameters for the dataset
    networks = get_imputation_networks(one_hot_max_sizes)

    # build VAEAC on top of returned network, optimizer on top of VAEAC,
    # extract optimization parameters and mask generator
    model = VAEAC(
        networks['reconstruction_log_prob'],
        networks['proposal_network'],
        networks['prior_network'],
        networks['generative_network']
    )
    optimizer = networks['optimizer'](model.parameters())
    batch_size = networks['batch_size']
    mask_generator = networks['mask_generator']
    vlb_scale_factor = networks.get('vlb_scale_factor', 1)

    checkpoint = torch.load(os.path.join(dirname, model_name))

    model.load_state_dict(checkpoint['model_state_dict'])

    # build dataloader for the whole input data
    dataloader = DataLoader(data, batch_size=batch_size,
                            shuffle=False, num_workers=num_workers,
                            drop_last=False)


    # prepare the store for the imputations
    results = []
    for i in range(num_imputations):
        results.append([])

    iterator = dataloader
    if verbose:
        iterator = tqdm(iterator)

    # impute missing values for all input data
    for batch in iterator:

        # if batch size is less than batch_size, extend it with objects
        # from the beginning of the dataset
        batch_extended = torch.tensor(batch)
        batch_extended = extend_batch(batch_extended, dataloader, batch_size)

        # compute the imputation mask
        mask_extended = torch.isnan(batch_extended).float()

        # compute imputation distributions parameters
        with torch.no_grad():
            samples_params = model.generate_samples_params(batch_extended,
                                                        mask_extended,
                                                        num_imputations)
            samples_params = samples_params[:batch.shape[0]]

        # make a copy of batch with zeroed missing values
        mask = torch.isnan(batch)
        batch_zeroed_nans = torch.tensor(batch)
        batch_zeroed_nans[mask] = 0

        # impute samples from the generative distributions into the data
        # and save it to the results
        for i in range(num_imputations):
            sample_params = samples_params[:, i]
            sample = networks['sampler'](sample_params)
            sample[(~mask).byte()] = 0
            sample += batch_zeroed_nans
            results[i].append(torch.tensor(sample, device='cpu'))

    # concatenate all batches into one [n x K x D] tensor,
    # where n in the number of objects, K is the number of imputations
    # and D is the dimensionality of one object
    for i in range(len(results)):
        results[i] = torch.cat(results[i]).unsqueeze(1)
    result = torch.cat(results, 1)

    # reshape result, undo normalization and save it
    result = result.view(result.shape[0] * result.shape[1], result.shape[2])
    result = result * norm_std[None] + norm_mean[None]

    part_imputations = result[0:num_imputations*input_size]

    return part_imputations.numpy()

