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
PROJECT_TAG="mot"

STACKNAME="${PROJECT_TAG}-${UNIQUE_NAME}"

make -o build

aws cloudformation validate-template --template-body file://generated/mot.json > /dev/null

PARAMETERS=(
  ParameterKey=VpcId,ParameterValue="$MOT_VPC"
  ParameterKey=SubnetId,ParameterValue="$MOT_SUBNET"
  ParameterKey=HookbotMonitorUrl,ParameterValue="$HOOKBOT_MONITOR_URL"
)


case "$WHAT" in
  create)

    aws cloudformation create-stack                                   \
      --stack-name "$STACKNAME"                                       \
      --disable-rollback                                              \
      --timeout-in-minutes "120"                                      \
      --tags Key=Name,Value="$STACKNAME" Key=Project,Value=mot \
      --capabilities CAPABILITY_IAM                                   \
      --parameters "${PARAMETERS[@]}"                                 \
      --template-body file://generated/mot.json
  ;;

  update)

    aws cloudformation update-stack     \
      --stack-name "$STACKNAME"         \
      --capabilities CAPABILITY_IAM     \
      --parameters "${PARAMETERS[@]}"   \
      --template-body file://generated/mot.json
  ;;

  delete)
   
    aws cloudformation delete-stack     \
      --stack-name "$STACKNAME"
  ;;

  *)
    usage
  ;;
esac

