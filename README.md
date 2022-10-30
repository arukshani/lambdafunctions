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

## Test Lamnda Function

```
docker build -t hello-world . 
docker run -p 9000:8080 hello-world 
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```
