from __future__ import absolute_import, division, print_function

import logging
import os
import json
import numpy as np

import torch

from forge.ml import losses
from forge.ml.models import ParameterizedRatioEstimator, DoublyParameterizedRatioEstimator
from forge.ml.trainer import train_model, evaluate_model
from forge.ml.utils import create_missing_folders, load_and_check, general_init


class Forge:

    def __init__(self, debug=False):
        general_init(debug=debug)

        self.method_type = None
        self.model = None
        self.method = None
        self.n_observables = None
        self.n_parameters = None
        self.n_hidden = None
        self.activation = None

    def train(self,
              method,
              x_filename,
              y_filename,
              theta0_filename,
              theta1_filename=None,
              r_xz_filename=None,
              t_xz0_filename=None,
              t_xz1_filename=None,
              n_hidden=(100, 100, 100),
              activation='tanh',
              alpha=1.,
              n_epochs=20,
              batch_size=64,
              initial_lr=0.001,
              final_lr=0.0001,
              validation_split=0.2,
              early_stopping=True):

        """ Trains likelihood ratio estimator """

        logging.info('Starting training')
        logging.info('  Method:                 %s', method)
        logging.info('  Training data: theta0 at %s', theta0_filename)
        if theta1_filename is not None:
            logging.info('                 theta1 at %s', theta1_filename)
        logging.info('                 x at %s', x_filename)
        logging.info('                 y at %s', y_filename)
        if r_xz_filename is not None:
            logging.info('                 r_xz at %s', r_xz_filename)
        if t_xz0_filename is not None:
            logging.info('                 t_xz (theta0) at  %s', t_xz0_filename)
        if t_xz1_filename is not None:
            logging.info('                 t_xz (theta1) at  %s', t_xz1_filename)
        logging.info('  Method:                 %s', method)
        logging.info('  Hidden layers:          %s', n_hidden)
        logging.info('  Activation function:    %s', activation)
        logging.info('  alpha:                  %s', alpha)
        logging.info('  Batch size:             %s', batch_size)
        logging.info('  Epochs:                 %s', n_epochs)
        logging.info('  Learning rate:          %s initially, decaying to %s', initial_lr, final_lr)
        logging.info('  Early stopping:         %s', early_stopping)

        # Load training data
        logging.info('Loading training data')

        theta0 = load_and_check(theta0_filename)
        theta1 = load_and_check(theta1_filename)
        x = load_and_check(x_filename)
        y = load_and_check(y_filename).reshape((-1, 1))
        r_xz = load_and_check(r_xz_filename)
        t_xz0 = load_and_check(t_xz0_filename)
        t_xz1 = load_and_check(t_xz1_filename)

        # Check necessary information is theere
        assert theta0 is not None
        assert x is not None
        assert y is not None
        if method in ['rolr', 'alice', 'rascal', 'alices', 'rolr2', 'alice2', 'rascal2', 'alices2']:
            assert r_xz is not None
        if method in ['rascal', 'alices', 'rascal2', 'alices2']:
            assert t_xz0 is not None
        if method in ['carl2', 'rolr2', 'alice2', 'rascal2', 'alices2']:
            assert theta1 is not None
        if method in ['rascal2', 'alices2']:
            assert t_xz1 is not None

        n_samples = theta0.shape[0]
        n_parameters = theta0.shape[1]
        n_observables = x.shape[1]

        logging.info('Found %s samples with %s parameters and %s observables', n_samples, n_parameters, n_observables)

        # Save setup
        self.method = method
        self.n_observables = n_observables
        self.n_parameters = n_parameters
        self.n_hidden = n_hidden
        self.activation = activation

        # Create model
        logging.info('Creating model for method %s', method)
        if method in ['carl', 'rolr', 'rascal', 'alice', 'alices']:
            self.method_type = 'parameterized'
            self.model = ParameterizedRatioEstimator(
                n_observables=n_observables,
                n_parameters=n_parameters,
                n_hidden=n_hidden,
                activation=activation
            )
        elif method in ['carl2', 'rolr2', 'rascal2', 'alice2', 'alices2']:
            self.method_type = 'doubly_parameterized'
            self.model = DoublyParameterizedRatioEstimator(
                n_observables=n_observables,
                n_parameters=n_parameters,
                n_hidden=n_hidden,
                activation=activation
            )
        else:
            raise NotImplementedError('Unknown method {}'.format(method))

        # Loss fn
        if method in ['carl', 'carl2']:
            loss_functions = [losses.standard_cross_entropy]
            loss_weights = [1.]
            loss_labels = ['xe']

        elif method in ['rolr', 'rolr2']:
            loss_functions = [losses.ratio_mse]
            loss_weights = [1.]
            loss_labels = ['mse_r']

        elif method == 'rascal':
            loss_functions = [losses.ratio_mse, losses.score_mse_num]
            loss_weights = [1., alpha]
            loss_labels = ['mse_r', 'mse_score']

        elif method == 'rascal2':
            loss_functions = [losses.ratio_mse, losses.score_mse]
            loss_weights = [1., alpha]
            loss_labels = ['mse_r', 'mse_score']

        elif method in ['alice', 'alice2']:
            loss_functions = [losses.augmented_cross_entropy]
            loss_weights = [1.]
            loss_labels = ['improved_xe']

        elif method == 'alices':
            loss_functions = [losses.augmented_cross_entropy, losses.score_mse_num]
            loss_weights = [1., alpha]
            loss_labels = ['improved_xe', 'mse_score']

        elif method == 'alices2':
            loss_functions = [losses.augmented_cross_entropy, losses.score_mse]
            loss_weights = [1., alpha]
            loss_labels = ['improved_xe', 'mse_score']

        else:
            raise NotImplementedError('Unknown method {}'.format(method))

        # Train model
        logging.info('Training model')

        train_model(
            model=self.model,
            method_type=self.method_type,
            loss_functions=loss_functions,
            loss_weights=loss_weights,
            loss_labels=loss_labels,
            theta0s=theta0,
            theta1s=theta1,
            xs=x,
            ys=y,
            r_xzs=r_xz,
            t_xz0s=t_xz0,
            t_xz1s=t_xz1,
            batch_size=batch_size,
            n_epochs=n_epochs,
            initial_learning_rate=initial_lr,
            final_learning_rate=final_lr,
            validation_split=validation_split,
            early_stopping=early_stopping
        )

    def evaluate(self,
                 x_filename,
                 theta0_filename,
                 theta1_filename=None,
                 test_all_combinations=True):

        """ Predicts log likelihood ratio for all combinations of theta and x """

        if self.model is None:
            raise ValueError('No model -- train or load model before evaluating it!')

        # Load training data
        logging.info('Loading evaluation data')

        theta0s = load_and_check(theta0_filename)
        theta1s = load_and_check(theta1_filename)
        xs = load_and_check(x_filename)

        # Balance thetas
        if theta1s is None:
            theta1s = [None for _ in theta0s]
        else:
            if len(theta1s) > len(theta0s):
                theta0s = [theta0s[i % len(theta0s)] for i in range(len(theta1s))]
            elif len(theta1s) < len(theta0s):
                theta1s = [theta1s[i % len(theta1s)] for i in range(len(theta0s))]

        # Loop over thetas
        all_log_r_hat = []
        all_t_hat0 = []
        all_t_hat1 = []

        if test_all_combinations:
            for i, (theta0, theta1) in enumerate(zip(theta0s, theta1s)):
                logging.debug('Starting evaluation for thetas %s / %s: %s vs %s',
                              i + 1, len(theta0s), theta0, theta1)

                _, log_r_hat, t_hat0, t_hat1 = evaluate_model(
                    model=self.model,
                    method_type=self.method_type,
                    theta0s=[theta0],
                    theta1s=[theta1] if theta1 is not None else None,
                    xs=xs
                )

                all_log_r_hat.append(log_r_hat)
                all_t_hat0.append(t_hat0)
                all_t_hat1.append(t_hat1)
        else:
            logging.debug('Starting evaluation for all thetas')

            _, log_r_hat, t_hat0, t_hat1 = evaluate_model(
                model=self.model,
                method_type=self.method_type,
                theta0s=theta0s,
                theta1s=None if None in theta1s else theta1s,
                xs=xs
            )

            all_log_r_hat.append(log_r_hat)
            all_t_hat0.append(t_hat0)
            all_t_hat1.append(t_hat1)

        # Return
        all_log_r_hat = np.array(all_log_r_hat)
        all_t_hat0 = np.array(all_t_hat0)
        all_t_hat1 = np.array(all_t_hat1)

        return all_log_r_hat, all_t_hat0, all_t_hat1

    def save(self,
             filename):

        """ Saves model state dict """

        if self.model is None:
            raise ValueError('No model -- train or load model before saving!')

        # Check paths
        create_missing_folders([os.path.dirname(filename)])

        # Save settings
        logging.info('Saving settings to %s_settings.json', filename)

        settings = {'method': self.method,
                    'method_type': self.method_type,
                    'n_observables': self.n_observables,
                    'n_parameters': self.n_parameters,
                    'n_hidden': list(self.n_hidden),
                    'activation': self.activation}

        with open(filename + '_settings.json', 'w') as f:
            json.dump(settings, f)

        # Save state dict
        logging.info('Saving state dictionary to %s_state_dict.pt', filename)
        torch.save(self.model.state_dict(), filename + '_state_dict.pt')

    def load(self,
             filename):

        """ Loads model state dict from file """

        # Load settings
        logging.info('Loading settings from %s_settings.json', filename)

        with open(filename + '_settings.json', 'r') as f:
            settings = json.load(f)

        self.method = settings['method']
        self.method_type = settings['method_type']
        self.n_observables = int(settings['n_observables'])
        self.n_parameters = int(settings['n_parameters'])
        self.n_hidden = tuple([int(item) for item in settings['n_hidden']])
        self.activation = str(settings['activation'])

        # Create model
        if self.method in ['carl', 'rolr', 'rascal', 'alice', 'alices']:
            assert self.method_type == 'parameterized'
            self.model = ParameterizedRatioEstimator(
                n_observables=self.n_observables,
                n_parameters=self.n_parameters,
                n_hidden=self.n_hidden,
                activation=self.activation
            )
        elif self.method in ['carl2', 'rolr2', 'rascal2', 'alice2', 'alices2']:
            assert self.method_type == 'doubly_parameterized'
            self.model = DoublyParameterizedRatioEstimator(
                n_observables=self.n_observables,
                n_parameters=self.n_parameters,
                n_hidden=self.n_hidden,
                activation=self.activation
            )
        else:
            raise NotImplementedError('Unknown method {}'.format(self.method))

        # Load state dict
        logging.info('Loading state dictionary from %s_state_dict.pt', filename)
        self.model.load_state_dict(torch.load(filename + '_state_dict.pt'))