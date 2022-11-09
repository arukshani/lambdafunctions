FROM public.ecr.aws/lambda/python:3.8

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
#RUN python3.8 -m pip install -r requirements.txt


#RUN mkdir -p /opt/katna
#COPY katna/ /opt/katna
#RUN ls -la /opt/katna
#WORKDIR /opt/katna
#RUN python3.8 example_video_compression.py 

#RUN yum update
#RUN yum install libglvnd-glx
#RUN yum install ffmpeg --target "${LAMBDA_TASK_ROOT}"
RUN yum install -y mesa-libGL
#COPY ffmpeg-release-amd64-static/ffmpeg-5.1.1-amd64-static/ /usr/local/bin/
COPY ffmpeg-release-amd64-static/ffmpeg-5.1.1-amd64-static/ /var/task/
RUN chmod +x /var/task/ffmpeg
RUN chmod +x /var/task/ffprobe
#RUN chmod +x /usr/local/bin/ffmpeg
#RUN chmod 777 -R /usr/local/bin/ffmpeg
#RUN chmod 777 -R /var/task/ffmpeg

COPY katna/ ${LAMBDA_TASK_ROOT}
# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
 
