## Install Docker

```
sudo apt install apt-transport-https ca-certificates curl software-properties-common 
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - 
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu `lsb_release -cs` test" 
sudo apt update 
sudo apt install docker-ce 
docker -v 
sudo docker run hello-world 
```

## You need to have katna repo inside lambdafunctions folder since we need to copy the katna repo. 
## Next cd in to lambdafunctions and run the following

## Test Lambda Function

```
sudo docker build -t hello-world . 
sudo docker run -p 9000:8080 hello-world 
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

## Run a container again and ssh into container to test the compression
```
sudo docker run -it --name test1  hello-world  /bin/sh
sudo docker exec -it test1 /bin/sh
```

### Once in the container go to /var/task and run
```
python3.8 example_video_compression.py
```
