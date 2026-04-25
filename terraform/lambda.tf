data "archive_file" "ingestor_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/ingestor/handler.py"
  output_path = "${path.module}/../lambdas/ingestor/ingestor.zip"
}

data "archive_file" "transformer_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/transformer/handler.py"
  output_path = "${path.module}/../lambdas/transformer/transformer.zip"
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transformer.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw.arn
}

resource "aws_lambda_function" "ingestor" {
  function_name    = "earthquake-ingestor"
  role             = aws_iam_role.ingestor.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.ingestor_zip.output_path
  source_code_hash = data.archive_file.ingestor_zip.output_base64sha256
  timeout          = 30
  memory_size      = 128

  environment {
    variables = {
      RAW_BUCKET       = aws_s3_bucket.raw.id
      AWS_ACCOUNT_ID   = data.aws_caller_identity.current.account_id
    }
  }
}

resource "aws_lambda_function" "transformer" {
  function_name    = "earthquake-transformer"
  role             = aws_iam_role.transformer.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.transformer_zip.output_path
  source_code_hash = data.archive_file.transformer_zip.output_base64sha256
  timeout          = 30
  memory_size      = 128

  environment {
    variables = {
      RAW_BUCKET       = aws_s3_bucket.raw.id
      PROCESSED_BUCKET = aws_s3_bucket.processed.id
      AWS_ACCOUNT_ID   = data.aws_caller_identity.current.account_id
    }
  }
}
