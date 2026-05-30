#!/usr/bin/env bash
set -euo pipefail

LAMBDA_NAME="${LAMBDA_NAME:-text-recognizer-api-bscs23020}"
ROLE_NAME="${ROLE_NAME:-text-recognizer-api-bscs23020-role}"
ROLL_NO="${ROLL_NO:-BSCS23020}"
MEMORY_SIZE="${MEMORY_SIZE:-3008}"
TIMEOUT="${TIMEOUT:-300}"
TORCH_NUM_THREADS="${TORCH_NUM_THREADS:-2}"
AWS_BIN="${AWS_BIN:-$HOME/.local/bin/aws}"
AWS_REGION="$($AWS_BIN configure get region)"
AWS_ACCOUNT_ID="$($AWS_BIN sts get-caller-identity --query Account --output text)"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_URI}/${LAMBDA_NAME}:latest"

echo "Building Lambda-compatible image..."
docker buildx build --platform linux/amd64 --provenance=false -t text-recognizer-api:latest --load .

echo "Logging in to ECR..."
$AWS_BIN ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_URI"

echo "Ensuring ECR repository exists..."
$AWS_BIN ecr describe-repositories --repository-names "$LAMBDA_NAME" >/dev/null 2>&1 \
  || $AWS_BIN ecr create-repository \
    --repository-name "$LAMBDA_NAME" \
    --image-scanning-configuration scanOnPush=true \
    --image-tag-mutability MUTABLE >/dev/null

echo "Pushing image..."
docker tag text-recognizer-api:latest "$IMAGE_URI"
docker push "$IMAGE_URI"

echo "Ensuring Lambda execution role exists..."
$AWS_BIN iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1 || \
  $AWS_BIN iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null

$AWS_BIN iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole >/dev/null

ROLE_ARN="$($AWS_BIN iam get-role --role-name "$ROLE_NAME" --query Role.Arn --output text)"
sleep 10

if $AWS_BIN lambda get-function --function-name "$LAMBDA_NAME" >/dev/null 2>&1; then
  echo "Updating existing Lambda function..."
  $AWS_BIN lambda update-function-code \
    --function-name "$LAMBDA_NAME" \
    --image-uri "$IMAGE_URI" >/dev/null
  $AWS_BIN lambda wait function-updated --function-name "$LAMBDA_NAME"
  $AWS_BIN lambda update-function-configuration \
    --function-name "$LAMBDA_NAME" \
    --timeout "$TIMEOUT" \
    --memory-size "$MEMORY_SIZE" \
    --environment "Variables={ROLL_NO=${ROLL_NO},TORCH_NUM_THREADS=${TORCH_NUM_THREADS}}" >/dev/null
else
  echo "Creating Lambda function..."
  $AWS_BIN lambda create-function \
    --function-name "$LAMBDA_NAME" \
    --package-type Image \
    --code "ImageUri=${IMAGE_URI}" \
    --role "$ROLE_ARN" \
    --timeout "$TIMEOUT" \
    --memory-size "$MEMORY_SIZE" \
    --environment "Variables={ROLL_NO=${ROLL_NO},TORCH_NUM_THREADS=${TORCH_NUM_THREADS}}" >/dev/null
fi

$AWS_BIN lambda wait function-active --function-name "$LAMBDA_NAME"

echo "Ensuring public function URL exists..."
$AWS_BIN lambda get-function-url-config --function-name "$LAMBDA_NAME" >/dev/null 2>&1 || \
  $AWS_BIN lambda create-function-url-config \
    --function-name "$LAMBDA_NAME" \
    --auth-type NONE \
    --cors '{"AllowOrigins":["*"],"AllowMethods":["GET","POST"],"AllowHeaders":["content-type"],"AllowCredentials":false}' >/dev/null

$AWS_BIN lambda add-permission \
  --function-name "$LAMBDA_NAME" \
  --action lambda:InvokeFunctionUrl \
  --statement-id open-access-function-url \
  --principal "*" \
  --function-url-auth-type NONE >/dev/null 2>&1 || true

$AWS_BIN lambda add-permission \
  --function-name "$LAMBDA_NAME" \
  --action lambda:InvokeFunction \
  --statement-id open-access-invoke-function \
  --principal "*" \
  --invoked-via-function-url >/dev/null 2>&1 || true

FUNCTION_URL="$($AWS_BIN lambda get-function-url-config --function-name "$LAMBDA_NAME" --query FunctionUrl --output text)"
echo "Function URL: ${FUNCTION_URL}"
echo "Health check:"
curl -sS "${FUNCTION_URL}health"
