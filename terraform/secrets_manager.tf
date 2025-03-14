resource "aws_secretsmanager_secret" "totesys_secret" {
  name                           = var.totesys_credentials_secret_name
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "totesys_secret_version" {
  secret_id = aws_secretsmanager_secret.totesys_secret.id
  secret_string = jsonencode({ username = var.a_totesys_username
    password = var.b_totesys_password
    host     = var.c_totesys_host
    database = var.d_totesys_database
  port = var.i_db_port })
}

resource "aws_secretsmanager_secret" "Data_Warehouse_secret" {
  name                           = var.dw_credentials_secret_name
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "finalDW_secret_version" {
  secret_id = aws_secretsmanager_secret.Data_Warehouse_secret.id
  secret_string = jsonencode({ username = var.e_final_dw_username
    password = var.f_final_dw_password
    host     = var.g_final_dw_host
    database = var.h_final_dw_database
  port = var.i_db_port })
}