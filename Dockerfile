FROM python:3.7

## make a local directory
RUN mkdir /app

# set "counter_app" as the working directory from which CMD, RUN, ADD references
WORKDIR /app

# now copy all the files in this directory to /counter_app
ADD . .

# pip install the local requirements.txt
RUN pip install -r requirements.txt

# Listen to port 5000 at runtime
EXPOSE 5000

# Define our command to be run when launching the container
CMD ["python", "-u", "manage.py", "runserver"]
