data "archive_file" "compressor" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/ingestor/handler.py"
  output_path = "${path.module}/../lambdas/ingestor/ingestor.zip"
}

resource "aws_lambda_function" "ingestor" {
  function_name    = "earthquake-ingestor"
  role             = aws_iam_role.ingestor.arn
  runtime          = "python3.12"
  handler          = "handler.lambda_handler"
  filename         = data.archive_file.compressor.output_path
  source_code_hash = data.archive_file.compressor.output_base64sha256
  timeout          = 30
  memory_size      = 128

  environment {
    variables = {
      RAW_BUCKET = aws_s3_bucket.raw.id
    }
  }
}
