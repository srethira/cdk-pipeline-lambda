from aws_cdk.core import Construct, Stack, Stage, Environment, CfnOutput
from cdk_pipeline_lambda.ApplicationStack import ApplicationStack

class ApplicationStage(Stage):
    gateway_url: CfnOutput = None

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        env = kwargs['env']

        app_stack = ApplicationStack(
            self, 
            "ApplicationStack",
            env=env
        )

        self.gateway_url = CfnOutput(
            app_stack, 
            "GatewayUrl",
            value=app_stack.gw_url
        )