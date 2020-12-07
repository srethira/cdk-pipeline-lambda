#!/usr/bin/env python3

from aws_cdk import core
from pipeline.PipelineStack import PipelineStack

app = core.App()
shared_service_account = app.node.try_get_context("sharedServiceAccount")
PipelineStack(
    app, "my-app-lambda-pipeline",
        env=core.Environment(account=shared_service_account["account"], 
              region=shared_service_account["region"])
)
app.synth()
