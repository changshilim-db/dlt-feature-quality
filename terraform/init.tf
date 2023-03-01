terraform {
  backend "s3" {
    bucket = "feature-quality-blog-tf-bucket"
    key    = "terraform.tfstate"
    region = "ap-southeast-1"
  }
}