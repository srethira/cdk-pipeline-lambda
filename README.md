
# Package Description:

The purpose of this artifact is to give a customer out of the box solution to get started with AWS CDK project for deploying
a serverless application into cross region and cross account using AWS Devloper tools like AWS CodeCommit, AWS CodePipeline and AWS Cloudformation.

The purpose of this artifact is to get the developer hands of experience with AWS CDK and show the way that CDK helps in generating AWS Cloudformation
tempaltes and provision Pipeline with few commands.
Also, since the AWS Codepipelines are provisioned through AWS CDK, when there is change to the pipeline itself (example, adding a new stage in the pipelines), 
developer need not to worry about operational changes to pipeline insfrastructre, as AWS CDK has a built in feature called `Self Mutation deploys` which means
if there are any changes to pipeline itselt, once the code is commited to CodeCommit Repo, the pipeline will take care of making changes to pipeline infrastrucre.

# Design Overview
This artifact is needed two AWS Accounts, one is to provision Pipeline Infrastrcutre and another is to provision Application Instraftructure(In this case it would be a Serverless Application)
![](design.png)

# Folder Structre

| Folder/File | Description |  
| :-------------------------| :-------------------------------------------------------------------------------------------------------------------|
| cdk.json                                    | Context values for application and parameters for AWS Accounts, also tells the CDK Toolkit how to execute your app |
| cdk.context.json                            | Context values for AWS Account Availability Zones |
| app.py                                      | Loads cdk.json and cdk.context.json and calls pipeline/PipelineStack.py to provision pipeline |
| pipeline/PipelineStack.py                   | Logic for representing how your pipeline should looks like (Imaging a CFN tempalte for provisioning pipeline) |
| ApplicationStage.py                         | Logic for representing an application modeling unit consisting of Stacks that can be deployed together. (Imaging multiple CFN templates/stacks for application stage in pipeline)| 
| cdk_pipeline_lambda/ApplicationStack.py     | Logic for provisioning your application infrastructure (Imagin a CFN template for application provisioning) |
| lambda                                      | Application Code |

# Pre-reqs:
1. Get CDK Installed and Configure AWS Credentials : [install-cdk link] (https://docs.aws.amazon.com/cdk/latest/guide/cli.html) 
2. Bootstrapping your environments : [General-Information link] (https://docs.aws.amazon.com/cdk/latest/guide/cli.html#cli-bootstrap)
   `env CDK_NEW_BOOTSTRAP=1 npx cdk bootstrap \
    --profile default \
    --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess \
    --trust <<ApplicationProvisionAWSAccount#>> \
    aws://<<PipelineProvisionAWSAccount#>>/us-west-1`
3. It is expected to have a CodeCommit Repo, if not please create one and checkout the repo.
4. Clone repo: [link] (https://gitlab.aws.dev/proserve-ussdt-devops/cdk-pipeline-lambda)
5. Checkout cdk-pipeline-lambda and copy the contents to CodeCommit Repo (Ref: Step3)
6. Open `cdk.json` and update the following: 
   1. account:`<<pipelineProvisionAWSAccount#>>` from line# 8
   2. account:`<<pipelineProvisionAWSAccount#>>` from line# 13
   3. account:`<<ApplicationProvisionAWSAccount#>>` from line# 16
   4. Optionals: If you would like to change the region, you can do so.

7. Open `cdk.context.json` and update the following:
   1. account=`<<pipelineProvisionAWSAccount#>>`
   2. account=`<<ApplicationProvisionAWSAccount#>>`
8. Open `pipeline/PipelineStack.py` and replace `cdk-pipeline-demo` this with your codecommit repo name.
9. Optional:
   1. If you want to change the stack name, Open `app.py`, replace `my-app-lambda-pipeline` this with new name.
   2. If you want to change the pipeline name, Open `pipeline/PipelineStack.py`, replace pipeline_name=`"MyLambdaPipeline"` this with new name.
10. Push changes to CodeCommit Repo

# Setup local environment:
    This project is set up like a standard Python project.  The initialization
    process also creates a virtualenv within this project, stored under the .env
    directory.  To create the virtualenv it assumes that there is a `python3`
    (or `python` for Windows) executable in your path with access to the `venv`
    package. If for any reason the automatic creation of the virtualenv fails,
    you can create the virtualenv manually.

    To manually create a virtualenv on MacOS and Linux:

    ```
    $ python3 -m venv .env
    ```

    After the init process completes and the virtualenv is created, you can use the following
    step to activate your virtualenv.

    ```
    $ source .env/bin/activate
    ```

    If you are a Windows platform, you would activate the virtualenv like this:

    ```
    % .env\Scripts\activate.bat
    ```

    Once the virtualenv is activated, you can install the required dependencies.

    ```
    $ pip install -r requirements.txt
    ```

    At this point you can now synthesize the CloudFormation template for this code.

    ```
    $ cdk synth
    ```

    To add additional dependencies, for example other CDK libraries, just add
    them to your `setup.py` file and rerun the `pip install -r requirements.txt`
    command.

# Provision pipelines
1. Execute `cdk deploy -All`, you should be receving few [y/n] prompts, please proveed with [y].
2. If everything goes well, you should be able to see the pipelines in Pipelines Provision AWS Account.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
