# mlops-iris-train-demo
Repo containing training code for an Iris classifier. This repo supports running the training code as an 
[AWS Sagemaker training job](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html).

## Requirements

- Python 3.8.X
- Poetry: for instructions see https://python-poetry.org/docs/

## Installation

1. Verify Python and Poetry installation

    ```bash
    $ cd mlops-iris-train-demo
    $ poetry env info
    # you should get a similar output
    Virtualenv
    Python:         3.8.12
    Implementation: CPython
    Path:           /Users/user1/mlops-iris-train-demo/.venv
    Valid:          True
    
    System
    Platform: darwin
    OS:       posix
    Python:   /Users/user1/.pyenv/versions/3.8.12
    ```

2. Create virtual environment and install dependencies:

    ```bash
    $ poetry install
    ```
   
3. Prior to running a training job, determine the values to assign to:
    - "train_data_dir": directory containing training data
    - "model_dir": directory where the model will be written
    - "output_dir": directory where errors will be reported
4. Run the training job:
    ```shell
    $ poetry run python src/mlops_iris_train_demo/train \
        --train_data_dir="/path/to/training/data/dir/" \ 
        --model_dir="/path/to/model/data/dir/" \
        --output_dir="/path/to/output/data/dir/"
    ```
   
    note: if not values are specified, default values will be assigned