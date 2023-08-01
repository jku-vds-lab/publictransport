# This Dockerfile is used as standalone container for simple deployments, it will be built and pushed to https://github.com/orgs/jku-vds-lab/packages?repo_name=publictransport automatically by GH Actions in the build.yml
FROM python:3.10-slim

# copy everything from our backend to our app folder # need to copy backend because we have to install the python packages
COPY fastapi/ /app/fastapi/

# # copy data from dropbox folder https://www.dropbox.com/sh/5at5fborwzi73ij/AABzIQMs0spOJRYyIsGEQ-mKa?dl=0
# RUN mkdir -p /app/fastapi/publictransport/data/
# WORKDIR /app/fastapi/publictransport/data/
# # TODO: make this recursive
# RUN wget -O agency.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AADCgSQbHxb5kto4K-pxomdHa/agency.txt?dl=1
# RUN wget -O calendar_dates.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AADUFULJQguxTnfZP5_EC3W8a/calendar_dates.txt?dl=1
# RUN wget -O calendar.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AACnspX7mP6ApnYrIw8TR2CSa/calendar.txt?dl=1
# RUN wget -O routes.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AACR2eM9Le27f9LmyZBOqX2Za/routes.txt?dl=1
# RUN wget -O shapes.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AACzgOdODnZrI8az6iBaRSRra/shapes.txt?dl=1
# RUN wget -O stop_times.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AABx6gsqO4_fUuCmj0xuIr5Ya/stop_times.txt?dl=1
# RUN wget -O stops.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AAC2HV9FK5Dzz1oattuLZHg5a/stops.txt?dl=1
# RUN wget -O trips.txt https://www.dropbox.com/sh/5at5fborwzi73ij/AADx3tTZ49pRPtGRzfxr6UFba/trips.txt?dl=1

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
