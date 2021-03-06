from aws_cdk.core import Stack, StackProps, Construct, SecretValue, Environment
from aws_cdk.pipelines import CdkPipeline, SimpleSynthAction, ShellScriptAction
from ApplicationStage import ApplicationStage

import aws_cdk.aws_codepipeline as codepipeline
import aws_cdk.aws_codepipeline_actions as codepipeline_actions
import aws_cdk.aws_codecommit as codecommit
import os


# Stack to hold the pipeline
class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repo = codecommit.Repository.from_repository_name(self, "ImportedRepo", "cdk-pipeline-demo")
        test_account = self.node.try_get_context("testAccount")
        prod_account = self.node.try_get_context("prodAccount")

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()
        pipeline = CdkPipeline(
            self, 
            "LambdaPipeline",
            pipeline_name="MyLambdaPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            source_action=codepipeline_actions.CodeCommitSourceAction(
                action_name="CodeCommit",
                repository=repo,
                output=source_artifact
            ),
            # Current limitation: generate CodeBuild reports within @aws-cdk/cdk-pipelines
            # https://github.com/aws/aws-cdk/issues/10464
            synth_action=SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                # enable privileged mode for docker-in-docker (for asset bundling)
                environment=dict(
                    privileged=True
                ),
                install_command="pipeline/bin/install.sh",
                synth_command="cdk synth",
            )
        )

        # Do this as many times as necessary with any account and region for testing
        # Account and region may be different from the pipeline's.
        test = ApplicationStage(
            self, 
            'Test',
            env=Environment(
                account=test_account["account"], 
                region=test_account["region"]
            )    
        )

        test_stage = pipeline.add_application_stage(
            test
        )

        test_stage.add_actions(
            ShellScriptAction(
                action_name='validate', 
                commands=['curl -X POST -H "Content-Type: application/json" -d "{\"option\":\"date\",\"period\":\"today\"}" $ENDPOINT_URL/'],
                use_outputs=dict(
                    ENDPOINT_URL=pipeline.stack_output(
                        test.gateway_url
                    )
                )
            )
        )

        # Do this as many times as necessary with any account and region for prod
        prod = ApplicationStage(
            self, 
            'Prod',
            env=Environment(
                account=prod_account["account"], 
                region=prod_account["region"]
            )
        )

        prod_stage = pipeline.add_application_stage(
            prod
        )

        prod_stage.add_actions(
            ShellScriptAction(
                action_name='validate', 
                commands=['curl -X POST -H "Content-Type: application/json" -d "{\"option\":\"date\",\"period\":\"today\"}" $ENDPOINT_URL/container'],
                use_outputs=dict(
                    ENDPOINT_URL=pipeline.stack_output(
                        prod.gateway_url
                    )
                )
            )
        )