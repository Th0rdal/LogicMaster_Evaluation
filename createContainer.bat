
docker build -t ai_base -f .\dockerfile_ai_base .
docker build -t qlearning -f dockerfile_qlearning .
docker build -t preprocessing -f .\dockerfile_preprocessing .