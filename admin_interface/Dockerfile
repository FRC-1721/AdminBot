FROM python:3.11

# Authors
LABEL authors="31870999+KenwoodFox@users.noreply.github.com"

# Set the name of our app
ARG APP_NAME=admin-interface
ENV APP_NAME=${APP_NAME}

# Install special deps
# RUN apt update && apt install -y <packages>

# Upgrade pip
RUN pip install --upgrade pip

# Get the current git version
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT

# App home
ARG HOME="/app"
ENV HOME=${HOME}

# Set workdir
WORKDIR ${HOME}

# Copy in all requirements
ADD requirements requirements/

# Install normal reqs
RUN pip install -r requirements/requirements.txt
# Install testing reqs
# RUN pip install -r requirements/test_requirements.txt

# Copy in everything else
ADD . ${HOME}
# Add /bin to path
ENV PATH $PATH:${HOME}/bin

# Drop root and change ownership of /app to app:app
RUN chown -R ${USER_ID}:${GROUP_ID} ${HOME}
USER ${USER_ID}

EXPOSE 8000

HEALTHCHECK NONE

# Run the entrypoint bin
ENTRYPOINT ["entrypoint"]
