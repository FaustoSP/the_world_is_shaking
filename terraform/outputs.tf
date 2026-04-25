output "cloudfront_domain" {
  value = "https://${aws_cloudfront_distribution.processed.domain_name}"
}
