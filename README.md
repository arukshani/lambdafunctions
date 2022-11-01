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

## Next cd in to lambdafunctions and run the following

## Test lambda function locally
#### [Compression code is in the lambda fcuntion]
```
sudo docker build -t test-katna . 
sudo docker run -p 9000:8080 test-katna 
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

## Push image to AWS ECR repository
#### set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN as environment variables
```
sudo aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin 072775118116.dkr.ecr.us-west-2.amazonaws.com
sudo aws ecr create-repository --repository-name test-katna --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
sudo docker tag  test-katna:latest 072775118116.dkr.ecr.us-west-2.amazonaws.com/test-katna:latest
sudo docker push 072775118116.dkr.ecr.us-west-2.amazonaws.com/test-katna:latest  
```

#### In AWS, create the lambda with the pushed image and run


