#!/usr/bin/env bash
timestamp() {
 date '+%Y-%m-%d %H:%M:%S' # current time
}
set -e

image=$1
region=$2

docker_file=Dockerfile

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]
then
    echo "Failed to retrieve current account"
    exit 255
fi

echo "account: ${account}"
echo "ecr repo name: ${image}"
echo "codebuild hash: $CODEBUILD_RESOLVED_SOURCE_VERSION"
if [[ -z "${CODEBUILD_RESOLVED_SOURCE_VERSION}" ]]; then
  echo "Using git hash commit"
  hash=$(git rev-parse --short HEAD)
  echo "git hash: $hash"
else
  echo "Using codebuild hash"
  hash=$(head -c 7 <<< "$CODEBUILD_RESOLVED_SOURCE_VERSION")
  echo "codebuild git hash: $hash"
fi

export CommitHash=$hash

# ECR login for the current account in order to publish our image
aws ecr get-login-password --region ${region} \
| docker login --username AWS --password-stdin ${account}.dkr.ecr.${region}.amazonaws.com

# Build the docker image locally with the image name and then push it to ECR with the full name.
echo $(timestamp) "Staring build of" ${image}
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}"
VERSIONED_IMG=${fullname}:${hash}
LATEST_IMG=${fullname}:latest
VERSION=${fullname}:${version}
docker build -t ${VERSIONED_IMG} -f ${docker_file} .

# Tag image w/ 2 tags :{hash} & :latest
docker tag ${VERSIONED_IMG} ${LATEST_IMG}

# Push image to AWS ECR
echo $(timestamp) "Pushing" ${fullname} "to ECR"
docker push -a ${fullname}
echo $(timestamp) "image ${fullname} has been pushed to ECR"