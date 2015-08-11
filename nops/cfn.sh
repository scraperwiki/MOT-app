#! /bin/bash

set -eu

usage() {
  echo "usage: $0 create|update|delete <stack name>" 1>&2
  echo "For example: ./cfn.sh create 20150521-sm"
  exit 1
}

if [ -z "${1-}" ] || [ -z "${2-}" ]; then
  usage
fi

WHAT="$1"
UNIQUE_NAME="$2"

# Sets the "Project" tag, for billing
PROJECT_TAG="newsreader"

STACKNAME="${PROJECT_TAG}-${UNIQUE_NAME}"

make -o build

aws cloudformation validate-template --template-body file://generated/newsreader.json > /dev/null

PARAMETERS=(
  ParameterKey=NewsreaderPublicUsername,ParameterValue="$NEWSREADER_PUBLIC_USERNAME"
  ParameterKey=NewsreaderPublicPassword,ParameterValue="$NEWSREADER_PUBLIC_PASSWORD"
  ParameterKey=NewsreaderPrivateUsername,ParameterValue="$NEWSREADER_PRIVATE_USERNAME"
  ParameterKey=NewsreaderPrivatePassword,ParameterValue="$NEWSREADER_PRIVATE_PASSWORD"
  ParameterKey=NewsreaderPublicApiKey,ParameterValue="$NEWSREADER_PUBLIC_API_KEY"
  ParameterKey=NewsreaderPrivateApiKey,ParameterValue="$NEWSREADER_PRIVATE_API_KEY"
  ParameterKey=VpcId,ParameterValue="$NEWSREADER_VPC"
  ParameterKey=SubnetId,ParameterValue="$NEWSREADER_SUBNET"
  ParameterKey=HookbotMonitorUrl,ParameterValue="$HOOKBOT_MONITOR_URL"
)


case "$WHAT" in
  create)

    aws cloudformation create-stack                                   \
      --stack-name "$STACKNAME"                                       \
      --disable-rollback                                              \
      --timeout-in-minutes "120"                                      \
      --tags Key=Name,Value="$STACKNAME" Key=Project,Value=newsreader \
      --capabilities CAPABILITY_IAM                                   \
      --parameters "${PARAMETERS[@]}"                                 \
      --template-body file://generated/newsreader.json
  ;;

  update)

    aws cloudformation update-stack     \
      --stack-name "$STACKNAME"         \
      --capabilities CAPABILITY_IAM     \
      --parameters "${PARAMETERS[@]}"   \
      --template-body file://generated/newsreader.json
  ;;

  delete)
   
    aws cloudformation delete-stack     \
      --stack-name "$STACKNAME"
  ;;

  *)
    usage
  ;;
esac

