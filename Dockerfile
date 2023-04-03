# This Dockerfile is used as standalone container for simple deployments, it will be built and pushed to https://github.com/orgs/jku-vds-lab/packages?repo_name=publictransport automatically by GH Actions in the build.yml
FROM python:3.10-buster

# copy everything from our backend to our app folder # need to copy backend because we have to install the python packages
COPY fastapi/ /app/fastapi/

# copy the pre-built front-end
COPY myapp/dist/ /app/fastapi/publictransport/frontend/

# define target folder
WORKDIR /app/fastapi

# RUN pip install --upgrade pip
RUN pip install -e .

# expose default port
EXPOSE 9000


# define target folder
WORKDIR /app/fastapi/publictransport

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]

# Running
# docker build -f Dockerfile -t publictransport .
# docker run --rm -it -p 9000:9000 publictransport
