FROM python:3.8.12

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Install poetry
ENV POETRY_VERSION=1.1.15
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"

# Copy sources
COPY pyproject.toml poetry.* /opt/program/iris_train/
COPY src /opt/program/iris_train/src

# Install project
WORKDIR /opt/program/iris_train/
RUN poetry config virtualenvs.create false --local
RUN poetry install

# COpy entrypoint script to /opt/program
WORKDIR /opt/program
RUN mv iris_train/src/train /opt/program/
RUN chmod +x /opt/program/train