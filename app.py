#!/usr/bin/env python3

from aws_cdk import core
from pipeline.PipelineStack import PipelineStack

app = core.App()
PipelineStack(app, "my-app-pipeline",
              env=core.Environment(account="820872918044", region="us-west-2"))
app.synth()
