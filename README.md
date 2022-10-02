# mlops-iris-train-demo
Repo containing training code for an Iris classifier. This repo supports running the training code as an 
[AWS Sagemaker training job](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html).

## Requirements

- Python 3.8.X
- Poetry: for instructions see https://python-poetry.org/docs/
- AWS CLI: for instructions see https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
- Docker Desktop: https://www.docker.com/products/docker-desktop/

__Disclaimer__: Be careful when provisioning resources in AWS, they cost money when you use them.
It's your responsibility to shut them down when unused to avoid extra/unexpected costs.

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
    # values between < and > should be replaced
    $ poetry run python src/mlops_iris_train_demo/train \
        --train_data_dir="</path/to/training/data/dir/>" \ 
        --model_dir="</path/to/model/data/dir/>" \
        --output_dir="</path/to/output/data/dir/>"
    ```
   
    note: if not values are specified, default values will be assigned

## Docker image build

To be able to run a training job with a custom algorithm in AWS, you have to
provide a docker image containing your custom training logic. Let's create this
docker image:

1. We provided a Dockerfile to be used to create the runtime environment for the
training job - to build this file locally, you need to install docker desktop

2. Once Docker Desktop is installed and running, build the image with the following 
command:

   ```shell
   $ docker build . -t iris-train
   ```

3. Once image is built, you can test it locally running this command:

   ```shell
   # values between < and > should be replaced
   $ docker run --rm -it \
     -v </path/to/training/data/dir/>:/opt/ml/input/data/training \
     -v </path/to/model/data/dir/>:/opt/ml/model \
     -v </path/to/output/data/dir/>:/opt/ml/output \
     iris-train train
   ```

## Pushing docker image with training code to AWS

1. Create docker image repository named "iris-train" in AWS - see: https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html

2. Build and push the docker image using the [build.sh](build.sh) script:

   ```shell
   # replace <aws-region> with the AWS region where you're creating your AWS resources
   $ ./build.sh iris-train <aws-region> 
   ```

## Add CI/CD using AWS CodeBuild

1. 