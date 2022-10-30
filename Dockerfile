FROM public.ecr.aws/lambda/python:3.8

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
RUN python3.8 -m pip install -r requirements.txt


RUN mkdir -p /opt/katna
COPY katna/ /opt/katna
RUN ls -la /opt/katna
WORKDIR /opt/katna
#RUN python3.8 example_video_compression.py 

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
 
