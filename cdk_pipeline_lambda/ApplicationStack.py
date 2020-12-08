from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ssm as ssm,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elb_targets,
    aws_lambda as _lambda,
    aws_codedeploy as codedeploy,
    aws_events as events,
    aws_events_targets as events_targets,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_apigateway as _apigw,
)
import os.path
import pathlib


class ApplicationStack(core.Stack):
    load_balancer_dns_name: core.CfnOutput = None

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # myDateTimeFunction lambda function
        my_datetime_lambda = _lambda.Function(
            self, 
            "my-datetime",
            runtime=_lambda.Runtime.NODEJS_12_X,
            handler="myDateTimeFunction.handler",
            code=_lambda.Code.asset("./lambda"),
            current_version_options=_lambda.VersionOptions(
                removal_policy=core.RemovalPolicy.RETAIN, 
                retry_attempts=1
            )
        )

        my_datetime_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["lambda:InvokeFunction"],
                resources=["*"]
            )
        )

        codedeploy.LambdaDeploymentGroup(
            self, 
            "datetime-lambda-deployment",
            alias=my_datetime_lambda.current_version.add_alias(
                "live"
            ),
            deployment_config=codedeploy.LambdaDeploymentConfig.ALL_AT_ONCE
        )

        gw = _apigw.LambdaRestApi(
            self, 
            "Gateway",
            handler=my_datetime_lambda,
            description="Endpoint for a simple Lambda-powered web service"
        )

        # add an output with a well-known name to read it from the integ tests
        self.gw_url = gw.url