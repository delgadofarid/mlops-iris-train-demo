# A MLOps Workflow - Iris Classifier
Repo containing training code for an Iris classifier. This repo supports running the training code as an 
[AWS Sagemaker training job](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html).

## Requirements

- Python 3.8.X
- Poetry: for instructions see https://python-poetry.org/docs/
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- AWS CLI: for instructions see https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

__Disclaimer__: Be careful when provisioning resources in AWS, they cost money when you use them.
It's your responsibility to shut them down when unused to avoid extra/unexpected costs.

## 1. Installation

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

## 2. Docker image build

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

## 3. Fork or replicate this repo on your GitHub account

This step is needed for you to be able to interact with the repo using a token with 
"repo" scope level. This will be important for the next step.

## 4. Create CloudFormation stack

We will use the CloudFormation template [cf-template.yml](workflow/cf-template.yml) to provision the AWS
infrastructure for our MLOps Workflow.

Remember to delete de stack once you finish the lab to avoid getting charged unnecessary costs.

1. Create an IAM role for CloudFormation (CF). This is the role used by CF to provision all
the required resources, therefore, depending on all the required resources, this role would have to
be adjusted correspondingly. For more info about IAM roles see: [Creating IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html).

2. Once the CF role is created, we can proceed uploading the template [cf-template.yml](workflow/cf-template.yml) as
explained here: [Using the console to create a CF stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html)

   1. Select the option "Upload a tempalte file and find [cf-template.yml](workflow/cf-template.yml), click "Next"
   2. Specify the CF stack name (e.g. a-mlops-workflow) and parameters:
      1. ECRRepositoryName: name of the ECR repository that will be created
      2. GitHubBranch: which GitHub branch to use for setting up the webhook
      3. GitHubOAuthToken: a GitHub PAT with "repo" level access to the repo specified in `GitHubRepo` parameter
      4. GitHubOwner: GitHub repository owner user
      5. GitHubRepo: GitHub repository name
      
      Then click "Next"
3. Assign the CF role previously created in the "Permissions" section, click "Next"
4. Review your stack, estimate stack cost, and after reviewing and validating everything, 
choose "Create stack" 

If everything is successful, we should have the following resources available for our MLOps workflow:
- Steps Function workflow with two steps: `Train Step`, `Save model`
- A CodePipeline pipeline listening for new changes in our GitHub repo, that:
  - build and push every new version of the training code to ECR, using 
  the commit hash as a versioning mechanims
  - triggers the Steps Function workflow which trains the model
  - two s3 buckets, one for the training data and another for the model artifacts

__Disclaimer__: at this point, multiple resources will be created in AWS and it's your responsibility
to keep track of the related costs. The advantage of provisioning the cloud infrastructure this way is 
that, once we finish the experiments, we can simply delete the entire CF stack and no resources will be
dangling around.

## 5. Upload the training data
1. Upload the [iris.csv](data/iris.csv) file to the S3 key: `s3://<modeldatabucket>/v1.0/train/` - replace 
`modeldatabucket` with the name of the bucket created by the CF stack

## 6. Trigger a model training

1. To trigger model training, we just need to make a change to the repository, commit and push these changes to the
branch specified above (i.e. `GitHubBranch`)

## Appendix

### Push docker image manually to AWS

This step is for the curious, not needed since this was automated using CodePipeline and CodePipeline.

1. Create docker image repository named "iris-train" in AWS: https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html

2. Setup AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

   ```shell
   # once configured, you should the following files created under ~/.aws/
   $ ls -l ~/.aws/
   total 16
   -rw-------  1 u6104617  staff   43  2 Oct 14:18 config
   -rw-------  1 u6104617  staff  116  2 Oct 14:18 credentials
   ```
   
   Note: Ensure these files are only accessible by yourself as they contain 
   your AWS credentials.

4. Build and push the docker image using the [build.sh](build.sh) script:

   ```shell
   # replace <aws-region> with the AWS region where you're creating your AWS resources
   $ ./build.sh iris-train <aws-region> 
   ```

## TODO:
- CloudFormation template:
  - adjust IAM roles with least required privileges
  - update GitHub version 1 source action to a GitHub version 2 source action: https://docs.aws.amazon.com/codepipeline/latest/userguide/update-github-action-connections.html
- Steps Function workflow:
  - add step to test model
- Trigger on data changes
  - event notification triggering lambda