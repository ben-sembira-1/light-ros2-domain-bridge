docker build -t query-topic-data .
docker run -v ./:/app -it --rm query-topic-data bash