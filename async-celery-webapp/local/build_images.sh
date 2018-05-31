echo "Building Handler..."
docker build -t async-handler ../async-celery-webapp/.
echo "Building Backend..."
docker build -t async-backend ../async-celery-backend/.