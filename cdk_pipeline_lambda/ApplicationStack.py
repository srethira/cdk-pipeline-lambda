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

        env = kwargs['env']

        work_dir = pathlib.Path(__file__).parents[1]

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

        # beforeAllowTraffic lambda function
        pre_traffic_lambda = _lambda.Function(
            self, 
            "pre-traffic",
            runtime=_lambda.Runtime.NODEJS_12_X,
            handler="beforeAllowTraffic.handler",
            code=_lambda.Code.asset(
                "./lambda"
            ),
            environment=dict(
                NewVersion=my_datetime_lambda.current_version.function_arn
            )
        )

        pre_traffic_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codedeploy:PutLifecycleEventHookExecutionStatus"],
                resources=["*"]
            )
        )

        pre_traffic_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["lambda:InvokeFunction"],
                resources=["*"]
            )
        )

        # afterAllowTraffic lambda function
        post_traffic_lambda = _lambda.Function(
            self, 
            "post-traffic",
            runtime=_lambda.Runtime.NODEJS_12_X,
            handler="afterAllowTraffic.handler",
            code=_lambda.Code.asset(
                "./lambda"
            ),
            environment=dict(
                NewVersion=my_datetime_lambda.current_version.function_arn
            )
        )

        post_traffic_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codedeploy:PutLifecycleEventHookExecutionStatus"],
                resources=["*"]
            )
        )

        post_traffic_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["lambda:InvokeFunction"],
                resources=["*"]
            )
        )

        # create a cloudwatch event rule
        events.Rule(
            self, 
            "CanaryRule",
            schedule=events.Schedule.expression(
                "rate(10 minutes)"
            ),
            targets=[events_targets.LambdaFunction(
                my_datetime_lambda.current_version
            )],

        )

        # create a cloudwatch alarm based on the lambda erros metrics
        alarm = cloudwatch.Alarm(
            self, 
            "LambdaCanaryAlarm",
            metric=my_datetime_lambda.current_version.metric_invocations(),
            threshold=0,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            treat_missing_data=cloudwatch.TreatMissingData.IGNORE,
            period=core.Duration.minutes(5),
            alarm_name="LambdaCanaryAlarm"
        )

        codedeploy.LambdaDeploymentGroup(
            self, 
            "datetime-lambda-deployment",
            alias=my_datetime_lambda.current_version.add_alias(
                "live"
            ),
            deployment_config=codedeploy.LambdaDeploymentConfig.ALL_AT_ONCE,
            alarms=[alarm],
            auto_rollback=codedeploy.AutoRollbackConfig(
                deployment_in_alarm=True
            ),
            pre_hook=pre_traffic_lambda,
            post_hook=post_traffic_lambda
        )

        gw = _apigw.LambdaRestApi(
            self, 
            "Gateway",
            handler=my_datetime_lambda,
            description="Endpoint for a simple Lambda-powered web service"
        )

        # add an output with a well-known name to read it from the integ tests
        self.gw_url = gw.url