# Terraform Deployment para Sentiment API

Este directorio contiene la configuración de Terraform para deployar la aplicación Sentiment API en AWS EC2.

## Prerequisitos

1. **Terraform instalado** (v1.0 o superior)
   ```bash
   # Verificar instalación
   terraform version
   ```

2. **AWS CLI configurado**
   ```bash
   aws configure
   ```

3. **Credenciales de AWS** con permisos para:
   - EC2 (crear instancias, security groups)
   - VPC (acceso a subnets)
   - CloudWatch Logs

## Configuración

### 1. Obtener información de tu infraestructura existente

Ejecuta estos comandos para obtener los IDs necesarios:

```bash
# Listar tus VPCs
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,Tags[?Key==`Name`].Value|[0]]' --output table

# Listar subnets en tu VPC
aws ec2 describe-subnets --filters "Name=vpc-id,Values=TU_VPC_ID" --query 'Subnets[*].[SubnetId,AvailabilityZone,CidrBlock]' --output table

# Listar Security Groups
aws ec2 describe-security-groups --filters "Name=vpc-id,Values=TU_VPC_ID" --query 'SecurityGroups[*].[GroupId,GroupName,Description]' --output table

# Listar Key Pairs
aws ec2 describe-key-pairs --query 'KeyPairs[*].KeyName' --output table
```

### 2. Crear archivos de configuración

```bash
# Copiar ejemplo de variables
cp terraform.tfvars.example terraform.tfvars
cp sensitive.tfvars.example sensitive.tfvars

# Editar con tus valores
# terraform.tfvars - Configuración de infraestructura
# sensitive.tfvars - Variables sensibles (MongoDB, etc.)
```

### 3. Editar `terraform.tfvars`

```hcl
aws_region        = "us-east-1"
vpc_id            = "vpc-abc123..."
subnet_id         = "subnet-xyz456..."
security_group_id = "sg-def789..."
key_name          = "tu-key-pair"
instance_type     = "t2.small"
```

### 4. Editar `sensitive.tfvars`

```hcl
mongodb_uri   = "mongodb+srv://user:pass@cluster.mongodb.net/MervalDB"
database_name = "MervalDB"
db_port       = "27017"
```

## Security Group Requirements

Asegúrate de que tu Security Group tenga estas reglas:

**Inbound Rules:**
- Puerto 22 (SSH) - Desde tu IP
- Puerto 8001 (API) - Desde donde necesites acceso (0.0.0.0/0 para público)

**Outbound Rules:**
- Todo el tráfico permitido (para descargar dependencias y conectar a MongoDB)

Si necesitas crear un nuevo Security Group:

```bash
aws ec2 create-security-group \
  --group-name sentiment-api-sg \
  --description "Security group for Sentiment API" \
  --vpc-id TU_VPC_ID

# Agregar reglas
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp --port 22 --cidr TU_IP/32

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp --port 8001 --cidr 0.0.0.0/0
```

## Deployment

### 1. Inicializar Terraform

```bash
cd terraform
terraform init
```

### 2. Validar configuración

```bash
terraform validate
```

### 3. Ver plan de ejecución

```bash
terraform plan -var-file="terraform.tfvars" -var-file="sensitive.tfvars"
```

### 4. Aplicar configuración

```bash
terraform apply -var-file="terraform.tfvars" -var-file="sensitive.tfvars"
```

Terraform te mostrará los cambios y pedirá confirmación. Escribe `yes` para continuar.

### 5. Ver outputs

```bash
terraform output
```

Obtendrás:
- IP pública de la instancia
- URL de la API
- URL de la documentación (Swagger)
- Comando SSH para conectarte

## Acceder a la API

Una vez deployada, la API estará disponible en:

```
http://<PUBLIC_IP>:8001
```

Documentación interactiva:
```
http://<PUBLIC_IP>:8001/docs
```

## Verificar deployment

### SSH a la instancia

```bash
ssh -i ~/.ssh/TU_KEY.pem ec2-user@<PUBLIC_IP>
```

### Verificar status del servicio

```bash
sudo systemctl status sentiment-api
```

### Ver logs

```bash
sudo journalctl -u sentiment-api -f
```

### Ver logs de la aplicación

```bash
sudo tail -f /var/log/cloud-init-output.log
```

## Actualizar la aplicación

### Opción 1: Desde GitHub (Recomendado)

```bash
# SSH a la instancia
ssh -i ~/.ssh/TU_KEY.pem ec2-user@<PUBLIC_IP>

# Actualizar código
cd /opt/sentiment-api
sudo git pull origin main

# Reiniciar servicio
sudo systemctl restart sentiment-api
```

### Opción 2: Recrear instancia

Modifica `user_data_replace_on_change = true` en `ec2.tf` y ejecuta:

```bash
terraform apply -var-file="terraform.tfvars" -var-file="sensitive.tfvars"
```

## Destruir infraestructura

```bash
terraform destroy -var-file="terraform.tfvars" -var-file="sensitive.tfvars"
```

## Troubleshooting

### La instancia no responde

1. Verificar Security Group permite puerto 8001
2. Verificar que el servicio esté corriendo: `sudo systemctl status sentiment-api`
3. Revisar logs: `sudo journalctl -u sentiment-api -f`

### Error de conexión a MongoDB

1. Verificar que las credenciales en `sensitive.tfvars` sean correctas
2. Verificar que la instancia tenga acceso a internet (outbound rules)
3. Revisar archivo .env en la instancia: `sudo cat /opt/sentiment-api/.env`

### Error al hacer terraform apply

1. Verificar credenciales AWS: `aws sts get-caller-identity`
2. Verificar que los IDs (VPC, Subnet, SG) existan y sean correctos
3. Verificar que tengas permisos suficientes en AWS

## Costos estimados

- **t2.micro** (free tier): ~$0/mes (si estás en free tier)
- **t2.small**: ~$17/mes
- **EBS 20GB gp3**: ~$2/mes

**Total aproximado**: $19-20/mes (sin free tier)

## Mejoras futuras

- [ ] Auto Scaling Group para alta disponibilidad
- [ ] Application Load Balancer
- [ ] HTTPS con certificado SSL
- [ ] CloudWatch alarms
- [ ] Backup automatizado
- [ ] CI/CD pipeline
- [ ] Multiple availability zones
