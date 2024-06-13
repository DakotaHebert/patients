FROM  public.ecr.aws/docker/library/python:3.11-slim-buster

COPY . ${TASK_ROOT}/
RUN cd ${TASK_ROOT} && \
  python -m pip install poetry==1.4.2 && \
  poetry export -f requirements.txt --without-hashes > requirements.txt && \
  python -m pip install --extra-index-url $CODE_ARTIFACT_REPOSITORY_URL -r requirements.txt
