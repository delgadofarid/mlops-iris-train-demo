import json
import logging
import os
import sys
import traceback

from mlops_iris_train_demo.iris_train import model

# This directory is the communication channel between Sagemaker and your container
from typing import Dict, Any

_logger = logging.getLogger(__name__)

_DEFAULT_SM_DIR_PREFIX = '/opt/ml'

# Here, Sagemaker will store the dataset copyied from S3
DEFAULT_TRAINING_PATH = os.path.join(_DEFAULT_SM_DIR_PREFIX, 'input/data/training')
# If something bad happens, write a failure file with the error messages and store here
DEFAULT_OUTPUT_PATH = os.path.join(_DEFAULT_SM_DIR_PREFIX, 'output')
# Everything you store here will be packed into a .tar.gz by Sagemaker and store into S3
DEFAULT_MODEL_PATH = os.path.join(_DEFAULT_SM_DIR_PREFIX, 'model')
# These are the hyperparameters you will send to your algorithms through the Estimator
DEFAULT_PARAM_PATH = os.path.join(_DEFAULT_SM_DIR_PREFIX, 'input/config/hyperparameters.json')


class IrisTrain(object):

    def __init__(self, args: Dict[str, str]):
        self.train_data_path = args["train_data_dir"] if "train_data_dir" in args else DEFAULT_TRAINING_PATH
        self.model_path = args["model_dir"] if "model_dir" in args else DEFAULT_MODEL_PATH
        self.output_path = args["output_dir"] if "output_dir" in args else DEFAULT_OUTPUT_PATH
        # fill training parameters
        self.params = {}
        self.params = self._populate_hyperparameters(self.params)
        if args is not None:
            self.params.update(args)

    def run(self):
        try:
            clf = model.train(self.train_data_path, hyperparameters=self.params)
            model.save(self.model_path, clf)
            return clf
        except Exception as ex:
            # Write out an error file. This will be returned as the failureReason in the
            # DescribeTrainingJob result.
            trc = traceback.format_exc()
            with open(os.path.join(self.output_path, 'failure'), 'w') as s:
                s.write('Exception during training: ' + str(ex) + '\n' + trc)
            # Printing this causes the exception to be in the training job logs, as well.
            print('Exception during training: ' + str(ex) + '\n' + trc, file=sys.stderr)
            # A non-zero exit code causes the training job to be marked as Failed.
            sys.exit(255)

    @staticmethod
    def _populate_hyperparameters(args: Dict[str, Any], hyperparamters_file: str = DEFAULT_PARAM_PATH):
        if not os.path.isfile(hyperparamters_file):
            return args
        with open(hyperparamters_file) as file:
            hyperparameters = json.load(file)
            for k, v in hyperparameters.items():
                args[k] = IrisTrain._convert_hyperparameters_to_datatype(k, v)
        return args

    @staticmethod
    def _convert_hyperparameters_to_datatype(key: str, paramter_str: Any):
        if isinstance(paramter_str, str):
            try:
                val = json.loads(paramter_str)
            except json.decoder.JSONDecodeError:
                val = paramter_str
                _logger.warning(f"Hyperparameter value {val} for {key} could not be decoded.")
        else:
            val = paramter_str
        return val
